import React, { useEffect, useState } from 'react';
import { Briefcase, Users, Network, AlertTriangle } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const data = [
  { name: 'Jan', cases: 40 }, { name: 'Feb', cases: 30 }, { name: 'Mar', cases: 55 },
  { name: 'Apr', cases: 45 }, { name: 'May', cases: 70 }, { name: 'Jun', cases: 65 },
  { name: 'Jul', cases: 85 }, { name: 'Aug', cases: 90 }, { name: 'Sep', cases: 110 },
  { name: 'Oct', cases: 100 }, { name: 'Nov', cases: 130 }, { name: 'Dec', cases: 150 },
];

const pieData = [
  { name: 'CRITICAL', value: 15, color: '#ef4444' },
  { name: 'HIGH', value: 30, color: '#f97316' },
  { name: 'MEDIUM', value: 40, color: '#f59e0b' },
  { name: 'LOW', value: 15, color: '#10b981' },
];

export default function Dashboard() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return <div className="flex h-full items-center justify-center text-cyan-500 animate-pulse">Initializing Sentinel Dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight">Tactical Dashboard</h1>
        <p className="text-slate-400">System overview and threat intelligence summary.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Cases', value: '1,248', icon: Briefcase, color: 'text-cyan-500', bg: 'bg-cyan-500/10', change: '+12%' },
          { label: 'Total Suspects', value: '4,892', icon: Users, color: 'text-amber-500', bg: 'bg-amber-500/10', change: '+5%' },
          { label: 'Active Networks', value: '342', icon: Network, color: 'text-emerald-500', bg: 'bg-emerald-500/10', change: '+2%' },
          { label: 'High-Risk Alerts', value: '18', icon: AlertTriangle, color: 'text-red-500', bg: 'bg-red-500/10', change: '+8%', pulse: true },
        ].map((kpi, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col relative overflow-hidden group hover:border-slate-700 transition-colors">
            <div className="flex justify-between items-start mb-4">
              <div className={`p-3 rounded-lg ${kpi.bg} ${kpi.pulse ? 'animate-pulse' : ''}`}>
                <kpi.icon className={`w-6 h-6 ${kpi.color}`} />
              </div>
              <span className="text-xs font-semibold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full">{kpi.change}</span>
            </div>
            <div>
              <h3 className="text-slate-400 text-sm font-medium">{kpi.label}</h3>
              <p className="text-3xl font-bold text-white mt-1">{kpi.value}</p>
            </div>
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:opacity-10 transition-opacity">
              <kpi.icon className="w-32 h-32" />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-white mb-4">Top 5 Kingpins</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-slate-400 uppercase bg-slate-800/50">
                <tr>
                  <th className="px-4 py-3 rounded-l-lg">Rank</th>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Risk Score</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 rounded-r-lg">Centrality</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { rank: 1, name: 'Vikram "Bhai" Sharma', score: 98, status: 'AT LARGE', cent: 0.94 },
                  { rank: 2, name: 'Abdul Rahman', score: 92, status: 'WANTED', cent: 0.88 },
                  { rank: 3, name: 'Unknown (Ghost)', score: 89, status: 'UNIDENTIFIED', cent: 0.85 },
                  { rank: 4, name: 'Jimmy D.', score: 85, status: 'ARRESTED', cent: 0.79 },
                  { rank: 5, name: 'Ravi Teja', score: 81, status: 'UNDER SURVEILLANCE', cent: 0.72 },
                ].map((row, i) => (
                  <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors cursor-pointer">
                    <td className="px-4 py-3 font-medium text-slate-300">#{row.rank}</td>
                    <td className="px-4 py-3 text-white">{row.name}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className={row.score > 90 ? 'text-red-400' : 'text-amber-400'}>{row.score}</span>
                        <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div className={`h-full ${row.score > 90 ? 'bg-red-500' : 'bg-amber-500'}`} style={{ width: `${row.score}%` }}></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold tracking-wider ${row.status === 'ARRESTED' ? 'bg-emerald-500/20 text-emerald-400' : row.status === 'AT LARGE' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'}`}>
                        {row.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-cyan-400">{row.cent.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-white mb-4">Threat Level Distribution</h2>
          <div className="h-[250px] w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={2} dataKey="value" stroke="none">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }} itemStyle={{ color: '#f8fafc' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap justify-center gap-4 mt-2">
            {pieData.map((entry, idx) => (
              <div key={idx} className="flex items-center gap-2 text-xs text-slate-300 font-medium">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }}></div>
                {entry.name}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-white mb-4">Case Volume (12M)</h2>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorCases" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} tickLine={false} axisLine={false} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }} />
                <Area type="monotone" dataKey="cases" stroke="#06b6d4" strokeWidth={2} fillOpacity={1} fill="url(#colorCases)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col">
          <h2 className="text-lg font-semibold text-white mb-4">Recent Activity</h2>
          <div className="flex-1 overflow-y-auto pr-2 space-y-4">
            {[
              { title: 'New FIR Ingested', desc: 'FIR-2023-049 processed. 12 entities extracted.', time: '10m ago', type: 'info', color: 'text-cyan-400', bg: 'bg-cyan-500/20' },
              { title: 'Structuring Alert', desc: 'Suspicious transactions detected in A/C ending 4921.', time: '1h ago', type: 'warning', color: 'text-amber-400', bg: 'bg-amber-500/20' },
              { title: 'High-Risk Node Flagged', desc: 'Unknown Phone +91-98XXX-XX123 centrality score spiked.', time: '3h ago', type: 'danger', color: 'text-red-400', bg: 'bg-red-500/20' },
              { title: 'Batch Upload Complete', desc: '5 CDR files successfully ingested.', time: '5h ago', type: 'success', color: 'text-emerald-400', bg: 'bg-emerald-500/20' },
              { title: 'User Login', desc: 'Investigator A. logged in from 192.168.1.45', time: '1d ago', type: 'default', color: 'text-slate-400', bg: 'bg-slate-700/50' },
            ].map((activity, i) => (
              <div key={i} className="flex gap-3 items-start">
                <div className={`w-2 h-2 mt-2 rounded-full flex-shrink-0 ${activity.bg.replace('/20', '')}`}></div>
                <div>
                  <h4 className="text-sm font-medium text-slate-200">{activity.title}</h4>
                  <p className="text-xs text-slate-400 mt-0.5">{activity.desc}</p>
                  <span className="text-[10px] text-slate-500 font-medium mt-1 inline-block">{activity.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
