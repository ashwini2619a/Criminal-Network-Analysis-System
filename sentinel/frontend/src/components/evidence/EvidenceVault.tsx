import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Lock,
  FileCheck,
  CheckCircle2,
  AlertTriangle,
  QrCode,
  Download,
  RefreshCw,
  Search,
  ExternalLink,
  Flame,
  RotateCcw,
  ShieldAlert,
  Trash2
} from 'lucide-react';
import {
  getAllEvidence,
  verifyEvidence,
  verifyChainIntegrity,
  simulateEvidenceTamper,
  restoreEvidenceIntegrity,
  deleteEvidence,
  clearEvidenceVault
} from '../../lib/api';

export const EvidenceVault: React.FC = () => {
  const [evidenceList, setEvidenceList] = useState<any[]>([]);
  const [verifying, setVerifying] = useState(false);
  const [tampering, setTampering] = useState(false);
  const [chainStatus, setChainStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadEvidence = async () => {
    try {
      setLoading(true);
      const [evList, chain] = await Promise.all([
        getAllEvidence(),
        verifyChainIntegrity()
      ]);
      setEvidenceList(evList || []);
      setChainStatus(chain || null);
    } catch (err) {
      console.error('Failed to load evidence vault:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvidence();
  }, []);

  const handleVerifyChain = async () => {
    try {
      setVerifying(true);
      const res = await verifyChainIntegrity();
      setChainStatus(res);
      await loadEvidence();
    } catch (err) {
      alert('Verification error: ' + err);
    } finally {
      setVerifying(false);
    }
  };

  const handleSimulateTamper = async () => {
    try {
      setTampering(true);
      await simulateEvidenceTamper(1);
      await loadEvidence();
    } catch (err) {
      alert('Simulation error: ' + err);
    } finally {
      setTampering(false);
    }
  };

  const handleRestoreIntegrity = async () => {
    try {
      setTampering(true);
      await restoreEvidenceIntegrity();
      await loadEvidence();
    } catch (err) {
      alert('Restore error: ' + err);
    } finally {
      setTampering(false);
    }
  };

  const handleDeleteEvidence = async (id: string, fileName: string) => {
    if (!window.confirm(`Are you sure you want to purge evidence item ${fileName || id}?`)) return;
    try {
      await deleteEvidence(fileName || id);
      setEvidenceList(prev => prev.filter(e => e.id !== id && e.file_name !== fileName));
    } catch (err) {
      alert('Failed to delete evidence: ' + err);
    }
  };

  const handleClearVault = async () => {
    if (!window.confirm('Are you sure you want to reset the Evidence Vault and cryptographic ledger to Genesis state?')) return;
    try {
      await clearEvidenceVault();
      await loadEvidence();
    } catch (err) {
      alert('Failed to clear vault: ' + err);
    }
  };

  const isTampered = chainStatus && (!chainStatus.integrity_valid || chainStatus.tampering_detected);

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in">
      {/* Top Banner */}
      <div className="border-b border-slate-200/90 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-xl font-extrabold tracking-tight text-slate-900">
              Digital Evidence Custody Vault (Sec 63 BSA / 65B IEA Certified)
            </h1>
            <span className={`text-[11px] font-mono px-2.5 py-1 rounded-full font-bold uppercase tracking-wider ${
              isTampered ? 'bg-rose-50 text-rose-700 border border-rose-200 animate-pulse' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
            }`}>
              {isTampered ? 'TAMPERING DETECTED' : 'SEC 63 BSA COMPLIANT'}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Tamper-evident SHA-256 cryptographic custody ledger. Every document, CDR file, and wiretap intercept is hashed and chained to guarantee statutory court admissibility under Section 63 Bharatiya Sakshya Adhiniyam, 2023 / Section 65B Indian Evidence Act.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Tamper Simulation Button */}
          {!isTampered ? (
            <button
              onClick={handleSimulateTamper}
              disabled={tampering || loading}
              className="tactical-btn-danger text-xs font-mono flex items-center space-x-1.5 shadow-xs"
              title="Simulate unauthorized evidence database tampering to test custody chain verification"
            >
              <Flame className="w-4 h-4 text-rose-600" />
              <span>{tampering ? 'TAMPERING...' : 'SIMULATE EVIDENCE TAMPERING'}</span>
            </button>
          ) : (
            <button
              onClick={handleRestoreIntegrity}
              disabled={tampering || loading}
              className="tactical-btn-secondary text-xs font-mono flex items-center space-x-1.5 shadow-xs"
            >
              <RotateCcw className="w-4 h-4 text-sky-600" />
              <span>RESTORE CUSTODY INTEGRITY</span>
            </button>
          )}

          <button
            onClick={handleClearVault}
            className="px-3 py-1.5 rounded-lg border border-rose-200 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-xs font-mono flex items-center space-x-1.5 transition-all shadow-xs"
            title="Reset Evidence Vault to Genesis block"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>RESET VAULT</span>
          </button>

          <button
            onClick={handleVerifyChain}
            disabled={verifying}
            className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs font-mono flex items-center space-x-1.5 transition-all shadow-xs disabled:opacity-50 active:scale-95"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>{verifying ? 'VERIFYING CHAIN...' : 'RUN STATUTORY INTEGRITY AUDIT'}</span>
          </button>
        </div>
      </div>

      {/* Critical Tampering Warning Banner (when tampered) */}
      {isTampered && (
        <div className="p-5 rounded-xl bg-rose-50/70 border-2 border-rose-500 space-y-2 animate-pulse shadow-xs">
          <div className="flex items-center space-x-2 text-rose-700 font-extrabold font-mono text-sm uppercase">
            <ShieldAlert className="w-5 h-5 text-rose-600" />
            <span>CRITICAL ALERT: CRYPTOGRAPHIC HASH CHAIN TAMPERING DETECTED</span>
          </div>
          <p className="text-xs text-slate-700 font-medium">
            A byte-level hash mismatch was caught between sequential custody records. An evidence record or its SHA-256 digest was modified post-sealing. Section 63 BSA / 65B IEA judicial certification is invalidated for this custody chain.
          </p>
          <div className="flex items-center space-x-4 text-[11px] font-mono text-rose-700 pt-1 font-bold">
            <span>Violated Block: <strong>#1 (FIR Evidence)</strong></span>
            <span>Custody Integrity: <strong>BROKEN</strong></span>
            <span>Court Admissibility: <strong>INVALIDATED (SEC 63 BSA)</strong></span>
          </div>
        </div>
      )}

      {/* Integrity Status Card */}
      <div className={`p-4 rounded-xl border flex flex-wrap items-center justify-between gap-4 shadow-xs ${
        isTampered ? 'bg-rose-50/50 border-rose-300' : 'bg-white border-slate-200/90'
      }`}>
        <div className="flex items-center space-x-3">
          <div className={`p-2.5 rounded-lg border ${
            isTampered ? 'bg-rose-50 border-rose-200 text-rose-600' : 'bg-emerald-50 border-emerald-200 text-emerald-600'
          }`}>
            {isTampered ? <AlertTriangle className="w-5 h-5" /> : <CheckCircle2 className="w-5 h-5" />}
          </div>
          <div>
            <div className="text-[10px] font-mono uppercase text-slate-400 font-bold">Cryptographic Proof Status</div>
            <div className="text-sm font-extrabold text-slate-900 flex items-center space-x-2 mt-0.5">
              <span>{isTampered ? 'CHAIN COMPROMISED // HASH MISMATCH' : 'CHAIN INTEGRITY VALIDATED // SEC 63 BSA COMPLIANT'}</span>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                isTampered ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
              }`}>
                {isTampered ? 'EVIDENCE COMPROMISED' : 'COURT ADMISSIBLE (SEC 63)'}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-6 text-xs font-mono">
          <div>
            <span className="text-slate-400 font-bold text-[10px] uppercase">SEALED BLOCKS:</span>
            <span className="text-slate-900 font-extrabold ml-1.5">{chainStatus?.total_blocks || evidenceList.length || 26}</span>
          </div>
          <div>
            <span className="text-slate-400 font-bold text-[10px] uppercase">HASH ALGORITHM:</span>
            <span className="text-sky-700 font-extrabold ml-1.5">SHA-256</span>
          </div>
          <div>
            <span className="text-slate-400 font-bold text-[10px] uppercase">STATUTORY AUDIT:</span>
            <span className="text-emerald-700 font-extrabold ml-1.5">SEC 63 BSA / 65B IEA</span>
          </div>
        </div>
      </div>

      {/* Evidence Table */}
      <div className="p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-400 font-mono uppercase text-[10px] font-bold">
                <th className="pb-3">Evidence ID</th>
                <th className="pb-3">File Name</th>
                <th className="pb-3">Type</th>
                <th className="pb-3">Sealed By</th>
                <th className="pb-3">SHA-256 Cryptographic Hash</th>
                <th className="pb-3 text-right">Chain Status</th>
                <th className="pb-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {evidenceList.map((ev, idx) => {
                const isCorrupted = !ev.integrity_verified;
                return (
                  <tr key={ev.id || idx} className={`transition-colors ${
                    isCorrupted ? 'bg-rose-50/70 hover:bg-rose-100/50 border-l-2 border-rose-500' : 'hover:bg-slate-50/80'
                  }`}>
                    <td className="py-3 font-mono text-sky-700 font-bold">{ev.id}</td>
                    <td className="py-3 font-semibold text-slate-900 flex items-center space-x-1.5">
                      {isCorrupted && <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0" />}
                      <span>{ev.file_name}</span>
                    </td>
                    <td className="py-3 font-mono text-slate-500">{ev.file_type}</td>
                    <td className="py-3 font-mono text-slate-600 font-medium">{ev.uploaded_by || 'Investigator'}</td>
                    <td className={`py-3 font-mono select-all ${isCorrupted ? 'text-rose-600 font-bold' : 'text-sky-700'}`}>
                      {ev.file_hash_sha256 ? `${ev.file_hash_sha256.slice(0, 24)}...` : 'SEALED'}
                    </td>
                    <td className="py-3 text-right">
                      {isCorrupted ? (
                        <span className="tactical-badge-rose text-[10px] font-bold animate-pulse">
                          TAMPERED ✗
                        </span>
                      ) : (
                        <span className="tactical-badge-emerald text-[10px]">
                          SEALED ✓
                        </span>
                      )}
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => handleDeleteEvidence(ev.id, ev.file_name)}
                        className="p-1 rounded text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                        title={`Purge evidence ${ev.file_name || ev.id}`}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
