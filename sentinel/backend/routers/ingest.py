from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import shutil
import hashlib
from datetime import datetime
import uuid

from pipeline.ocr_extractor import extract_text
from pipeline.ner_extractor import IndianLawNER
from pipeline.relation_builder import deduplicate_entities, build_relations_from_cooccurrence
from pipeline.graph_builder import process_ingested_data

router = APIRouter(prefix='/api/ingest', tags=['ingestion'])

# In-memory preview cache for uploaded files awaiting approval / review
extraction_cache: Dict[str, Dict[str, Any]] = {}

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

ner_engine = IndianLawNER()

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB forensic file size limit
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.csv', '.xlsx', '.xls', '.jpg', '.jpeg', '.png', '.json', '.bmp', '.webp'}

def validate_file_payload(filename: str, contents: bytes) -> str:
    """
    Forensic security gateway: validates payload size, extension whitelist,
    and binary magic bytes to eliminate corrupt, oversized, or spoofed uploads.
    """
    if not contents:
        raise HTTPException(status_code=400, detail="Forensic Upload Rejected: Empty payload provided")
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"Forensic Upload Rejected: File exceeds 100MB limit ({len(contents)} bytes)")

    safe_filename = os.path.basename(filename)
    file_ext = os.path.splitext(safe_filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Forensic Upload Rejected: Format '{file_ext}' unauthorized. Permitted: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Magic byte header verification (flexible and robust)
    if file_ext == '.pdf' and not (contents.startswith(b"%PDF-") or b"%PDF-" in contents[:1024]):
        raise HTTPException(status_code=400, detail="Forensic Header Mismatch: Missing %PDF- signature in uploaded PDF")
    elif file_ext == '.png' and not contents.startswith(b"\x89PNG\r\n\x1a\n"):
        raise HTTPException(status_code=400, detail="Forensic Header Mismatch: Corrupt or invalid PNG signature")
    elif file_ext in ('.jpg', '.jpeg') and not contents.startswith(b"\xff\xd8\xff"):
        raise HTTPException(status_code=400, detail="Forensic Header Mismatch: Corrupt or invalid JPEG SOI marker")
    elif file_ext == '.xlsx' and not contents.startswith(b"PK\x03\x04"):
        raise HTTPException(status_code=400, detail="Forensic Header Mismatch: Corrupt or invalid XLSX archive signature")

    return file_ext

@router.post('/upload')
async def upload_file(request: Request, file: UploadFile = File(...)):
    """
    Accepts raw evidence file (PDF, CSV, Excel, Image, TXT), validates magic bytes & size,
    calculates SHA-256 cryptographic seal, adds record to blockchain audit trail,
    and runs multi-modal extraction (OCR, NER, CDR, Financial, Faces).
    """
    try:
        contents = await file.read()
        safe_filename = os.path.basename(file.filename or "evidence.txt")
        file_ext = validate_file_payload(safe_filename, contents)
        upload_id = str(uuid.uuid4())
        save_path = os.path.join(UPLOAD_DIR, f"{upload_id}_{safe_filename}")

        # Compute SHA-256 cryptographic seal
        sha256_hash = hashlib.sha256(contents).hexdigest()

        with open(save_path, "wb") as f:
            f.write(contents)

        # Register in blockchain audit trail if service available
        blockchain = getattr(request.app.state, 'blockchain', None)
        if blockchain:
            blockchain.add_block(
                file_hash=sha256_hash,
                file_name=file.filename,
                file_type=file_ext,
                uploaded_by="Investigator (Badge #4092)"
            )

        # Extract text via OCR & document parser pipeline
        extracted_text = extract_text(save_path)

        # 1. Run Indian NER pipeline on textual content
        entities = ner_engine.extract_entities(extracted_text)
        relations = ner_engine.extract_relations(extracted_text, entities)

        # 2. Specialized tabular extraction for CSV & Excel (CDR & Financials)
        if file_ext in ('.csv', '.xlsx', '.xls'):
            try:
                from pipeline.cdr_parser import CDRParser
                from pipeline.financial_parser import FinancialParser
                
                # Check for CDR
                cdr_parser = CDRParser()
                cdrs = []
                if file_ext == '.csv':
                    cdrs = cdr_parser.parse_csv(save_path)
                elif file_ext in ('.xlsx', '.xls'):
                    import pandas as pd
                    excel_df = pd.read_excel(save_path)
                    csv_temp = os.path.join(UPLOAD_DIR, f"temp_{upload_id}.csv")
                    excel_df.to_csv(csv_temp, index=False)
                    cdrs = cdr_parser.parse_csv(csv_temp)
                    if os.path.exists(csv_temp):
                        os.remove(csv_temp)

                for c in cdrs:
                    caller = c.get('caller')
                    receiver = c.get('receiver')
                    if caller:
                        entities.append({'text': caller, 'entity_type': 'PHONE', 'confidence': 0.98, 'start': 0, 'end': len(caller)})
                    if receiver:
                        entities.append({'text': receiver, 'entity_type': 'PHONE', 'confidence': 0.98, 'start': 0, 'end': len(receiver)})
                    if caller and receiver:
                        relations.append({'source': caller, 'target': receiver, 'relation_type': 'CALLED', 'confidence': 0.95})
                    if c.get('tower_id'):
                        entities.append({'text': c['tower_id'], 'entity_type': 'LOCATION', 'confidence': 0.90, 'start': 0, 'end': len(c['tower_id'])})

                # Check for Financial Transactions
                fin_parser = FinancialParser()
                txs = []
                if file_ext == '.csv':
                    txs = fin_parser.parse_csv(save_path)
                elif file_ext in ('.xlsx', '.xls'):
                    import pandas as pd
                    excel_df = pd.read_excel(save_path)
                    csv_temp = os.path.join(UPLOAD_DIR, f"temp_fin_{upload_id}.csv")
                    excel_df.to_csv(csv_temp, index=False)
                    txs = fin_parser.parse_csv(csv_temp)
                    if os.path.exists(csv_temp):
                        os.remove(csv_temp)

                for t in txs:
                    s_acc = t.get('sender_account')
                    r_acc = t.get('receiver_account')
                    amt = t.get('amount')
                    if s_acc:
                        entities.append({'text': f"ACC-{s_acc}", 'entity_type': 'BANK_ACCOUNT', 'confidence': 0.98, 'start': 0, 'end': len(s_acc)})
                    if r_acc:
                        entities.append({'text': f"ACC-{r_acc}", 'entity_type': 'BANK_ACCOUNT', 'confidence': 0.98, 'start': 0, 'end': len(r_acc)})
                    if s_acc and r_acc:
                        relations.append({'source': f"ACC-{s_acc}", 'target': f"ACC-{r_acc}", 'relation_type': 'TRANSFERRED_MONEY_TO', 'confidence': 0.98})
                    if amt:
                        entities.append({'text': f"₹{amt:,.2f}", 'entity_type': 'AMOUNT', 'confidence': 0.95, 'start': 0, 'end': len(str(amt))})
            except Exception as tab_err:
                print(f"Tabular extraction notice: {tab_err}")

        # 3. Specialized Image / Photo Extraction (Face Detection & Biometrics)
        if file_ext in ('.jpg', '.jpeg', '.png', '.bmp', '.webp'):
            try:
                from pipeline.face_processor import FaceProcessor
                face_proc = FaceProcessor()
                detected_faces = face_proc.detect_faces(save_path)
                for idx, bbox in enumerate(detected_faces):
                    face_label = f"Suspect Visual #{idx+1} ({safe_filename})"
                    entities.append({
                        'text': face_label,
                        'entity_type': 'PERSON',
                        'confidence': 0.95,
                        'start': 0,
                        'end': len(face_label),
                        'metadata': {'bbox': bbox, 'source_file': safe_filename}
                    })
            except Exception as face_err:
                print(f"Image face extraction notice: {face_err}")

        # Entity deduplication against existing graph
        graph_store = getattr(request.app.state, 'graph_store', None)
        existing_nodes = []
        if graph_store and graph_store.graph:
            existing_nodes = [dict(d, id=n) for n, d in graph_store.graph.nodes(data=True)]

        deduped_entities = deduplicate_entities(entities, existing_nodes)

        # Categorize entities cleanly for structured UI and analytical review
        categorized: Dict[str, List[Dict[str, Any]]] = {
            "PERSONS": [e for e in deduped_entities if e.get("entity_type") in ("PERSON", "AADHAAR")],
            "PHONES": [e for e in deduped_entities if e.get("entity_type") == "PHONE"],
            "BANK_ACCOUNTS": [e for e in deduped_entities if e.get("entity_type") in ("BANK_ACCOUNT", "UPI_ID", "CRYPTO_WALLET")],
            "VEHICLES": [e for e in deduped_entities if e.get("entity_type") == "VEHICLE_REG"],
            "LOCATIONS": [e for e in deduped_entities if e.get("entity_type") in ("LOCATION", "TOWER")],
            "INCIDENTS_SECTIONS": [e for e in deduped_entities if e.get("entity_type") in ("IPC_SECTION", "FIR_NO")],
            "ORGANIZATIONS": [e for e in deduped_entities if e.get("entity_type") == "ORGANIZATION"],
            "FINANCIAL": [e for e in deduped_entities if e.get("entity_type") == "AMOUNT"],
            "OTHER": [e for e in deduped_entities if e.get("entity_type") not in (
                "PERSON", "AADHAAR", "PHONE", "BANK_ACCOUNT", "UPI_ID", "CRYPTO_WALLET",
                "VEHICLE_REG", "LOCATION", "TOWER", "IPC_SECTION", "FIR_NO", "ORGANIZATION", "AMOUNT"
            )]
        }
        summary_counts = {k: len(v) for k, v in categorized.items() if len(v) > 0}

        # Run Cross-Case Intelligence Linker (Auto-Feature 2)
        from backend.pipeline.cross_case_linker import CrossCaseLinker
        cross_linker = CrossCaseLinker(graph_store)
        cross_case_alerts = cross_linker.scan_for_cross_case_links(deduped_entities)

        # Log in SQLite database with real entity counts
        db = getattr(request.app.state, 'db', None)
        if db:
            db.add_upload({
                "id": upload_id,
                "file_name": file.filename,
                "file_type": file_ext,
                "file_size": len(contents),
                "sha256_hash": sha256_hash,
                "upload_timestamp": datetime.now().isoformat(),
                "status": "SEALED",
                "extracted_entities_count": len(deduped_entities)
            })

        # Cache extraction result for preview
        extraction_cache[upload_id] = {
            'upload_id': upload_id,
            'file_name': file.filename,
            'file_path': save_path,
            'sha256_hash': sha256_hash,
            'file_size': len(contents),
            'extracted_text': extracted_text[:1500] + ('...' if len(extracted_text) > 1500 else ''),
            'entities': deduped_entities,
            'relations': relations,
            'categorized': categorized,
            'cross_case_links': cross_case_alerts,
            'timestamp': datetime.now().isoformat(),
            'status': 'EXTRACTED'
        }

        return {
            'upload_id': upload_id,
            'file_name': file.filename,
            'sha256_hash': sha256_hash,
            'file_size': len(contents),
            'file_type': file_ext,
            'blockchain_sealed': True,
            'entities_count': len(deduped_entities),
            'relations_count': len(relations),
            'summary': summary_counts,
            'categorized_entities': categorized,
            'cross_case_links': cross_case_alerts,
            'entities_preview': deduped_entities[:30],
            'extracted_text_preview': extracted_text[:1500] + ('...' if len(extracted_text) > 1500 else '')
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process evidence upload: {str(e)}")

@router.post('/batch')
async def batch_upload_files(request: Request, files: List[UploadFile] = File(...)):
    """Auto-Feature 1: Batch Upload. Process multiple files simultaneously."""
    results = []
    for f in files:
        try:
            r = await upload_file(request, f)
            results.append(r)
        except Exception as ex:
            results.append({"file_name": f.filename, "status": "ERROR", "error": str(ex)})
    return {"total_files": len(files), "processed": results}


@router.post('/process/{upload_id}')
async def process_and_add_to_graph(upload_id: str, request: Request):
    """Inserts extracted and verified entities/relations into the live intelligence graph."""
    if upload_id not in extraction_cache:
        raise HTTPException(status_code=404, detail="Upload ID not found or already processed.")

    cached = extraction_cache[upload_id]
    graph_store = getattr(request.app.state, 'graph_store', None)
    if not graph_store or graph_store.graph is None:
        raise HTTPException(status_code=500, detail="Graph store uninitialized.")

    # Insert into live graph
    summary = process_ingested_data(graph_store.graph, cached['entities'], cached['relations'])
    cached['status'] = 'COMMITTED_TO_GRAPH'

    return {
        'status': 'SUCCESS',
        'upload_id': upload_id,
        'summary': summary
    }

@router.get('/history')
async def get_upload_history(request: Request):
    """Returns evidentiary upload history with cryptographic verification status."""
    db = getattr(request.app.state, 'db', None)
    if db:
        history = db.get_uploads()
        return {'history': history}
        
    # In-memory fallback
    items = list(extraction_cache.values())
    return {'history': items}

@router.get('/preview/{upload_id}')
async def get_extraction_preview(upload_id: str):
    """Retrieves extracted entities and text preview before graph insertion."""
    if upload_id not in extraction_cache:
        raise HTTPException(status_code=404, detail="Upload ID not found.")
    return extraction_cache[upload_id]

class IntelReportRequest(BaseModel):
    title: Optional[str] = "Field Surveillance Intelligence Report"
    text: str
    report_id: Optional[str] = None
    author: Optional[str] = "Special Cell Field Officer"
    source_type: Optional[str] = "HUMINT_SURVEILLANCE"
    auto_commit: Optional[bool] = True

@router.post('/intel-report')
async def ingest_unstructured_intel_report(req: IntelReportRequest, request: Request):
    """
    Ingests unstructured field surveillance and intelligence report text.
    Extracts entities, contacts, and vehicles with exact character and sentence PROVENANCE linking,
    commits document hash to the immutable blockchain audit chain, and integrates into the knowledge graph.
    """
    from pipeline.intel_extractor import IntelReportExtractor
    
    report_id = req.report_id or f"INTEL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    title = req.title or "Field Surveillance Intelligence Report"
    raw_bytes = req.text.encode('utf-8')
    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()

    # 1. Register in blockchain audit trail
    blockchain = getattr(request.app.state, 'blockchain', None)
    if blockchain:
        blockchain.add_block(
            file_hash=sha256_hash,
            file_name=f"{report_id}.txt",
            file_type="INTEL_TEXT",
            uploaded_by=f"{req.author} ({req.source_type})"
        )

    # 2. Extract with strict sentence & char provenance
    extractor = IntelReportExtractor()
    intel_res = extractor.process_intel_text(
        text=req.text,
        doc_id=report_id,
        doc_title=title,
        author=req.author or "Special Cell Field Officer",
        source_type=req.source_type or "HUMINT_SURVEILLANCE"
    )

    # 3. Add to live graph if requested
    graph_summary = {'nodes_added': 0, 'edges_added': 0}
    graph_store = getattr(request.app.state, 'graph_store', None)
    if req.auto_commit and graph_store and graph_store.graph:
        graph_summary = extractor.ingest_intel_into_graph(graph_store.graph, intel_res)

    # 4. Record in SQLite db
    db = getattr(request.app.state, 'db', None)
    if db:
        db.add_upload({
            "id": report_id,
            "file_name": f"{title}.txt",
            "file_type": "INTEL_REPORT",
            "file_size": len(raw_bytes),
            "sha256_hash": sha256_hash,
            "upload_timestamp": datetime.now().isoformat(),
            "status": "PROCESSED_WITH_PROVENANCE",
            "extracted_entities_count": len(intel_res['entities'])
        })

    return {
        'status': 'SUCCESS',
        'report_id': report_id,
        'doc_title': title,
        'sha256_hash': sha256_hash,
        'entities_extracted': len(intel_res['entities']),
        'entities': intel_res['entities'],
        'relations_extracted': len(intel_res['relations']),
        'relations': intel_res['relations'],
        'provenance_count': len(intel_res['entities']),
        'total_sentences': intel_res['total_sentences'],
        'graph_summary': graph_summary
    }

from fastapi.responses import FileResponse
from backend.config import TEST_DOCS_DIR
from backend.services.generate_test_pdfs import generate_sample_fir_pdf, generate_sample_intel_report_pdf

@router.get('/sample-files')
async def list_sample_files():
    """Lists available court-standard test PDFs generated for testing."""
    os.makedirs(TEST_DOCS_DIR, exist_ok=True)
    p1 = os.path.join(TEST_DOCS_DIR, "SAMPLE_POLICE_FIR_CR2026_0418.pdf")
    p2 = os.path.join(TEST_DOCS_DIR, "SAMPLE_INTELLIGENCE_SURVEILLANCE_REPORT.pdf")
    if not os.path.exists(p1):
        generate_sample_fir_pdf(p1)
    if not os.path.exists(p2):
        generate_sample_intel_report_pdf(p2)

    return {
        "sample_files": [
            {
                "id": "sample-fir",
                "filename": "SAMPLE_POLICE_FIR_CR2026_0418.pdf",
                "title": "Jharkhand Police FIR (Kotwali PS - Extortion & Arms Act)",
                "size_bytes": os.path.getsize(p1) if os.path.exists(p1) else 0,
                "download_url": "/api/ingest/sample-pdf/SAMPLE_POLICE_FIR_CR2026_0418.pdf",
                "description": "Realistic First Information Report with suspects Vikram Sinha, Deepak Tiwari, Suresh Patel, vehicles, phones, and hawala accounts."
            },
            {
                "id": "sample-intel",
                "filename": "SAMPLE_INTELLIGENCE_SURVEILLANCE_REPORT.pdf",
                "title": "Special Task Force Intelligence Surveillance Brief",
                "size_bytes": os.path.getsize(p2) if os.path.exists(p2) else 0,
                "download_url": "/api/ingest/sample-pdf/SAMPLE_INTELLIGENCE_SURVEILLANCE_REPORT.pdf",
                "description": "SIGINT and cell tower telemetry report covering burner IMEI reuse, nocturnal co-locations, and structured cash loops."
            }
        ]
    }

@router.get('/sample-pdf/{filename}')
async def download_sample_pdf(filename: str):
    """Serves the test PDF file for download or local testing."""
    safe_name = os.path.basename(filename)
    file_path = os.path.join(TEST_DOCS_DIR, safe_name)
    if not os.path.exists(file_path):
        if "fir" in safe_name.lower():
            generate_sample_fir_pdf(file_path)
        else:
            generate_sample_intel_report_pdf(file_path)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample PDF not found.")

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=safe_name,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'}
    )

@router.post('/auto-test-sample')
async def auto_ingest_sample_test_pdf(request: Request, sample_type: str = "fir"):
    """
    One-click automated test:
    Ingests the sample FIR PDF directly into the live graph,
    computes SHA-256 seal, logs to blockchain, runs OCR + NER,
    and commits extracted entities and relations to the graph.
    """
    os.makedirs(TEST_DOCS_DIR, exist_ok=True)
    if sample_type.lower() == "intel":
        file_path = os.path.join(TEST_DOCS_DIR, "SAMPLE_INTELLIGENCE_SURVEILLANCE_REPORT.pdf")
        if not os.path.exists(file_path):
            generate_sample_intel_report_pdf(file_path)
    else:
        file_path = os.path.join(TEST_DOCS_DIR, "SAMPLE_POLICE_FIR_CR2026_0418.pdf")
        if not os.path.exists(file_path):
            generate_sample_fir_pdf(file_path)

    with open(file_path, "rb") as f:
        contents = f.read()

    filename = os.path.basename(file_path)
    sha256_hash = hashlib.sha256(contents).hexdigest()
    upload_id = str(uuid.uuid4())

    # Save to uploads
    save_path = os.path.join(UPLOAD_DIR, f"{upload_id}_{filename}")
    with open(save_path, "wb") as f:
        f.write(contents)

    # Blockchain registration
    blockchain = getattr(request.app.state, 'blockchain', None)
    if blockchain:
        blockchain.add_block(
            file_hash=sha256_hash,
            file_name=filename,
            file_type=".pdf",
            uploaded_by="Investigator (Auto-Test)"
        )

    # Extract text with OCR + NER
    extracted_text = extract_text(save_path)
    entities = ner_engine.extract_entities(extracted_text)
    relations = ner_engine.extract_relations(extracted_text, entities)

    # Commit to graph
    graph_store = getattr(request.app.state, 'graph_store', None)
    summary = {}
    if graph_store and graph_store.graph is not None:
        summary = process_ingested_data(graph_store.graph, entities, relations)

    # Log in SQLite db
    db = getattr(request.app.state, 'db', None)
    if db:
        db.add_upload({
            "id": upload_id,
            "file_name": filename,
            "file_type": ".pdf",
            "file_size": len(contents),
            "sha256_hash": sha256_hash,
            "upload_timestamp": datetime.now().isoformat(),
            "status": "COMMITTED_TO_GRAPH",
            "extracted_entities_count": len(entities)
        })

    return {
        "status": "SUCCESS",
        "upload_id": upload_id,
        "file_name": filename,
        "sha256_hash": sha256_hash,
        "entities_extracted_count": len(entities),
        "entities": entities[:20],
        "relations_count": len(relations),
        "relations": relations[:15],
        "graph_summary": summary,
        "message": f"Successfully ingested {filename} into the criminal network graph."
    }

@router.delete("/history/{upload_id}")
async def delete_upload_history_item(upload_id: str, request: Request):
    db = getattr(request.app.state, 'db', None)
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    success = db.delete_upload(upload_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Upload record {upload_id} not found")
    return {"status": "ok", "deleted_upload_id": upload_id}

@router.post("/clear-history")
async def clear_upload_history(request: Request):
    db = getattr(request.app.state, 'db', None)
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    db.clear_uploads()
    return {"status": "ok", "message": "All ingestion history records cleared"}
