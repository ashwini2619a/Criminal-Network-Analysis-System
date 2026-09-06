import React, { useState, useEffect } from 'react';
import {
  Landmark,
  ArrowRight,
  AlertTriangle,
  RotateCw,
  TrendingDown,
  Download,
  Sliders,
  CheckCircle2,
  RefreshCw,
  ShieldAlert
} from 'lucide-react';
import { getHawala } from '../../lib/api';

export const FinancialFlow: React.FC = () => {
  const [hawalaData, setHawalaData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [maxHours, setMaxHours] = useState<number>(72);
  const [structuringThreshold, setStructuringThreshold] = useState<number>(50000);

  const fetchHawala = () => {
    setLoading(true);
    getHawala(maxHours, structuringThreshold)
      .then(res => setHawalaData(res))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchHawala();
  }, [maxHours, structuringThreshold]);

  const cycles = hawalaData?.cycles || [];
  const structuring = hawalaData?.structuring || hawalaData?.structuring_alerts || [];
  const fanInFanOut = hawalaData?.fan_in_fan_out || [];

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in">
      {/* Top Banner */}
      <div className="border-b border-slate-200/90 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl font-bold tracking-tight text-slate-900 font-sans">
              Mule Layering & Smurfing AML Analysis (PMLA 2002)
            </h1>
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200 tracking-wider">
              PMLA 2002 / FIU-IND COMPLIANT
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-mono tracking-tight font-medium">
            Detects multi-hop mule account layering, circular bank transfers, structuring below ₹50,000 PAN threshold (Sec 139A IT Act), and rapid fan-in/fan-out mule syndicates.
          </p>
          <div className="mt-2 text-[11px] text-amber-800 bg-amber-50/80 border border-amber-200 rounded-lg px-2.5 py-1 font-mono font-medium">
            ℹ️ <strong>Statutory Context:</strong> Domestic banking loops detect structured mule accounts. Informal off-us Hawala networks operate via unrecorded Angadia physical tokens rather than direct banking rails.
          </div>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <button
            onClick={fetchHawala}
            disabled={loading}
            className="px-3.5 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-xs font-mono font-semibold text-slate-700 border border-slate-200 hover:border-sky-300 flex items-center space-x-1.5 transition disabled:opacity-50 shadow-2xs hover:shadow-xs active:scale-95 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-sky-600 ${loading ? 'animate-spin' : ''}`} />
            <span>Recalculate AML</span>
          </button>
          <a
            href="/api/export/excel/transactions"
            target="_blank"
            rel="noreferrer"
            className="px-3.5 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-xs font-mono font-semibold text-slate-700 border border-slate-200 hover:border-amber-400 flex items-center space-x-1.5 transition shadow-2xs hover:shadow-xs active:scale-95 cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-amber-600" />
            <span>Export Transactions (CSV)</span>
          </a>
        </div>
      </div>

      {/* Dynamic Threshold Controls */}
      <div className="p-4 rounded-xl tactical-card flex flex-wrap items-center justify-between gap-4 text-xs font-mono shadow-xs">
        <div className="flex items-center space-x-2 text-sky-800 font-bold uppercase">
          <Sliders className="w-4 h-4 text-sky-600" />
          <span>Algorithmic Detection Thresholds</span>
        </div>

        <div className="flex flex-wrap items-center gap-6">
          {/* Max Cycle Duration */}
          <div className="flex items-center space-x-2">
            <span className="text-slate-500 font-medium">Max Cycle Duration:</span>
            <select
              value={maxHours}
              onChange={(e) => setMaxHours(Number(e.target.value))}
              className="bg-slate-50 border border-slate-200 rounded-md px-2.5 py-1 text-slate-900 focus:outline-none focus:border-sky-500 transition cursor-pointer font-bold"
            >
              <option value={24}>24 Hours</option>
              <option value={48}>48 Hours</option>
              <option value={72}>72 Hours (Default)</option>
              <option value={120}>120 Hours (5 Days)</option>
              <option value={168}>168 Hours (1 Week)</option>
            </select>
          </div>

          {/* Structuring Threshold */}
          <div className="flex items-center space-x-2">
            <span className="text-slate-500 font-medium">Structuring Limit:</span>
            <div className="flex items-center bg-slate-50 border border-slate-200 rounded-md px-2 py-1">
              <span className="text-amber-600 mr-1 font-bold">₹</span>
              <input
                type="number"
                step="5000"
                value={structuringThreshold}
                onChange={(e) => setStructuringThreshold(Number(e.target.value))}
                className="bg-transparent text-slate-900 w-20 focus:outline-none text-right font-mono font-bold"
              />
            </div>
            <span className="text-[10px] text-slate-400 font-medium">(PAN Rule)</span>
          </div>
        </div>
      </div>

      {/* Algorithmic AML Engine: Multi-Hop Mule Layering & Cyclic Transfers */}
      <div className="p-5 rounded-xl tactical-card border-rose-200 space-y-4 relative overflow-hidden before:absolute before:inset-x-0 before:top-0 before:h-[2px] before:bg-gradient-to-r before:from-rose-500 before:via-amber-500 before:to-rose-500 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center space-x-2 text-xs font-bold text-rose-700 uppercase font-mono">
            <RotateCw className={`w-4 h-4 text-rose-600 ${loading ? 'animate-spin' : ''}`} />
            <span>ALGORITHMIC AML ENGINE // MULTI-HOP MULE LAYERING & CYCLIC TRANSFERS</span>
          </div>
          <span className="px-2.5 py-0.5 rounded-md text-[10px] font-mono bg-rose-50 text-rose-800 border border-rose-200 font-bold self-start sm:self-auto shadow-2xs">
            {cycles.length > 0 ? `${cycles.length} CYCLE(S) FLAGGED // ${maxHours}H WINDOW` : 'CLEAN // NO DIRECT CYCLES'}
          </span>
        </div>

        {cycles.length === 0 ? (
          <div className="p-6 rounded-lg bg-slate-50 border border-slate-200 text-center text-xs font-mono text-slate-500">
            No circular mule funds movement detected matching the current criteria ({maxHours}h window).
          </div>
        ) : (
          cycles.map((cycle: any, cIdx: number) => {
            const labels = cycle.cycle_labels || cycle.cycle_nodes || [];
            const txs = cycle.transactions || [];
            return (
              <div key={cIdx} className="space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs font-mono px-1 gap-2">
                  <span className="text-slate-900 font-bold">Loop #{cIdx + 1} ({labels.length} Hop Layering Flow)</span>
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="text-slate-500">Time Span: <strong className="text-sky-700">{cycle.time_span_hours} hrs</strong></span>
                    <span className="text-slate-500">Cyclic Volume: <strong className="text-amber-700 font-bold">₹{cycle.total_amount?.toLocaleString('en-IN')}</strong></span>
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                      cycle.risk_level === 'CRITICAL' ? 'bg-rose-50 text-rose-800 border border-rose-200 shadow-2xs' : 'bg-amber-50 text-amber-800 border border-amber-200'
                    }`}>
                      {cycle.risk_level} RISK
                    </span>
                  </div>
                </div>

                {/* Visual Cyclic Flow Steps */}
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
                  {labels.map((nodeName: string, nIdx: number) => {
                    const tx = txs[nIdx] || {};
                    const amountStr = tx.amount ? `₹${Number(tx.amount).toLocaleString('en-IN')}` : '₹49,500.00';
                    return (
                      <React.Fragment key={nIdx}>
                        <div className="p-3 rounded-lg bg-white border border-slate-200 text-center flex-1 min-w-[130px] shadow-xs hover:border-sky-300 transition-colors">
                          <div className="text-[10px] text-slate-500 font-mono font-semibold">
                            {nIdx === 0 ? 'ORIGIN NODE' : `MULE LAYER ${String.fromCharCode(65 + nIdx)}`}
                          </div>
                          <div className="font-bold text-slate-900 mt-0.5 truncate max-w-[150px] mx-auto" title={nodeName}>
                            {nodeName}
                          </div>
                          <div className="text-[11px] text-amber-700 font-bold mt-1">{amountStr}</div>
                        </div>

                        <ArrowRight className="w-4 h-4 text-slate-400 hidden sm:block shrink-0 animate-pulse" />
                      </React.Fragment>
                    );
                  })}

                  {/* Return to Origin Closure */}
                  <div className="p-3 rounded-lg bg-rose-50/90 border border-rose-200 text-center flex-1 min-w-[130px] shadow-xs">
                    <div className="text-[10px] text-rose-700 font-mono font-bold">RETURN TO ORIGIN</div>
                    <div className="font-bold text-slate-900 mt-0.5 truncate max-w-[150px] mx-auto">
                      {labels[0] || 'Origin'}
                    </div>
                    <div className="text-[10px] text-rose-700 font-bold mt-1">Closed Mule Transfer Loop</div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Structuring / Smurfing & Fan-in Fan-out Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Structuring Panel */}
        <div className="p-5 rounded-xl tactical-card space-y-3 shadow-xs">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span>Structuring / Smurfing Flags (&lt; ₹{structuringThreshold.toLocaleString('en-IN')})</span>
            </h2>
            <span className="text-xs font-mono text-amber-800 font-bold bg-amber-50 px-2 py-0.5 rounded border border-amber-200">PAN Rule Limit</span>
          </div>
          <p className="text-[11px] text-slate-500 font-mono font-medium">
            Accounts intentionally executing transactions in the sub-threshold range to evade mandatory PAN reporting under Income Tax Section 139A / PMLA.
          </p>

          <div className="divide-y divide-slate-200/80 text-xs font-mono max-h-80 overflow-y-auto pr-1">
            {structuring.length === 0 ? (
              <div className="py-6 text-center text-slate-500">No sub-threshold smurfing patterns detected.</div>
            ) : (
              structuring.map((s: any, idx: number) => (
                <div key={idx} className="py-2.5 flex items-center justify-between hover:bg-sky-50/60 px-2 rounded-lg transition-colors cursor-pointer">
                  <div>
                    <div className="font-bold text-slate-900">{s.account_name || s.account_id}</div>
                    <div className="text-[10px] text-slate-500 font-medium">{s.count} staged transfers detected ({s.pattern_type || 'Sub-threshold'})</div>
                  </div>
                  <div className="text-right">
                    <div className="text-amber-800 font-bold">₹{s.total_structured_amount?.toLocaleString('en-IN')}</div>
                    <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                      s.risk_level === 'CRITICAL' ? 'bg-rose-50 text-rose-800 border border-rose-200' : 'bg-amber-50 text-amber-800 border border-amber-200'
                    }`}>
                      {s.risk_level || 'FLAGGED'}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Money Mule Accounts (Fan-In / Fan-Out) */}
        <div className="p-5 rounded-xl tactical-card space-y-3 shadow-xs">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
              <TrendingDown className="w-4 h-4 text-sky-600" />
              <span>Fan-In / Fan-Out Money Mule Nodes</span>
            </h2>
            <span className="text-xs font-mono text-sky-800 font-bold bg-sky-50 px-2 py-0.5 rounded border border-sky-200">Mule Engine</span>
          </div>
          <p className="text-[11px] text-slate-500 font-mono font-medium">
            Nodes aggregating micro-deposits from multiple sources and immediately dispersing to high-level cartel controllers.
          </p>

          <div className="divide-y divide-slate-200/80 text-xs font-mono max-h-80 overflow-y-auto pr-1">
            {fanInFanOut.length === 0 ? (
              <div className="py-6 text-center text-slate-500">No high-risk fan-in/fan-out mule patterns detected.</div>
            ) : (
              fanInFanOut.map((m: any, idx: number) => (
                <div key={idx} className="py-2.5 flex items-center justify-between hover:bg-sky-50/60 px-2 rounded-lg transition-colors cursor-pointer">
                  <div>
                    <div className="font-bold text-slate-900">{m.account_name || m.account_id}</div>
                    <div className="text-[10px] text-slate-500 font-medium">
                      {m.in_count} in (₹{m.in_total?.toLocaleString('en-IN')}) ➔ {m.out_count} out (₹{m.out_total?.toLocaleString('en-IN')})
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sky-700 font-bold">Risk: {m.risk_score}/100</div>
                    <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                      m.pattern_type === 'BOTH' ? 'bg-rose-50 text-rose-800 border border-rose-200' :
                      m.pattern_type === 'FAN_OUT' ? 'bg-sky-50 text-sky-800 border border-sky-200' :
                      'bg-indigo-50 text-indigo-800 border border-indigo-200'
                    }`}>
                      {m.pattern_type || 'FAN-OUT MULE'}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
