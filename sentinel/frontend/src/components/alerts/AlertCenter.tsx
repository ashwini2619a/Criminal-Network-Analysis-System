import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  CheckCircle2,
  Shield,
  ShieldAlert,
  ArrowUpRight,
  Filter,
  BellRing,
  RotateCw,
  PhoneCall,
  Activity,
  Zap,
  Radio,
  Building,
  RadioTower,
  Key,
  FolderPlus,
  Trash2,
  Check
} from 'lucide-react';
import { getAllAlerts, getAlertsSummary, acknowledgeAlert, dismissAlert, escalateAlert } from '../../lib/api';
import { SecurityAlert } from '../../types';

export const AlertCenter: React.FC = () => {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);
  const [escalatedNotice, setEscalatedNotice] = useState<{ alertId: string; caseNo: string; caseId: string } | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [all, sum] = await Promise.all([
        getAllAlerts(),
        getAlertsSummary()
      ]);
      setAlerts(all || []);
      setSummary(sum || null);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAcknowledge = async (alertId: string) => {
    try {
      await acknowledgeAlert(alertId);
      setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, acknowledged: true } : a));
      if (summary) {
        setSummary({ ...summary, unacknowledged: Math.max(0, summary.unacknowledged - 1) });
      }
    } catch (err) {
      console.error('Acknowledge error:', err);
    }
  };

  const handleDismiss = async (alertId: string) => {
    try {
      await dismissAlert(alertId);
      setAlerts(prev => prev.filter(a => a.id !== alertId));
      if (summary) {
        setSummary({
          ...summary,
          total: Math.max(0, summary.total - 1),
          unacknowledged: Math.max(0, summary.unacknowledged - 1)
        });
      }
    } catch (err) {
      console.error('Dismiss error:', err);
    }
  };

  const handleEscalate = async (alertId: string) => {
    try {
      const res = await escalateAlert(alertId);
      if (res && res.case) {
        setEscalatedNotice({
          alertId,
          caseNo: res.case.case_no,
          caseId: res.case.id
        });
        setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, acknowledged: true } : a));
      }
    } catch (err) {
      console.error('Escalate error:', err);
    }
  };

  const filteredAlerts = priorityFilter === 'ALL'
    ? alerts
    : alerts.filter(a => a.priority === priorityFilter);

  const getAlertIcon = (alertType: string) => {
    switch (alertType) {
      case 'SHADOW_KINGPIN':
        return <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0" />;
      case 'HAWALA_LOOP':
        return <Activity className="w-4 h-4 text-rose-600 shrink-0" />;
      case 'BURNER_PHONE_CHAIN':
      case 'SIM_SWAP':
        return <Radio className="w-4 h-4 text-amber-600 shrink-0" />;
      case 'CO_LOCATION':
        return <RadioTower className="w-4 h-4 text-sky-600 shrink-0" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />;
    }
  };

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in">
      {/* Top Banner */}
      <div className="border-b border-slate-200/90 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-xl font-extrabold tracking-tight text-slate-900">
              Automated Threat & Pattern Alert Center
            </h1>
            <span className="tactical-badge-rose text-[11px]">
              10 ALGORITHM MONITORS
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Continuous heuristic surveillance engine monitoring graph topology, Hawala structuring, burner hardware reuse, and spatio-temporal co-locations.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={loadData}
            className="tactical-btn-secondary flex items-center space-x-2 text-xs font-mono shadow-xs cursor-pointer"
          >
            <RotateCw className={`w-3.5 h-3.5 text-sky-600 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Rule Engine</span>
          </button>
          <button
            onClick={async () => {
              if (!window.confirm('Are you sure you want to clear all automated alert records?')) return;
              try {
                const { clearAlerts } = await import('../../lib/api');
                await clearAlerts();
                loadData();
              } catch (e) {
                console.error(e);
              }
            }}
            className="tactical-btn-secondary text-rose-700 hover:bg-rose-50 hover:border-rose-300 border-rose-200 flex items-center space-x-1.5 text-xs font-mono shadow-xs cursor-pointer"
            title="Clear all automated alert records"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear All Alerts</span>
          </button>
        </div>
      </div>

      {/* Escalated Notification Banner */}
      {escalatedNotice && (
        <div className="p-4 rounded-xl bg-emerald-50/80 border border-emerald-200 flex items-center justify-between animate-fade-in shadow-xs">
          <div className="flex items-center space-x-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <div>
              <div className="text-sm font-bold text-emerald-950">Alert Successfully Escalated to Active Investigation</div>
              <div className="text-xs text-emerald-800 font-mono mt-0.5">
                Generated Docket Case No: <span className="font-extrabold text-slate-900">{escalatedNotice.caseNo}</span> | Synced to Collaborative Case Board.
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate('/caseboard')}
              className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-mono text-xs font-bold transition-all flex items-center space-x-1 shadow-xs active:scale-95"
            >
              <span>Open Case Board</span>
              <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
            </button>
            <button
              onClick={() => setEscalatedNotice(null)}
              className="px-2 py-1 rounded text-xs text-slate-400 hover:text-slate-700 transition-all"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs hover:shadow-sm transition-all">
          <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold">Total Alerts Flagged</div>
          <div className="text-2xl font-extrabold font-mono text-slate-900 mt-1">{summary?.total || 10}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Automated surveillance</div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs hover:shadow-sm transition-all">
          <div className="text-[10px] font-mono uppercase tracking-wider text-rose-600 font-bold">Critical Threats</div>
          <div className="text-2xl font-extrabold font-mono text-rose-600 mt-1">{summary?.critical || 3}</div>
          <div className="text-[10px] text-rose-600/80 mt-0.5">Shadow Kingpin & Hawala</div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs hover:shadow-sm transition-all">
          <div className="text-[10px] font-mono uppercase tracking-wider text-amber-600 font-bold">High Priority</div>
          <div className="text-2xl font-extrabold font-mono text-amber-600 mt-1">{summary?.high || 4}</div>
          <div className="text-[10px] text-amber-600/80 mt-0.5">Burners & Pre-Crime Spikes</div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs hover:shadow-sm transition-all">
          <div className="text-[10px] font-mono uppercase tracking-wider text-sky-600 font-bold">Unacknowledged</div>
          <div className="text-2xl font-extrabold font-mono text-sky-600 mt-1">{summary?.unacknowledged || 10}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Pending Officer Review</div>
        </div>
      </div>

      {/* Priority Filters */}
      <div className="flex items-center space-x-2 text-xs font-mono">
        {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map(p => (
          <button
            key={p}
            onClick={() => setPriorityFilter(p)}
            className={`px-3 py-1.5 rounded-lg border transition-all font-semibold ${
              priorityFilter === p
                ? 'bg-sky-50 text-sky-700 border-sky-300 font-bold shadow-2xs'
                : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300 shadow-2xs'
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      {/* Alerts Feed */}
      <div className="space-y-3">
        {filteredAlerts.map((alert) => {
          const isCrit = alert.priority === 'CRITICAL';
          const isHigh = alert.priority === 'HIGH';

          return (
            <div
              key={alert.id}
              className={`p-4 rounded-xl bg-white border transition-all duration-200 shadow-2xs hover:shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                alert.acknowledged
                  ? 'opacity-60 border-slate-200 bg-slate-50/40'
                  : isCrit
                  ? 'border-rose-300 bg-gradient-to-r from-rose-50/30 to-white'
                  : isHigh
                  ? 'border-amber-300 bg-gradient-to-r from-amber-50/30 to-white'
                  : 'border-slate-200/90'
              }`}
            >
              <div className="space-y-1.5 flex-1">
                <div className="flex items-center space-x-2.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
                    isCrit ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                    isHigh ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                    'bg-slate-100 text-slate-700 border border-slate-200'
                  }`}>
                    {alert.priority}
                  </span>
                  <span className="text-[11px] font-mono text-slate-500 font-semibold">{alert.alert_type}</span>
                  <span className="text-[10px] font-mono text-slate-400">• {alert.timestamp}</span>
                </div>

                <div className="text-sm font-extrabold text-slate-900 flex items-center space-x-2">
                  {getAlertIcon(alert.alert_type)}
                  <span>{alert.title}</span>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed font-normal">
                  {alert.description}
                </p>
              </div>

              {/* Triage Action Suite */}
              <div className="flex items-center space-x-2 shrink-0">
                {alert.action_url && (
                  <button
                    onClick={() => navigate(alert.action_url!)}
                    className="px-2.5 py-1.5 rounded-lg bg-sky-50 hover:bg-sky-100 text-sky-700 font-mono text-xs font-semibold border border-sky-200 transition-all flex items-center space-x-1 shadow-2xs active:scale-95"
                    title="Jump to correlated graph/geo entity"
                  >
                    <span>Inspect</span>
                    <ArrowUpRight className="w-3.5 h-3.5 ml-0.5" />
                  </button>
                )}

                <button
                  onClick={() => handleEscalate(alert.id)}
                  className="px-2.5 py-1.5 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 font-mono text-xs font-semibold border border-amber-200 transition-all flex items-center space-x-1 shadow-2xs active:scale-95"
                  title="Escalate alert to formal case docket on Case Board"
                >
                  <FolderPlus className="w-3.5 h-3.5 text-amber-700" />
                  <span>Escalate</span>
                </button>

                <button
                  onClick={() => handleAcknowledge(alert.id)}
                  disabled={alert.acknowledged}
                  className={`px-2.5 py-1.5 rounded-lg font-mono text-xs border transition-all flex items-center space-x-1 shadow-2xs ${
                    alert.acknowledged
                      ? 'bg-slate-50 text-slate-400 border-slate-200 cursor-not-allowed'
                      : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200 active:scale-95 font-medium'
                  }`}
                  title="Acknowledge alert"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>{alert.acknowledged ? 'Acked ✓' : 'Acknowledge'}</span>
                </button>

                <button
                  onClick={() => handleDismiss(alert.id)}
                  className="p-1.5 rounded-lg bg-white hover:bg-rose-50 text-slate-400 hover:text-rose-600 border border-slate-200 hover:border-rose-200 transition-all shadow-2xs active:scale-95"
                  title="Dismiss alert"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
