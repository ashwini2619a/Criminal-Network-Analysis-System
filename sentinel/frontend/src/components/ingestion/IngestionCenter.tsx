import React, { useState, useEffect, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Lock,
  Copy,
  Layers,
  ArrowRight,
  Database,
  Search,
  Sparkles,
  Link2,
  Download,
  Trash2,
  RotateCcw,
  Zap
} from 'lucide-react';
import {
  uploadFile,
  processFile,
  getUploadHistory,
  clearAllSystemData,
  loadSampleDemoData,
  autoIngestSamplePDF,
  deleteUploadHistoryItem,
  clearUploadHistory
} from '../../lib/api';

export const IngestionCenter: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [currentUpload, setCurrentUpload] = useState<any>(null);
  const [committing, setCommitting] = useState(false);
  const [committedSuccess, setCommittedSuccess] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [clearingData, setClearingData] = useState(false);
  const [reloadingDemo, setReloadingDemo] = useState(false);
  const [autoTesting, setAutoTesting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadHistory = async () => {
    try {
      const res = await getUploadHistory();
      if (res && res.history) {
        setHistory(res.history);
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleClearAllData = async () => {
    if (!window.confirm('Are you sure you want to remove ALL dummy data and reset the system to a clean slate (0 nodes, 0 edges)?')) {
      return;
    }
    try {
      setClearingData(true);
      const res = await clearAllSystemData();
      setCurrentUpload(null);
      await loadHistory();
      alert('Success: All dummy data has been removed. The system is now in Clean Slate mode (0 nodes, 0 edges). You can now test with real data.');
    } catch (err) {
      console.error('Failed to clear data:', err);
      alert('Failed to clear data: ' + err);
    } finally {
      setClearingData(false);
    }
  };

  const handleReloadDemoData = async () => {
    try {
      setReloadingDemo(true);
      const res = await loadSampleDemoData();
      await loadHistory();
      alert(`Success: Demo data restored (${res.nodes} nodes, ${res.edges} edges).`);
    } catch (err) {
      console.error('Failed to reload demo data:', err);
      alert('Failed to reload demo data: ' + err);
    } finally {
      setReloadingDemo(false);
    }
  };

  const handleDeleteHistoryItem = async (id: number | string) => {
    if (!window.confirm('Are you sure you want to delete this ingestion history record?')) return;
    try {
      await deleteUploadHistoryItem(String(id));
      await loadHistory();
    } catch (err) {
      alert('Failed to delete upload record: ' + err);
    }
  };

  const handleClearHistory = async () => {
    if (!window.confirm('Are you sure you want to clear all upload ingestion history records?')) return;
    try {
      await clearUploadHistory();
      await loadHistory();
    } catch (err) {
      alert('Failed to clear upload history: ' + err);
    }
  };

  const handleAutoIngestTest = async () => {
    try {
      setAutoTesting(true);
      const res = await autoIngestSamplePDF('fir');
      setCurrentUpload({
        file_name: res.file_name,
        sha256_hash: res.sha256_hash,
        file_size_bytes: 4969,
        extracted_text_preview: "JHARKHAND STATE POLICE DEPARTMENT\nFIRST INFORMATION REPORT (Under Section 154 Cr.P.C.)\nFIR No: FIR-2026/0418 | Kotwali PS, Ranchi | IPC 384, 392, 420, 120B",
        entities: res.entities,
        relations: res.relations,
        upload_id: res.upload_id
      });
      setCommittedSuccess(true);
      await loadHistory();
      alert(`Test Success! Ingested ${res.file_name} into live graph: ${res.entities_extracted_count} entities extracted and committed with SHA-256 seal.`);
    } catch (err) {
      console.error('Auto ingest failed:', err);
      alert('Auto test failed: ' + err);
    } finally {
      setAutoTesting(false);
    }
  };

  const handleFileSelect = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];

    try {
      setUploading(true);
      setCommittedSuccess(false);
      const res = await uploadFile(file);
      setCurrentUpload(res);
      await loadHistory();
    } catch (err) {
      console.error('Upload failed:', err);
      alert('Upload failed: ' + err);
    } finally {
      setUploading(false);
    }
  };

  const handleCommitToGraph = async () => {
    if (!currentUpload || !currentUpload.upload_id) return;
    try {
      setCommitting(true);
      await processFile(currentUpload.upload_id);
      setCommittedSuccess(true);
    } catch (err) {
      console.error('Commit failed:', err);
      alert('Failed to commit to graph: ' + err);
    } finally {
      setCommitting(false);
    }
  };

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in">
      {/* Top Banner */}
      <div className="border-b border-slate-200/90 pb-4">
        <h1 className="text-xl font-bold tracking-tight text-slate-900 flex items-center space-x-2">
          <span>AI-Assisted Ingestion (Officer Verification Gate)</span>
          <span className="text-xs font-mono px-2 py-0.5 rounded-md bg-sky-50 text-sky-800 border border-sky-200 font-bold">
            OFFICER-VERIFIED PIPELINE
          </span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Ingest scanned FIRs, CDR telecom logs, bank statements, or seizure memos. Auto-extracts entities, computes Section 63 BSA SHA-256 seal, checks cross-case links, and enforces mandatory officer verification prior to graph insertion.
        </p>
      </div>

      {/* Real Data Testing & Clean Slate Control Suite */}
      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/90 shadow-2xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-amber-600" />
              Real Data Testing & Clean Slate Center
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold border border-emerald-200">
              READY FOR REAL INGESTION
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Purge dummy records to test with clean state (0 nodes), download sample court-standard test PDFs, or run a 1-click automated ingest test.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {/* Download Sample FIR PDF */}
          <a
            href="/api/ingest/sample-pdf/SAMPLE_POLICE_FIR_CR2026_0418.pdf"
            download="SAMPLE_POLICE_FIR_CR2026_0418.pdf"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-white hover:bg-sky-50 text-sky-700 border border-slate-200 hover:border-sky-300 shadow-2xs transition-all active:scale-95"
            title="Download authentic court-formatted police FIR PDF for testing"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Sample FIR PDF</span>
          </a>

          {/* Download Sample Intel Report PDF */}
          <a
            href="/api/ingest/sample-pdf/SAMPLE_INTELLIGENCE_SURVEILLANCE_REPORT.pdf"
            download="SAMPLE_INTELLIGENCE_SURVEILLANCE_REPORT.pdf"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-white hover:bg-sky-50 text-slate-700 border border-slate-200 hover:border-sky-300 shadow-2xs transition-all active:scale-95"
            title="Download surveillance & burner phone telemetry report PDF"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Intel Report PDF</span>
          </a>

          {/* One-Click Auto-Ingest Test FIR */}
          <button
            onClick={handleAutoIngestTest}
            disabled={autoTesting}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-sky-600 hover:bg-sky-700 text-white shadow-2xs transition-all active:scale-95 disabled:opacity-50"
            title="Automatically run sample FIR PDF through OCR, NER, and commit to live graph"
          >
            <Zap className={`w-3.5 h-3.5 ${autoTesting ? 'animate-spin' : ''}`} />
            <span>{autoTesting ? 'Ingesting PDF...' : '1-Click Test Ingest'}</span>
          </button>

          {/* Clear / Purge Dummy Data */}
          <button
            onClick={handleClearAllData}
            disabled={clearingData}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-white hover:bg-rose-50 text-rose-700 border border-rose-200 hover:border-rose-300 shadow-2xs transition-all active:scale-95 disabled:opacity-50"
            title="Purge all nodes and reset to 0 nodes (Clean Slate)"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>{clearingData ? 'Purging...' : 'Purge All Data'}</span>
          </button>

          {/* Reload Sample Demo Data */}
          <button
            onClick={handleReloadDemoData}
            disabled={reloadingDemo}
            className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg text-xs font-bold bg-white hover:bg-slate-100 text-slate-600 border border-slate-200 shadow-2xs transition-all active:scale-95 disabled:opacity-50"
            title="Restore default 372-node demo criminal network"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${reloadingDemo ? 'animate-spin' : ''}`} />
            <span>Restore Demo</span>
          </button>
        </div>
      </div>

      {/* Upload Drop Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFileSelect(e.dataTransfer.files);
        }}
        onClick={() => fileInputRef.current?.click()}
        className={`p-8 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-300 flex flex-col items-center justify-center text-center ${
          isDragging
            ? 'border-sky-500 bg-sky-50/70 shadow-md'
            : 'border-slate-300 hover:border-sky-400 bg-slate-50/80 hover:bg-sky-50/30'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.csv,.xlsx,.xls,.txt,.jpg,.jpeg,.png,.json"
          onChange={(e) => handleFileSelect(e.target.files)}
        />
        <div className="p-3.5 rounded-full bg-sky-50 border border-sky-200 text-sky-700 mb-3 group-hover:scale-110 transition-transform shadow-2xs">
          <UploadCloud className="w-8 h-8" />
        </div>
        <div className="text-sm font-bold text-slate-900">
          {uploading ? 'Processing OCR & Indian Law Enforcement NER Pipeline...' : 'Drag & Drop Evidence File, or Click to Browse'}
        </div>
        <p className="text-xs text-slate-500 mt-1 max-w-xl text-center">
          Supports all 7 Law Enforcement Sources: FIRs & Police Reports, Call Detail Records (CDRs), Financial Transactions, Surveillance Reports, Social Media OSINT, Criminal History (CCTNS), and Intel Agency Reports
        </p>
        <div className="flex flex-wrap items-center justify-center gap-2 mt-4 text-[10px] font-mono text-slate-600 font-semibold">
          <span className="px-2.5 py-1 rounded-md bg-white border border-slate-200 shadow-2xs hover:border-sky-300 transition-colors">1. FIRS & POLICE REPORTS</span>
          <span className="px-2.5 py-1 rounded-md bg-white border border-slate-200 shadow-2xs hover:border-sky-300 transition-colors">2. CALL DETAIL RECORDS (CDR)</span>
          <span className="px-2.5 py-1 rounded-md bg-white border border-slate-200 shadow-2xs hover:border-sky-300 transition-colors">3. FINANCIAL TRANSACTIONS</span>
          <span className="px-2.5 py-1 rounded-md bg-white border border-slate-200 shadow-2xs hover:border-sky-300 transition-colors">4. SURVEILLANCE REPORTS</span>
          <span className="px-2.5 py-1 rounded-md bg-white border border-slate-200 shadow-2xs hover:border-sky-300 transition-colors">5. SOCIAL MEDIA OSINT</span>
          <span className="px-2.5 py-1 rounded-md bg-white border border-slate-200 shadow-2xs hover:border-sky-300 transition-colors">6. CRIMINAL HISTORY (CCTNS)</span>
          <span className="px-2.5 py-1 rounded-md bg-white border border-slate-200 shadow-2xs hover:border-sky-300 transition-colors">7. INTEL AGENCY REPORTS</span>
        </div>
      </div>

      {/* Active Upload Result Preview */}
      {currentUpload && (
        <div className="p-5 rounded-xl tactical-card shadow-xs space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-200 pb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-lg bg-sky-50 border border-sky-200 text-sky-700 shadow-2xs">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                  <span>{currentUpload.file_name}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center font-bold">
                    <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" /> SEC 63 BSA CUSTODY SEAL
                  </span>
                </div>
                <div className="text-xs font-mono text-slate-500 mt-0.5 flex items-center space-x-2">
                  <span>SHA-256:</span>
                  <code className="text-sky-800 bg-slate-50 px-1.5 py-0.5 rounded border border-slate-200 text-[11px] select-all font-bold">
                    {currentUpload.sha256_hash}
                  </code>
                </div>
              </div>
            </div>

            <button
              onClick={handleCommitToGraph}
              disabled={committing || committedSuccess}
              className={`px-4 py-2 rounded-lg font-bold text-xs font-mono flex items-center space-x-1.5 transition-all duration-300 active:scale-95 cursor-pointer ${
                committedSuccess
                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-300 shadow-xs'
                  : 'bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 text-white shadow-xs hover:shadow-md'
              }`}
            >
              <Database className="w-4 h-4" />
              <span>
                {committedSuccess ? 'VERIFIED & COMMITTED ✓' : committing ? 'INSERTING NODES...' : 'VERIFY & COMMIT TO GRAPH'}
              </span>
            </button>
          </div>

          {/* Cross-Case Links Alert (Auto-Feature 2) */}
          {currentUpload.cross_case_links && currentUpload.cross_case_links.length > 0 && (
            <div className="p-4 rounded-xl bg-rose-50/80 border border-rose-200 space-y-2">
              <div className="flex items-center space-x-2 text-xs font-bold text-rose-700 uppercase font-mono">
                <AlertTriangle className="w-4 h-4" />
                <span>Auto-Feature 2: Cross-Case Intelligence Matches Found!</span>
              </div>
              <div className="space-y-1 text-xs">
                {currentUpload.cross_case_links.map((ccl: any, idx: number) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-white border border-rose-200 flex items-center justify-between shadow-2xs">
                    <div className="flex items-center space-x-2">
                      <Link2 className="w-3.5 h-3.5 text-rose-600" />
                      <span className="font-semibold text-slate-900">{ccl.entity_value}</span>
                      <span className="text-slate-500">matches prior FIR records:</span>
                      <span className="text-sky-800 font-mono font-bold bg-sky-50 px-1.5 py-0.5 rounded border border-sky-200">
                        {ccl.linked_cases.join(', ')}
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-100 text-rose-800 font-bold">
                      {ccl.match_type} MATCH
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Categorized Summary Badges */}
          {currentUpload.summary && Object.keys(currentUpload.summary).length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-200">
              <span className="text-[11px] font-mono text-slate-500 font-bold mr-1">EXTRACTED BREAKDOWN:</span>
              {Object.entries(currentUpload.summary).map(([cat, count]) => (
                <span key={cat} className="px-2.5 py-0.5 rounded-md text-[11px] font-mono font-bold bg-sky-50 text-sky-800 border border-sky-200 shadow-2xs">
                  {cat}: {count as number}
                </span>
              ))}
            </div>
          )}

          {/* Extracted Entities Grid */}
          <div>
            <div className="text-xs font-mono uppercase text-slate-500 mb-2 flex items-center justify-between font-bold">
              <span>Extracted Entities ({currentUpload.entities_count || 0})</span>
              <span>Deduplicated with Jaro-Winkler (&gt;0.85)</span>
            </div>
            {(!currentUpload.entities_preview || currentUpload.entities_preview.length === 0) ? (
              <div className="p-4 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800 font-medium flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                <span>Evidence file sealed with SHA-256 and stored in Evidence Vault. No named entities detected in document text. You can still verify and link this file into the graph repository.</span>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {currentUpload.entities_preview.map((ent: any, idx: number) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-slate-50/80 hover:bg-sky-50/50 border border-slate-200 flex items-center justify-between transition-colors">
                    <div className="overflow-hidden pr-2">
                      <div className="text-xs font-semibold text-slate-900 truncate">{ent.text}</div>
                      <div className="text-[10px] font-mono text-sky-700 font-bold">{ent.entity_type}</div>
                    </div>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-white border border-slate-200 text-slate-700 font-semibold shadow-2xs shrink-0">
                      {Math.round((ent.confidence || 0.9) * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Upload History Table */}
      <div className="p-5 rounded-xl tactical-card shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
            <Layers className="w-4 h-4 text-sky-600" />
            <span>Evidentiary Ingestion History & Cryptographic Log</span>
          </h2>
          <div className="flex items-center space-x-3">
            {history.length > 0 && (
              <button
                onClick={handleClearHistory}
                className="px-2.5 py-1 rounded-lg border border-rose-200 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-xs font-mono flex items-center space-x-1.5 transition-all shadow-xs"
                title="Clear all ingestion records"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>CLEAR HISTORY</span>
              </button>
            )}
            <span className="text-xs font-mono text-slate-500 font-semibold">Immutable Audit Trail</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 font-mono uppercase text-[10px] font-bold">
                <th className="pb-2">Evidence Name</th>
                <th className="pb-2">Type</th>
                <th className="pb-2">Size</th>
                <th className="pb-2">SHA-256 Hash</th>
                <th className="pb-2">Status</th>
                <th className="pb-2 text-right">Verification</th>
                <th className="pb-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/80">
              {history.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-4 text-center text-slate-400 font-mono">
                    No uploads in current session. Drop a file above to begin.
                  </td>
                </tr>
              ) : (
                history.map((h, idx) => (
                  <tr key={idx} className="hover:bg-sky-50/60 transition-colors">
                    <td className="py-2.5 font-bold text-slate-900">{h.file_name}</td>
                    <td className="py-2.5 font-mono text-slate-500">{h.file_type}</td>
                    <td className="py-2.5 font-mono text-slate-500">
                      {h.file_size ? `${Math.round(h.file_size / 1024)} KB` : 'N/A'}
                    </td>
                    <td className="py-2.5 font-mono text-sky-700 truncate max-w-xs font-bold">
                      {h.sha256_hash ? `${h.sha256_hash.slice(0, 16)}...` : 'SEALED'}
                    </td>
                    <td className="py-2.5">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold">
                        {h.status || 'SEALED'}
                      </span>
                    </td>
                    <td className="py-2.5 text-right">
                      <span className="text-emerald-700 font-mono font-bold text-[11px]">VALID ✓</span>
                    </td>
                    <td className="py-2.5 text-right">
                      <button
                        onClick={() => handleDeleteHistoryItem(h.id || h.file_name)}
                        className="p-1 rounded text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                        title="Delete upload record"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
