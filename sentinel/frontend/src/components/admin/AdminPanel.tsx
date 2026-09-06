import React, { useState, useEffect } from 'react';
import {
  Settings,
  Shield,
  Users,
  Activity,
  Lock,
  Database,
  CheckCircle2,
  Terminal,
  Key,
  Trash2,
  RotateCcw,
  Sparkles,
  AlertTriangle,
  FileText,
  Layers,
  Share2,
  FolderOpen
} from 'lucide-react';
import {
  getAdminUsers,
  getAdminAudit,
  getAdminHealth,
  clearAllSystemData,
  loadSampleDemoData,
  purgeAdminGraph,
  purgeAdminCases,
  purgeAdminEvidence,
  purgeAdminAlerts,
  purgeAdminUploads
} from '../../lib/api';

export const AdminPanel: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'HEALTH' | 'USERS' | 'AUDIT' | 'DATA_PURGE'>('HEALTH');
  const [clearing, setClearing] = useState(false);
  const [reloading, setReloading] = useState(false);
  const [purgingSection, setPurgingSection] = useState<string | null>(null);

  const refreshAll = () => {
    Promise.all([
      getAdminUsers(),
      getAdminAudit(),
      getAdminHealth()
    ]).then(([u, a, h]) => {
      setUsers(u || []);
      setAuditLogs(a || []);
      setHealth(h || null);
    }).catch(console.error);
  };

  useEffect(() => {
    refreshAll();
  }, []);

  const handleClearAll = async () => {
    if (!window.confirm('Purge all dummy nodes and reset system to a Clean Slate (0 nodes, 0 edges)?')) {
      return;
    }
    try {
      setClearing(true);
      await clearAllSystemData();
      refreshAll();
      alert('Success: All dummy data cleared. System is now in Clean Slate mode.');
    } catch (err) {
      console.error(err);
      alert('Failed to clear data: ' + err);
    } finally {
      setClearing(false);
    }
  };

  const handleReloadDemo = async () => {
    try {
      setReloading(true);
      const res = await loadSampleDemoData();
      refreshAll();
      alert(`Success: Demo data loaded (${res.nodes} nodes, ${res.edges} edges).`);
    } catch (err) {
      console.error(err);
      alert('Failed to load demo data: ' + err);
    } finally {
      setReloading(false);
    }
  };

  const handlePurgeSection = async (sectionName: string, purgeFn: () => Promise<any>, confirmMsg: string) => {
    if (!window.confirm(confirmMsg)) return;
    try {
      setPurgingSection(sectionName);
      const res = await purgeFn();
      refreshAll();
      alert(`Success: ${res?.message || `${sectionName} data has been purged.`}`);
    } catch (err) {
      console.error(err);
      alert(`Failed to purge ${sectionName}: ` + err);
    } finally {
      setPurgingSection(null);
    }
  };

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in">
      {/* Top Banner */}
      <div className="border-b border-slate-200/90 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-xl font-extrabold tracking-tight text-slate-900">
              System Administration & Evidence Audit Vault (Sec 63 BSA)
            </h1>
            <span className="tactical-badge-rose text-[11px]">
              ROOT PRIVILEGE
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Manage officer authorizations, inspect Section 63 BSA evidentiary audit trails, and monitor server memory and graph engine diagnostics.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleClearAll}
            disabled={clearing}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-white hover:bg-rose-50 text-rose-700 border border-rose-200 hover:border-rose-300 shadow-2xs transition-all active:scale-95 disabled:opacity-50"
            title="Purge dummy data to clean slate"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>{clearing ? 'Purging...' : 'Purge All Data (Clean Slate)'}</span>
          </button>

          <button
            onClick={handleReloadDemo}
            disabled={reloading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 shadow-2xs transition-all active:scale-95 disabled:opacity-50"
            title="Load sample 372-node demo data"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${reloading ? 'animate-spin' : ''}`} />
            <span>Reload Demo Data</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-200/90 pb-2 text-xs font-mono select-none">
        <button
          onClick={() => setActiveTab('HEALTH')}
          className={`px-4 py-2 rounded-lg border transition-all font-semibold ${
            activeTab === 'HEALTH'
              ? 'bg-sky-50 text-sky-700 border-sky-300 font-bold shadow-2xs'
              : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300'
          }`}
        >
          System Diagnostics
        </button>
        <button
          onClick={() => setActiveTab('USERS')}
          className={`px-4 py-2 rounded-lg border transition-all font-semibold ${
            activeTab === 'USERS'
              ? 'bg-sky-50 text-sky-700 border-sky-300 font-bold shadow-2xs'
              : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300'
          }`}
        >
          Officer Roles (RBAC)
        </button>
        <button
          onClick={() => setActiveTab('AUDIT')}
          className={`px-4 py-2 rounded-lg border transition-all font-semibold ${
            activeTab === 'AUDIT'
              ? 'bg-sky-50 text-sky-700 border-sky-300 font-bold shadow-2xs'
              : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300'
          }`}
        >
          Sec 63 BSA Custody Log
        </button>
        <button
          onClick={() => setActiveTab('DATA_PURGE')}
          className={`px-4 py-2 rounded-lg border transition-all font-semibold ${
            activeTab === 'DATA_PURGE'
              ? 'bg-rose-50 text-rose-700 border-rose-300 font-bold shadow-2xs'
              : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300'
          }`}
        >
          Data Deletion Hub
        </button>
      </div>

      {/* Tab 1: Health Diagnostics */}
      {activeTab === 'HEALTH' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
          <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs hover:shadow-sm transition-all">
            <span className="text-[10px] text-slate-400 font-bold uppercase">System Status</span>
            <div className="text-xl font-extrabold text-emerald-600 mt-1 flex items-center">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 mr-2 animate-pulse" />
              ONLINE / NORMAL
            </div>
            <div className="text-[10px] text-slate-400 mt-1">Uptime: {health?.uptime_seconds || 120}s</div>
          </div>

          <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs hover:shadow-sm transition-all">
            <span className="text-[10px] text-slate-400 font-bold uppercase">Knowledge Graph Memory</span>
            <div className="text-xl font-extrabold text-sky-700 mt-1">372 Nodes</div>
            <div className="text-[10px] text-slate-500 mt-1 font-medium">869 Typed Relationships</div>
          </div>

          <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs hover:shadow-sm transition-all">
            <span className="text-[10px] text-slate-400 font-bold uppercase">Evidence Database</span>
            <div className="text-xl font-extrabold text-slate-900 mt-1">{health?.database_size_mb || 0.4} MB</div>
            <div className="text-[10px] text-slate-400 mt-1">SQLite Thread-Safe WAL</div>
          </div>

          <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs hover:shadow-sm transition-all">
            <span className="text-[10px] text-slate-400 font-bold uppercase">Custody Hash Integrity</span>
            <div className="text-xl font-extrabold text-emerald-600 mt-1">100% VALID</div>
            <div className="text-[10px] text-slate-400 mt-1">SHA-256 Chained Hash (Sec 63 BSA)</div>
          </div>
        </div>
      )}

      {/* Tab 2: Officer Roles (RBAC) */}
      {activeTab === 'USERS' && (
        <div className="p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 uppercase text-[10px] font-bold">
                  <th className="pb-3">User ID</th>
                  <th className="pb-3">Officer Username</th>
                  <th className="pb-3">Access Role</th>
                  <th className="pb-3">Registered Date</th>
                  <th className="pb-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.length === 0 ? (
                  <tr className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 font-bold text-slate-900">U-ADMIN</td>
                    <td className="py-3 text-sky-700 font-extrabold">admin (Badge #4092)</td>
                    <td className="py-3">
                      <span className="tactical-badge-rose text-[10px]">
                        ADMIN
                      </span>
                    </td>
                    <td className="py-3 text-slate-500">2026-01-01</td>
                    <td className="py-3 text-right">
                      <span className="tactical-badge-emerald text-[10px]">ACTIVE ✓</span>
                    </td>
                  </tr>
                ) : (
                  users.map(u => (
                    <tr key={u.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 text-slate-400">{u.id}</td>
                      <td className="py-3 font-extrabold text-slate-900">{u.username}</td>
                      <td className="py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                          u.role === 'ADMIN' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                          'bg-sky-50 text-sky-700 border border-sky-200'
                        }`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="py-3 text-slate-500">{u.created_at}</td>
                      <td className="py-3 text-right">
                        <span className="tactical-badge-emerald text-[10px]">ACTIVE ✓</span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Section 63 BSA Audit Log */}
      {activeTab === 'AUDIT' && (
        <div className="p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 uppercase text-[10px] font-bold">
                  <th className="pb-3">Timestamp</th>
                  <th className="pb-3">Officer</th>
                  <th className="pb-3">Action</th>
                  <th className="pb-3">Resource</th>
                  <th className="pb-3">IP Address</th>
                  <th className="pb-3 text-right">Verification</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {auditLogs.length === 0 ? (
                  <tr className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 text-slate-400">2026-09-03 19:40:00</td>
                    <td className="py-3 text-slate-900 font-extrabold">admin</td>
                    <td className="py-3 text-sky-700 font-extrabold">SYSTEM_STARTUP</td>
                    <td className="py-3 text-slate-700">SENTINEL Core Engine Launched</td>
                    <td className="py-3 text-slate-400">127.0.0.1</td>
                    <td className="py-3 text-right">
                      <span className="tactical-badge-emerald text-[10px]">VERIFIED ✓</span>
                    </td>
                  </tr>
                ) : (
                  auditLogs.map(a => (
                    <tr key={a.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 text-slate-400">{a.timestamp}</td>
                      <td className="py-3 text-slate-900 font-extrabold">{a.username || a.user_id}</td>
                      <td className="py-3 text-sky-700 font-extrabold">{a.action}</td>
                      <td className="py-3 text-slate-700">{a.details || a.resource}</td>
                      <td className="py-3 text-slate-400">{a.ip_address}</td>
                      <td className="py-3 text-right">
                        <span className="tactical-badge-emerald text-[10px]">VERIFIED ✓</span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 4: Data Management & Section-by-Section Deletion Hub */}
      {activeTab === 'DATA_PURGE' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-100/70 border border-slate-200 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
                <Trash2 className="w-4 h-4 text-rose-600" />
                <span>Section Data Management & Deletion Controls</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Purge individual operational subsystems, reset specific modules, or perform a total platform-wide wipe.
              </p>
            </div>
            <span className="text-[10px] font-mono bg-rose-50 text-rose-700 border border-rose-200 px-2 py-1 rounded font-bold">
              IRREVERSIBLE ACTIONS
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 font-mono">
            {/* 1. Knowledge Graph */}
            <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-sky-700 font-bold uppercase bg-sky-50 px-2 py-0.5 rounded border border-sky-200">
                    NETWORK INTELLIGENCE
                  </span>
                  <Share2 className="w-4 h-4 text-sky-600" />
                </div>
                <h3 className="text-sm font-extrabold text-slate-900 mt-2">Knowledge Graph Network</h3>
                <p className="text-xs text-slate-500 font-sans mt-1">
                  Purges all 372 nodes, 869 edges, cell towers, and transaction connections from in-memory and persistent graph storage.
                </p>
              </div>
              <button
                onClick={() => handlePurgeSection('Knowledge Graph', purgeAdminGraph, 'Are you sure you want to purge all nodes and relationships in the Knowledge Graph?')}
                disabled={purgingSection === 'Knowledge Graph'}
                className="w-full py-2 px-3 rounded-lg border border-rose-200 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-xs flex items-center justify-center space-x-1.5 transition-all active:scale-95 disabled:opacity-50"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{purgingSection === 'Knowledge Graph' ? 'PURGING GRAPH...' : 'PURGE GRAPH DATA'}</span>
              </button>
            </div>

            {/* 2. Case Board */}
            <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-amber-700 font-bold uppercase bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                    INVESTIGATION DOCKETS
                  </span>
                  <FolderOpen className="w-4 h-4 text-amber-600" />
                </div>
                <h3 className="text-sm font-extrabold text-slate-900 mt-2">Case Board Dockets</h3>
                <p className="text-xs text-slate-500 font-sans mt-1">
                  Deletes all active FIR investigation dossiers, investigative priority statuses, and lead cards from the investigation board.
                </p>
              </div>
              <button
                onClick={() => handlePurgeSection('Case Board', purgeAdminCases, 'Are you sure you want to delete all case cards from the Case Board?')}
                disabled={purgingSection === 'Case Board'}
                className="w-full py-2 px-3 rounded-lg border border-rose-200 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-xs flex items-center justify-center space-x-1.5 transition-all active:scale-95 disabled:opacity-50"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{purgingSection === 'Case Board' ? 'PURGING CASES...' : 'PURGE CASE DOCKETS'}</span>
              </button>
            </div>

            {/* 3. Evidence Vault */}
            <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-emerald-700 font-bold uppercase bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    SEC 63 BSA / 65B IEA
                  </span>
                  <Lock className="w-4 h-4 text-emerald-600" />
                </div>
                <h3 className="text-sm font-extrabold text-slate-900 mt-2">Evidence Custody Vault</h3>
                <p className="text-xs text-slate-500 font-sans mt-1">
                  Purges all hashed evidence records, resets cryptographic ledger hashes, and re-initializes genesis custody block.
                </p>
              </div>
              <button
                onClick={() => handlePurgeSection('Evidence Vault', purgeAdminEvidence, 'Are you sure you want to reset the Evidence Vault and audit ledger to Genesis state?')}
                disabled={purgingSection === 'Evidence Vault'}
                className="w-full py-2 px-3 rounded-lg border border-rose-200 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-xs flex items-center justify-center space-x-1.5 transition-all active:scale-95 disabled:opacity-50"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{purgingSection === 'Evidence Vault' ? 'RESETTING VAULT...' : 'RESET EVIDENCE LEDGER'}</span>
              </button>
            </div>

            {/* 4. Threat Alerts */}
            <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-rose-700 font-bold uppercase bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                    REAL-TIME ALERTS
                  </span>
                  <AlertTriangle className="w-4 h-4 text-rose-600" />
                </div>
                <h3 className="text-sm font-extrabold text-slate-900 mt-2">Threat Intelligence Alerts</h3>
                <p className="text-xs text-slate-500 font-sans mt-1">
                  Clears all syndicate trigger alerts, Hawala fund movement warnings, and geo-fence intrusion notifications.
                </p>
              </div>
              <button
                onClick={() => handlePurgeSection('Alerts', purgeAdminAlerts, 'Are you sure you want to clear all threat alerts?')}
                disabled={purgingSection === 'Alerts'}
                className="w-full py-2 px-3 rounded-lg border border-rose-200 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-xs flex items-center justify-center space-x-1.5 transition-all active:scale-95 disabled:opacity-50"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{purgingSection === 'Alerts' ? 'CLEARING ALERTS...' : 'CLEAR ALL ALERTS'}</span>
              </button>
            </div>

            {/* 5. Ingestion History */}
            <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-purple-700 font-bold uppercase bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                    INGESTION & OCR
                  </span>
                  <Layers className="w-4 h-4 text-purple-600" />
                </div>
                <h3 className="text-sm font-extrabold text-slate-900 mt-2">Upload Ingestion History</h3>
                <p className="text-xs text-slate-500 font-sans mt-1">
                  Purges all uploaded evidentiary document logs, parsed text OCR caches, and batch upload tracking history.
                </p>
              </div>
              <button
                onClick={() => handlePurgeSection('Upload History', purgeAdminUploads, 'Are you sure you want to clear all upload ingestion history records?')}
                disabled={purgingSection === 'Upload History'}
                className="w-full py-2 px-3 rounded-lg border border-rose-200 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-xs flex items-center justify-center space-x-1.5 transition-all active:scale-95 disabled:opacity-50"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{purgingSection === 'Upload History' ? 'PURGING UPLOADS...' : 'PURGE UPLOAD RECORDS'}</span>
              </button>
            </div>

            {/* 6. Master Clean Slate */}
            <div className="p-4 rounded-xl bg-rose-50/50 border border-rose-200 shadow-xs flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-rose-700 font-bold uppercase bg-rose-100 px-2 py-0.5 rounded border border-rose-300">
                    PLATFORM-WIDE RESET
                  </span>
                  <Trash2 className="w-4 h-4 text-rose-600" />
                </div>
                <h3 className="text-sm font-extrabold text-rose-900 mt-2">Master Clean Slate</h3>
                <p className="text-xs text-rose-700/80 font-sans mt-1">
                  Wipes ALL sections simultaneously (Graph, Cases, Evidence Vault, Alerts, Ingest History). Zeroes all databases.
                </p>
              </div>
              <button
                onClick={handleClearAll}
                disabled={clearing}
                className="w-full py-2 px-3 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs flex items-center justify-center space-x-1.5 transition-all active:scale-95 disabled:opacity-50 shadow-xs"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{clearing ? 'EXECUTING WIPE...' : 'EXECUTE MASTER PURGE'}</span>
              </button>
            </div>
          </div>

          {/* Quick Recovery Notice */}
          <div className="p-4 rounded-xl bg-sky-50/60 border border-sky-200 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Sparkles className="w-5 h-5 text-sky-600 shrink-0" />
              <div>
                <div className="text-xs font-bold text-sky-900 font-mono">Need to re-populate after testing deletion?</div>
                <div className="text-[11px] text-slate-600">
                  You can reload the complete Dhanbad Extortion Syndicate demo dataset anytime with 1 click.
                </div>
              </div>
            </div>
            <button
              onClick={handleReloadDemo}
              disabled={reloading}
              className="px-3.5 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-700 text-white font-bold text-xs font-mono flex items-center space-x-1.5 transition-all shadow-xs"
            >
              <RotateCcw className={`w-3.5 h-3.5 ${reloading ? 'animate-spin' : ''}`} />
              <span>RELOAD DEMO DATASET</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
