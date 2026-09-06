import React from 'react';
import { ResponsiveContainer, BarChart, Bar, Cell, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { AlertOctagon, Repeat, TrendingUp, ShieldAlert, DollarSign } from 'lucide-react';

const txData = [
  { date: 'Oct 1', amount: 15000 }, { date: 'Oct 2', amount: 48000 },
  { date: 'Oct 3', amount: 49500 }, { date: 'Oct 4', amount: 12000 },
  { date: 'Oct 5', amount: 48500 }, { date: 'Oct 6', amount: 49000 },
  { date: 'Oct 7', amount: 20000 }, { date: 'Oct 8', amount: 150000 },
];

export default function FinancialFlow() {
  return (
    <div className="space-y-6 h-full flex flex-col">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight">Mule Layering & Smurfing AML Analysis (PMLA 2002)</h1>
        <p className="text-slate-400">Multi-hop mule layering, circular bank transfers, and structuring detection (PMLA 2002 / FIU-IND).</p>
      </header>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 min-h-[300px] relative flex flex-col justify-between overflow-hidden">
        <h2 className="text-sm font-semibold text-white mb-4 absolute top-5 left-5 z-10">High-Risk Transfer Flow</h2>
        
        <div className="flex-1 w-full flex items-center justify-center p-8 mt-6">
           <svg className="w-full h-full max-h-[200px]" viewBox="0 0 800 200" preserveAspectRatio="xMidYMid meet">
             <path d="M 150,100 C 250,100 250,50 350,50" fill="none" stroke="#ef4444" strokeWidth="8" strokeOpacity="0.4" className="animate-pulse" />
             <path d="M 150,100 C 250,100 250,150 350,150" fill="none" stroke="#f59e0b" strokeWidth="4" strokeOpacity="0.4" />
             <path d="M 450,50 C 550,50 550,100 650,100" fill="none" stroke="#ef4444" strokeWidth="6" strokeOpacity="0.4" />
             <path d="M 450,150 C 550,150 550,100 650,100" fill="none" stroke="#f59e0b" strokeWidth="4" strokeOpacity="0.4" />
             
             <text x="250" y="60" fill="#cbd5e1" fontSize="12" textAnchor="middle" className="font-mono">₹5.0L</text>
             <text x="250" y="145" fill="#cbd5e1" fontSize="12" textAnchor="middle" className="font-mono">₹1.2L</text>
             
             <g transform="translate(50, 75)">
               <rect width="100" height="50" rx="8" fill="#1e293b" stroke="#334155" strokeWidth="2" />
               <text x="50" y="25" fill="#f8fafc" fontSize="14" textAnchor="middle" fontWeight="bold">Shell Corp A</text>
               <text x="50" y="40" fill="#94a3b8" fontSize="10" textAnchor="middle">Acct: ...4921</text>
             </g>
             
             <g transform="translate(350, 25)">
               <rect width="100" height="50" rx="8" fill="#450a0a" stroke="#ef4444" strokeWidth="2" />
               <text x="50" y="25" fill="#f8fafc" fontSize="14" textAnchor="middle" fontWeight="bold">Vikram S.</text>
               <text x="50" y="40" fill="#94a3b8" fontSize="10" textAnchor="middle">Acct: ...8822</text>
             </g>
             
             <g transform="translate(350, 125)">
               <rect width="100" height="50" rx="8" fill="#1e293b" stroke="#f59e0b" strokeWidth="2" />
               <text x="50" y="25" fill="#f8fafc" fontSize="14" textAnchor="middle" fontWeight="bold">Ramesh K.</text>
               <text x="50" y="40" fill="#94a3b8" fontSize="10" textAnchor="middle">Acct: ...1123</text>
             </g>
             
             <g transform="translate(650, 75)">
               <rect width="100" height="50" rx="8" fill="#1e293b" stroke="#334155" strokeWidth="2" />
               <text x="50" y="25" fill="#f8fafc" fontSize="14" textAnchor="middle" fontWeight="bold">Overseas LLC</text>
               <text x="50" y="40" fill="#94a3b8" fontSize="10" textAnchor="middle">Dubai</text>
             </g>
           </svg>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 min-h-0">
        <div className="flex flex-col gap-6 min-h-0">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shrink-0">
             <div className="flex justify-between items-center mb-4">
               <h2 className="text-sm font-semibold text-white flex items-center gap-2"><TrendingUp size={16} /> Transaction Timeline</h2>
               <span className="text-[10px] bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded font-bold uppercase">Smurfing Suspected</span>
             </div>
             <div className="h-[180px] w-full">
               <ResponsiveContainer width="100%" height="100%">
                 <BarChart data={txData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                   <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                   <XAxis dataKey="date" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 10 }} tickLine={false} axisLine={false} />
                   <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 10 }} tickLine={false} axisLine={false} />
                   <Tooltip cursor={{ fill: '#1e293b' }} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc', fontSize: '12px' }} />
                   <Bar dataKey="amount">
                     {txData.map((entry, index) => (
                       <Cell key={`cell-${index}`} fill={entry.amount >= 48000 && entry.amount < 50000 ? '#ef4444' : '#06b6d4'} />
                     ))}
                   </Bar>
                 </BarChart>
               </ResponsiveContainer>
             </div>
          </div>
          
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex-1 overflow-hidden flex flex-col">
            <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2"><Repeat size={16} /> Detected Multi-Hop Mule Cycles (PMLA)</h2>
            <div className="flex-1 overflow-y-auto space-y-3">
              {[
                { risk: 'CRITICAL', entities: ['Ranchi Node', 'Kolkata Hub', 'Dubai Acct', 'Ranchi Node'], amount: '₹12.5L', days: 3 },
                { risk: 'HIGH', entities: ['Vikram S.', 'Shell Corp B', 'NGO Acc', 'Vikram S.'], amount: '₹8.0L', days: 7 }
              ].map((cycle, i) => (
                <div key={i} className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="flex justify-between items-center mb-3">
                    <span className={`text-[10px] px-2 py-0.5 rounded font-bold tracking-wider ${cycle.risk === 'CRITICAL' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'}`}>{cycle.risk} CYCLE</span>
                    <span className="text-sm font-mono text-cyan-400">{cycle.amount}</span>
                  </div>
                  <div className="flex items-center flex-wrap gap-2 text-xs text-slate-300">
                    {cycle.entities.map((ent, idx) => (
                      <React.Fragment key={idx}>
                        <span className="bg-slate-800 px-2 py-1 rounded">{ent}</span>
                        {idx < cycle.entities.length - 1 && <span className="text-slate-500">→</span>}
                      </React.Fragment>
                    ))}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-2 text-right">Completed in {cycle.days} days</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden">
          <div className="p-5 border-b border-slate-800">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2"><ShieldAlert size={16} /> Structuring (Smurfing) Alerts</h2>
            <p className="text-xs text-slate-400 mt-1">Transactions just below reporting threshold (₹50,000)</p>
          </div>
          <div className="flex-1 overflow-auto">
            <table className="w-full text-sm text-left whitespace-nowrap">
              <thead className="text-xs text-slate-400 uppercase bg-slate-800/50 sticky top-0">
                <tr>
                  <th className="px-5 py-3">Account</th>
                  <th className="px-5 py-3">Amount</th>
                  <th className="px-5 py-3">Date</th>
                  <th className="px-5 py-3 text-right">Similar Count</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {[
                  { acct: 'HDFC ...4921', amt: 49500, date: 'Oct 03', count: 4 },
                  { acct: 'HDFC ...4921', amt: 49000, date: 'Oct 06', count: 4 },
                  { acct: 'HDFC ...4921', amt: 48500, date: 'Oct 05', count: 4 },
                  { acct: 'SBI ...1123', amt: 49900, date: 'Oct 01', count: 2 },
                  { acct: 'ICICI ...8822', amt: 48000, date: 'Sep 28', count: 1 },
                ].map((row, i) => (
                  <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-5 py-3 font-medium text-slate-300 flex items-center gap-2">
                      <DollarSign size={14} className="text-slate-500" /> {row.acct}
                    </td>
                    <td className="px-5 py-3 font-mono text-red-400">₹{row.amt.toLocaleString()}</td>
                    <td className="px-5 py-3 text-slate-400">{row.date}</td>
                    <td className="px-5 py-3 text-right text-amber-400 font-bold">{row.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
