import React, { useState, useEffect } from 'react';
import {
  Kanban,
  Plus,
  ArrowRight,
  ArrowLeft,
  Briefcase,
  Users,
  ShieldCheck,
  Clock,
  MessageSquare,
  AlertTriangle,
  FileText,
  Trash2
} from 'lucide-react';
import { getCaseCards, moveCaseCard, addCaseCard, deleteCaseCard, clearCaseCards } from '../../lib/api';
import { CaseCardData } from '../../types';

export const CaseBoard: React.FC = () => {
  const [cases, setCases] = useState<CaseCardData[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newCrimeType, setNewCrimeType] = useState('EXTORTION');
  const [newOfficer, setNewOfficer] = useState('Inspector R. K. Choudhary');

  const loadCards = async () => {
    try {
      setLoading(true);
      const res = await getCaseCards();
      setCases(res || []);
    } catch (err) {
      console.error('Failed to load caseboard cards:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCards();
  }, []);

  const columns: Array<{ key: CaseCardData['status']; label: string; color: string }> = [
    { key: 'NEW', label: '1. Ingested & Registered', color: 'border-sky-500' },
    { key: 'UNDER_ANALYSIS', label: '2. Under Graph Analysis', color: 'border-amber-500' },
    { key: 'LEADS_GENERATED', label: '3. Actionable Leads', color: 'border-indigo-500' },
    { key: 'CHARGESHEET_READY', label: '4. Chargesheet / Court Ready', color: 'border-emerald-500' }
  ];

  const handleMove = async (caseId: string, currentStatus: string, direction: 'forward' | 'backward') => {
    const statusOrder: CaseCardData['status'][] = ['NEW', 'UNDER_ANALYSIS', 'LEADS_GENERATED', 'CHARGESHEET_READY'];
    const currIdx = statusOrder.indexOf(currentStatus as any);
    const newIdx = direction === 'forward' ? currIdx + 1 : currIdx - 1;

    if (newIdx < 0 || newIdx >= statusOrder.length) return;
    const nextStatus = statusOrder[newIdx];

    try {
      await moveCaseCard(caseId, nextStatus);
      setCases(prev => prev.map(c => c.id === caseId ? { ...c, status: nextStatus } : c));
    } catch (err) {
      console.error('Move case error:', err);
    }
  };

  const handleCreateCase = async () => {
    if (!newTitle) return;
    const newCard: Partial<CaseCardData> = {
      id: `CASE-MANUAL-${Date.now()}`,
      case_no: `FIR/2026/${Math.floor(100 + Math.random() * 900)}`,
      title: newTitle,
      crime_type: newCrimeType,
      severity: 'HIGH',
      status: 'NEW',
      assigned_officer: newOfficer,
      lead_suspect: 'Suspect Under Review',
      suspect_count: 2,
      evidence_count: 3,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      notes: [{ author: newOfficer, text: 'Case initiated for tactical network analysis', timestamp: new Date().toISOString() }]
    };

    try {
      await addCaseCard(newCard);
      await loadCards();
      setShowAddModal(false);
      setNewTitle('');
    } catch (err) {
      alert('Error creating case: ' + err);
    }
  };

  const handleDeleteCase = async (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (!window.confirm(`Delete case docket ${id}?`)) return;
    try {
      await deleteCaseCard(id);
      setCases(prev => prev.filter(c => c.id !== id));
    } catch (err) {
      alert('Failed to delete case: ' + err);
    }
  };

  const handleClearAllCases = async () => {
    if (!window.confirm('Are you sure you want to clear ALL case dockets from the Case Board?')) return;
    try {
      await clearCaseCards();
      await loadCards();
    } catch (err) {
      alert('Failed to clear cases: ' + err);
    }
  };

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in">
      {/* Top Banner */}
      <div className="border-b border-slate-200/90 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-xl font-extrabold tracking-tight text-slate-900">
              Collaborative Multi-Officer Case Board
            </h1>
            <span className="tactical-badge-sky text-[11px]">
              KANBAN PIPELINE
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Real-time multi-investigator case tracking from initial FIR intake through graph intelligence to court-ready chargesheet.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <a
            href="/api/export/case-report/NCRB_SUMMARY_2026"
            target="_blank"
            rel="noreferrer"
            className="tactical-btn-secondary text-xs font-mono flex items-center space-x-1.5 shadow-xs"
          >
            <FileText className="w-4 h-4 text-amber-600" />
            <span>Export Case Brief (PDF)</span>
          </a>
          <button
            onClick={handleClearAllCases}
            className="tactical-btn-secondary text-rose-700 hover:bg-rose-50 hover:border-rose-300 border-rose-200 text-xs font-mono flex items-center space-x-1.5 shadow-xs cursor-pointer"
            title="Clear all case dockets from Case Board"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear All Dockets</span>
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="tactical-btn text-xs font-mono flex items-center space-x-1.5 shadow-xs cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>+ Register New Docket</span>
          </button>
        </div>
      </div>

      {/* 4-Column Kanban Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 select-none">
        {columns.map(col => {
          const colCases = cases.filter(c => c.status === col.key);
          return (
            <div
              key={col.key}
              className="bg-slate-50/60 rounded-xl border border-slate-200/90 flex flex-col max-h-[calc(100vh-210px)] overflow-hidden shadow-xs"
            >
              {/* Column Header */}
              <div className={`px-4 py-3 border-b border-slate-200 border-t-2 ${col.color} bg-white flex items-center justify-between`}>
                <span className="font-extrabold text-xs font-mono text-slate-900 tracking-tight">{col.label}</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-slate-100 text-slate-700 font-bold border border-slate-200">
                  {colCases.length}
                </span>
              </div>

              {/* Cards Container */}
              <div className="p-3 overflow-y-auto space-y-3 flex-1 tactical-scrollbar">
                {colCases.map((c) => (
                  <div
                    key={c.id}
                    className="p-3.5 rounded-xl bg-white border border-slate-200/90 hover:border-sky-400 hover:shadow-sm hover:-translate-y-0.5 transition-all space-y-2.5 shadow-2xs group"
                  >
                    <div className="flex items-center justify-between text-[10px] font-mono">
                      <span className="text-sky-700 font-extrabold">{c.case_no}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
                        c.severity === 'CRITICAL' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                        c.severity === 'HIGH' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                        'bg-slate-100 text-slate-700 border border-slate-200'
                      }`}>
                        {c.severity}
                      </span>
                    </div>

                    <div className="text-xs font-extrabold text-slate-900 leading-snug">
                      {c.title}
                    </div>

                    <div className="text-[11px] font-mono text-slate-500 space-y-1 pt-1.5 border-t border-slate-100">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-400 text-[10px] uppercase font-bold">Lead Suspect:</span>
                        <span className="text-slate-900 font-bold">{c.lead_suspect || 'Vikram Sinha'}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-400 text-[10px] uppercase font-bold">Assigned:</span>
                        <span className="text-sky-700 font-semibold">{c.assigned_officer}</span>
                      </div>
                    </div>

                    {/* Footer / Move arrows */}
                    <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[10px] font-mono">
                      <div className="flex items-center space-x-2 text-slate-500">
                        <span className="flex items-center font-semibold"><Users className="w-3 h-3 mr-1 text-sky-600" /> {c.suspect_count || 3}</span>
                        <span className="flex items-center font-semibold"><ShieldCheck className="w-3 h-3 mr-1 text-emerald-600" /> {c.evidence_count || 4}</span>
                      </div>

                      <div className="flex items-center space-x-1">
                        {col.key !== 'NEW' && (
                          <button
                            onClick={() => handleMove(c.id, c.status, 'backward')}
                            className="p-1 rounded bg-slate-50 hover:bg-slate-100 text-slate-600 hover:text-slate-900 transition border border-slate-200 active:scale-95 shadow-2xs"
                            title="Move Backward"
                          >
                            <ArrowLeft className="w-3 h-3" />
                          </button>
                        )}
                        {col.key !== 'CHARGESHEET_READY' && (
                          <button
                            onClick={() => handleMove(c.id, c.status, 'forward')}
                            className="p-1 rounded bg-slate-50 hover:bg-sky-50 hover:text-sky-700 text-slate-600 transition border border-slate-200 active:scale-95 shadow-2xs cursor-pointer"
                            title="Advance Stage"
                          >
                            <ArrowRight className="w-3 h-3" />
                          </button>
                        )}
                        <button
                          onClick={(e) => handleDeleteCase(c.id, e)}
                          className="p-1 rounded bg-slate-50 hover:bg-rose-50 hover:text-rose-600 text-slate-400 hover:border-rose-300 transition border border-slate-200 active:scale-95 shadow-2xs cursor-pointer"
                          title="Delete Case Docket"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Add New Case Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 max-w-md w-full space-y-4 shadow-xl animate-fade-in">
            <h2 className="text-base font-extrabold text-slate-900 flex items-center space-x-2">
              <Briefcase className="w-4 h-4 text-sky-600" />
              <span>Register New Investigation Docket</span>
            </h2>

            <div className="space-y-3 text-xs font-mono">
              <div>
                <label className="text-slate-600 font-bold block mb-1">CASE / INCIDENT TITLE:</label>
                <input
                  type="text"
                  placeholder="e.g. Armed Extortion Cell at Bankmore PS"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="tactical-input w-full text-xs"
                />
              </div>

              <div>
                <label className="text-slate-600 font-bold block mb-1">CRIME CATEGORY:</label>
                <select
                  value={newCrimeType}
                  onChange={(e) => setNewCrimeType(e.target.value)}
                  className="tactical-input w-full text-xs"
                >
                  <option value="EXTORTION">EXTORTION (Sec 384 IPC)</option>
                  <option value="WOMEN_SAFETY">WOMEN SAFETY (Sec 376/366A IPC)</option>
                  <option value="HAWALA_FRAUD">HAWALA & FRAUD (Sec 420 IPC)</option>
                  <option value="NARCOTICS">NARCOTICS (NDPS Act)</option>
                  <option value="CYBERCRIME">CYBERCRIME (IT Act Sec 66D)</option>
                </select>
              </div>

              <div>
                <label className="text-slate-600 font-bold block mb-1">INVESTIGATING OFFICER:</label>
                <input
                  type="text"
                  value={newOfficer}
                  onChange={(e) => setNewOfficer(e.target.value)}
                  className="tactical-input w-full text-xs"
                />
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
              <button
                onClick={() => setShowAddModal(false)}
                className="tactical-btn-secondary text-xs"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateCase}
                className="tactical-btn text-xs font-bold shadow-xs"
              >
                Create Docket
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
