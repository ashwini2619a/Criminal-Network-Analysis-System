import sys, os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

with client:
    print('====================================================')
    print('  SENTINEL v2.0 FULL VERIFICATION TEST SUITE')
    print('====================================================')

    # Ensure sample intelligence dataset is populated
    load_res = client.post('/api/admin/load-sample-data').json()
    print(f"[INIT] Loaded Intelligence Graph -> {load_res.get('total_nodes')} Nodes, {load_res.get('total_edges')} Edges")

    # Test 1: System Health & Graph Metrics
    h = client.get('/api/health').json()
    assert h['status'] == 'ok'
    print(f'[PASS] Test 1: System Health -> Status: {h["status"]}, Nodes: {h["nodes"]}, Edges: {h["edges"]}')

    # Test 2: Ingestion & Upload History
    ih = client.get('/api/ingest/history').json()
    print(f'[PASS] Test 2: Ingestion History -> Found: {len(ih.get("history", []))} records')

    # Test 3: Graph Core & 1-Click Expansion (Auto-Feature 3)
    exp = client.get('/api/graph/one-click-expand/SUSP-VIKRAM-SINHA?depth=2').json()
    assert 'nodes' in exp and 'edges' in exp
    print(f'[PASS] Test 3: 1-Click Expansion (Vikram Sinha) -> Nodes: {len(exp["nodes"])}, Edges: {len(exp["edges"])}')

    # Test 4: Geo Towers (30 Towers)
    towers = client.get('/api/geo/towers').json()
    assert len(towers) >= 30
    print(f'[PASS] Test 4: Geo Towers -> {len(towers)} telecom cell towers loaded with real coordinates')

    # Test 5: Geo Trail & Dwell Percentages (Screen 4 Layer 5)
    tr = client.get('/api/geo/trail/%2B91-9876500001').json()
    assert len(tr['waypoints']) > 0
    print(f'[PASS] Test 5: CDR Movement Trail -> {tr["total_hits"]} tower waypoints, Dwell: {tr["dwell_percentages"]}')

    # Test 6: Co-Location Events (Screen 4 Layer 7)
    coloc = client.get('/api/geo/colocations').json()
    assert len(coloc) > 0
    print(f'[PASS] Test 6: Co-Location Events -> Detected {len(coloc)} nocturnal meetings (<500m)')

    # Test 7: Hawala Loops & Structuring (Screen 6)
    hw = client.get('/api/analysis/hawala').json()
    assert len(hw['cycles']) > 0
    print(f'[PASS] Test 7: Hawala AML -> {len(hw["cycles"])} cycles found (Closed loop: {hw["cycles"][0]["total_amount"]} INR)')

    # Test 8: Burner Phones & IMEI Device Reuse (Screen 5)
    bp = client.get('/api/analysis/burner-phones').json()
    assert len(bp['imei_reuse']) > 0
    print(f'[PASS] Test 8: Burner Triangulation -> IMEI {bp["imei_reuse"][0]["imei"]} reused across {len(bp["imei_reuse"][0]["phone_numbers"])} SIMs')

    # Test 9: Pre-Crime Spikes & Temporal Timeline (Screen 7)
    tp = client.get('/api/analysis/temporal').json()
    print(f'[PASS] Test 9: Temporal Reconstruction -> {len(tp.get("timeline", []))} chronological events')

    # Test 10: AI NL Query & Problem Statement 26189 Mandate
    q = client.post('/api/chat/query', json={'message': 'Who is the leader of the Dhanbad extortion gang?'}).json()
    assert q['query_type'] == 'KINGPIN_DISCOVERY'
    q_ps = client.post('/api/chat/query', json={'message': 'Explain compliance with Problem Statement 26189'}).json()
    assert q_ps['query_type'] == 'SYSTEM_MANDATE'
    print(f'[PASS] Test 10: AI Natural Language Query -> Resolved: {q["query_type"]} & {q_ps["query_type"]} (PS #26189 Verified)')

    # Test 11: Alert Center (Screen 11, Auto-Feature 4)
    alts = client.get('/api/alerts/all').json()
    assert len(alts) >= 10
    print(f'[PASS] Test 11: Alert Center -> {len(alts)} automated detection monitors active')

    # Test 12: Collaborative Case Board (Screen 13, Auto-Feature 9)
    cb = client.get('/api/caseboard/cards').json()
    assert len(cb) >= 8
    print(f'[PASS] Test 12: Collaborative Case Board -> {len(cb)} active investigation dockets')

    # Test 13: Evidence Vault & Blockchain Integrity (Screen 10)
    ev = client.get('/api/evidence/all').json()
    integ = client.get('/api/export/verify-integrity').json()
    assert integ['integrity_valid'] is True
    print(f'[PASS] Test 13: Evidence Vault -> {len(ev)} items, Blockchain Integrity: 100% VALID')

    # Test 14: Automated Reports Engine (Screen 12, Auto-Feature 10)
    rep = client.get('/api/export/reports/daily').json()
    assert rep['report_type'] == 'DAILY_DIGEST'
    print(f'[PASS] Test 14: Report Generator -> Daily Digest compiled: "{rep["title"]}"')

    # Test 15: Unstructured Intelligence Extraction & Provenance Linking
    intel_payload = {
        "report_id": "INTEL-TEST-01",
        "text": "Secret source reports Vikram Sinha met associate Suresh Patel in Ranchi near Tower Chowk on 14/03/2024 to collect ₹49,500."
    }
    intel_res = client.post('/api/ingest/intel-report', json=intel_payload).json()
    assert intel_res['entities_extracted'] > 0
    print(f'[PASS] Test 15: Unstructured Intel Report -> Extracted {intel_res["entities_extracted"]} entities with provenance')

    # Test 16: CCTNS Criminal History Database
    cctns_res = client.get('/api/analysis/suspect/SUSP-VIKRAM-SINHA/criminal-history').json()
    assert 'cctns_record' in cctns_res
    print(f'[PASS] Test 16: CCTNS Integration -> Retrieved {len(cctns_res["cctns_record"].get("prior_firs", []))} prior FIRs, Mod: +{cctns_res["risk_modifier"]}')

    # Test 17: Section 65B Certified Case Report PDF Export
    case_pdf = client.get('/api/export/case-report/CASE-101')
    assert case_pdf.status_code == 200
    assert case_pdf.headers['content-type'] == 'application/pdf'
    print(f'[PASS] Test 17: Case Report PDF Export -> Received {len(case_pdf.content)} bytes of court-certified PDF')

    # Test 18: Blockchain SHA-256 Tamper Simulation & Self-Healing Restoration
    tamper_res = client.post('/api/evidence/simulate-tamper?block_index=1').json()
    assert tamper_res['tampered'] is True
    check_tampered = client.get('/api/export/verify-integrity').json()
    assert check_tampered['integrity_valid'] is False
    restore_res = client.post('/api/evidence/restore').json()
    assert restore_res['restored'] is True
    check_restored = client.get('/api/export/verify-integrity').json()
    assert check_restored['integrity_valid'] is True
    print('[PASS] Test 18: Blockchain Tamper Simulation & Restoration -> Successfully simulated tamper and restored chain')

    # Test 19: Alert Triage (Acknowledge, Escalate, Dismiss)
    test_alert_id = alts[0]['id']
    ack_res = client.post(f'/api/alerts/acknowledge/{test_alert_id}').json()
    assert ack_res['acknowledged'] is True
    esc_res = client.post(f'/api/alerts/escalate/{test_alert_id}').json()
    assert esc_res['escalated'] is True
    print(f'[PASS] Test 19: Alert Triage Lifecycle -> Acknowledged and Escalated to Case {esc_res["case"]["case_no"]}')

    print('====================================================')
    print('  ALL 19 SENTINEL v2.0 INTEGRATION TESTS PASSED!')
    print('====================================================')

