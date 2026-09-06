import React, { useState, useEffect } from 'react';
import {
  FileSpreadsheet,
  Download,
  Calendar,
  Shield,
  FileText,
  Activity,
  CheckCircle2,
  TrendingUp,
  Clock
} from 'lucide-react';
import { getDailyDigest, getWeeklyBrief, getMonthlyStats } from '../../lib/api';

export const ReportGenerator: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'DAILY' | 'WEEKLY' | 'MONTHLY'>('DAILY');
  const [reportData, setReportData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    let promise: Promise<any>;
    if (activeTab === 'DAILY') {
      promise = getDailyDigest();
    } else if (activeTab === 'WEEKLY') {
      promise = getWeeklyBrief();
    } else {
      promise = getMonthlyStats();
    }

    promise
      .then(res => setReportData(res))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [activeTab]);

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in">
      {/* Top Banner */}
      <div className="border-b border-slate-200/90 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-xl font-extrabold tracking-tight text-slate-900">
              Automated Intelligence Report Generator
            </h1>
            <span className="tactical-badge-sky text-[11px]">
              ZERO HUMAN COMPILATION
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Auto-compiles executive briefings, weekly threat appraisals, and court-admissible dossiers without manual word processing.
          </p>
        </div>

        {/* Quick Excel Exports */}
        <div className="flex items-center space-x-2">
          <a
            href="/api/export/excel/suspects"
            target="_blank"
            rel="noreferrer"
            className="tactical-btn-secondary text-xs font-mono flex items-center space-x-1.5 shadow-xs"
          >
            <Download className="w-3.5 h-3.5 text-sky-600" />
            <span>Suspects (CSV)</span>
          </a>
          <a
            href="/api/export/excel/transactions"
            target="_blank"
            rel="noreferrer"
            className="tactical-btn-secondary text-xs font-mono flex items-center space-x-1.5 shadow-xs"
          >
            <Download className="w-3.5 h-3.5 text-amber-600" />
            <span>Mule AML Transactions (CSV)</span>
          </a>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex items-center space-x-2 border-b border-slate-200/90 pb-2 text-xs font-mono select-none">
        <button
          onClick={() => setActiveTab('DAILY')}
          className={`px-4 py-2 rounded-lg border transition-all font-semibold ${
            activeTab === 'DAILY'
              ? 'bg-sky-50 text-sky-700 border-sky-300 font-bold shadow-2xs'
              : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300'
          }`}
        >
          Daily Digest
        </button>
        <button
          onClick={() => setActiveTab('WEEKLY')}
          className={`px-4 py-2 rounded-lg border transition-all font-semibold ${
            activeTab === 'WEEKLY'
              ? 'bg-sky-50 text-sky-700 border-sky-300 font-bold shadow-2xs'
              : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300'
          }`}
        >
          Weekly Intelligence Brief
        </button>
        <button
          onClick={() => setActiveTab('MONTHLY')}
          className={`px-4 py-2 rounded-lg border transition-all font-semibold ${
            activeTab === 'MONTHLY'
              ? 'bg-sky-50 text-sky-700 border-sky-300 font-bold shadow-2xs'
              : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300'
          }`}
        >
          Monthly Statistics
        </button>
      </div>

      {/* Report Preview Document */}
      <div className="p-8 rounded-2xl bg-white border border-slate-200/90 space-y-6 max-w-4xl mx-auto shadow-sm">
        {/* Document Header */}
        <div className="border-b border-slate-200 pb-4 flex items-center justify-between">
          <div>
            <div className="text-[10px] font-mono text-rose-600 tracking-wider uppercase font-extrabold">
              OFFICIAL LAW ENFORCEMENT SENSITIVE // MHA NCRB
            </div>
            <h2 className="text-xl font-extrabold text-slate-900 mt-1 tracking-tight">{reportData?.title || 'Intelligence Report'}</h2>
            <div className="text-xs font-mono text-slate-500 mt-0.5 flex items-center space-x-2">
              <Clock className="w-3.5 h-3.5 text-sky-600" />
              <span>Generated: {reportData?.generated_at || new Date().toISOString()}</span>
            </div>
          </div>

          <div className="text-right">
            <span className="tactical-badge-emerald text-xs font-mono font-bold flex items-center py-1">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />
              <span>DIGITALLY CERTIFIED</span>
            </span>
          </div>
        </div>

        {/* Dynamic Content based on Tab */}
        {activeTab === 'DAILY' && reportData?.summary && (
          <div className="space-y-6 text-xs font-mono">
            {/* KPI Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80">
                <span className="text-[10px] text-slate-400 font-bold uppercase">ACTIVE THREAT ALERTS:</span>
                <div className="text-xl font-extrabold text-rose-600 mt-1">{reportData.summary.active_threat_alerts}</div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80">
                <span className="text-[10px] text-slate-400 font-bold uppercase">CRITICAL PRIORITY:</span>
                <div className="text-xl font-extrabold text-rose-600 mt-1">{reportData.summary.critical_alerts_count}</div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80">
                <span className="text-[10px] text-slate-400 font-bold uppercase">CASES ACTIVE:</span>
                <div className="text-xl font-extrabold text-slate-900 mt-1">{reportData.summary.total_cases_active}</div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80">
                <span className="text-[10px] text-slate-400 font-bold uppercase">TOTAL ENTITIES:</span>
                <div className="text-xl font-extrabold text-sky-700 mt-1">{reportData.summary.total_network_entities}</div>
              </div>
            </div>

            {/* Action Items */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <div className="font-extrabold text-sky-700 uppercase tracking-wider text-[11px]">Recommended Executive Operations:</div>
              <ul className="list-disc pl-4 space-y-1.5 text-slate-700 font-sans text-xs">
                {(reportData.action_items || []).map((item: string, idx: number) => (
                  <li key={idx} className="leading-relaxed">{item}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'WEEKLY' && (
          <div className="space-y-4 text-xs font-mono">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <div className="font-extrabold text-amber-700 uppercase tracking-wider text-[11px]">Strategic Threat Assessment:</div>
              <p className="text-slate-700 leading-relaxed font-sans text-xs">
                {reportData?.strategic_assessment}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <div className="font-extrabold text-sky-700 uppercase tracking-wider text-[11px]">Top Syndicate Targets:</div>
              <div className="divide-y divide-slate-200/80">
                {(reportData?.top_threat_entities || []).map((t: any, idx: number) => (
                  <div key={idx} className="py-2.5 flex items-center justify-between">
                    <div>
                      <span className="font-extrabold text-slate-900">{t.name}</span>
                      <span className="text-slate-400 ml-2 font-normal">({t.role})</span>
                    </div>
                    <span className="text-rose-600 font-extrabold font-mono">{t.threat_score}/100 Risk</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'MONTHLY' && reportData?.metrics && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs font-mono">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
              <span className="text-[10px] text-slate-400 font-bold uppercase">CLEARANCE RATE:</span>
              <div className="text-2xl font-extrabold text-emerald-600 mt-1">{reportData.metrics.clearance_rate_pct}%</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
              <span className="text-[10px] text-slate-400 font-bold uppercase">LAUNDERED MULE FUNDS FROZEN:</span>
              <div className="text-2xl font-extrabold text-amber-600 mt-1">₹{reportData.metrics.hawala_funds_frozen_inr?.toLocaleString('en-IN')}</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
              <span className="text-[10px] text-slate-400 font-bold uppercase">BURNERS NEUTRALIZED:</span>
              <div className="text-2xl font-extrabold text-sky-700 mt-1">{reportData.metrics.burner_phones_neutralized}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
