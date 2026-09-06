import React from 'react';
import { Shield, Users, Activity, HardDrive, Cpu, TerminalSquare } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area } from 'recharts';

const perfData = Array.from({ length: 24 }).map((_, i) => ({ time: i, ms: 45 + Math.random() * 30 }));

export default function AdminPanel() {
  return (
    <div className="space-y-6 h-full flex flex-col">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight">System Administration</h1>
        <p className="text-slate-400">Access control, audit logs, and system health.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Database Size', value: '42.8 GB', icon: HardDrive, color: 'text-cyan-400' },
          { label: 'Total Nodes', value: '1,204', icon: Activity, color: 'text-emerald-400' },
          { label: 'Total Edges', value: '3,842', icon: Activity, color: 'text-emerald-400' },
          { label: 'API Uptime', value: '99.99%', icon: Cpu, color: 'text-cyan-400' },
        ].map((stat, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className={`p-3 rounded-lg bg-slate-950 border border-slate-800 ${stat.color}`}>
              <stat.icon size={20} />
            </div>
            <div>
              <div className="text-xs text-slate-400 font-medium">{stat.label}</div>
              <div className="text-xl font-bold text-white">{stat.value}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 min-h-0">
        <div className="flex flex-col gap-6 min-h-0">
          <div className="bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden flex-[2]">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
              <h2 className="text-sm font-semibold text-white flex items-center gap-2"><Users size={16} /> User Management</h2>
              <button className="text-xs bg-cyan-600 hover:bg-cyan-500 text-white px-3 py-1.5 rounded transition-colors">Add User</button>
            </div>
            <div className="flex-1 overflow-auto">
              <table className="w-full text-sm text-left whitespace-nowrap">
                <thead className="text-xs text-slate-400 uppercase bg-slate-800/50">
                  <tr>
                    <th className="px-4 py-3">User</th>
                    <th className="px-4 py-3">Role</th>
                    <th className="px-4 py-3">Last Login</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {[
                    { u: 'admin_root', r: 'Admin', l: 'Now', s: 'ACTIVE', c: 'red' },
                    { u: 'investigator_a', r: 'Analyst', l: '2 hrs ago', s: 'ACTIVE', c: 'amber' },
                    { u: 'officer_01', r: 'Viewer', l: '1 day ago', s: 'INACTIVE', c: 'slate' }
                  ].map((row, i) => (
                    <tr key={i} className="hover:bg-slate-800/30">
                      <td className="px-4 py-3 text-slate-200 font-medium">{row.u}</td>
                      <td className="px-4 py-3"><span className={`text-[10px] px-2 py-0.5 rounded font-bold tracking-wider bg-${row.c}-500/20 text-${row.c}-400`}>{row.r}</span></td>
                      <td className="px-4 py-3 text-slate-400 text-xs">{row.l}</td>
                      <td className="px-4 py-3"><span className="text-[10px] text-emerald-400">{row.s}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex-1 flex flex-col">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2 mb-4"><Shield size={16} /> Ledger Integrity</h2>
            <div className="flex-1 flex flex-col justify-center items-center text-center">
              <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center border border-emerald-500/20 mb-4">
                <Shield size={32} className="text-emerald-400" />
              </div>
              <h3 className="text-emerald-400 font-bold mb-1">CHAIN VALIDATED</h3>
              <p className="text-xs text-slate-400 font-mono mb-4">Last checked: 2023-10-24 16:00:00 UTC</p>
              <button className="bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium px-4 py-2 rounded transition-colors border border-slate-700">Run Integrity Check</button>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-6 min-h-0">
          <div className="bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden flex-[2]">
            <div className="p-4 border-b border-slate-800">
              <h2 className="text-sm font-semibold text-white flex items-center gap-2"><TerminalSquare size={16} /> Audit Trail</h2>
            </div>
            <div className="flex-1 overflow-auto bg-slate-950 p-4 font-mono text-[10px] space-y-1">
              {[
                '[16:45:12] admin_root EXPORTED dossier_P-89241.pdf (IP: 192.168.1.5)',
                '[16:30:05] investigator_a QUERIED /api/graph/expand/P-89241 (IP: 192.168.1.45)',
                '[15:12:44] SYSTEM INGESTED FIR_049.pdf (Hash: e3b0c442...)',
                '[14:05:22] officer_01 FAILED_LOGIN (IP: 10.0.0.52)'
              ].map((log, i) => (
                <div key={i} className="text-slate-400">
                  <span className="text-cyan-600 mr-2">&gt;</span>
                  {log.includes('EXPORTED') ? <span className="text-amber-400">{log}</span> : 
                   log.includes('FAILED') ? <span className="text-red-400">{log}</span> :
                   log}
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex-1 flex flex-col">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2 mb-4"><Activity size={16} /> API Response Times (24h)</h2>
            <div className="flex-1 w-full relative">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={perfData}>
                  <Area type="monotone" dataKey="ms" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.1} strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
              <div className="absolute top-0 right-0 text-xs font-mono text-cyan-400">Avg: 54ms</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
