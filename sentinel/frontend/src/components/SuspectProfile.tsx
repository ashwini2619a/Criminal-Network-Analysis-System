import React from 'react';
import { useParams } from 'react-router-dom';
import { User, Phone, Banknote, ShieldAlert, FileText, Activity, MapPin } from 'lucide-react';

export default function SuspectProfile() {
  const { id } = useParams();

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-red-500/5 rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
        
        <div className="flex flex-col md:flex-row gap-6 items-start md:items-center">
          <div className="w-24 h-24 bg-slate-800 rounded-2xl flex items-center justify-center border border-slate-700 shadow-xl shrink-0">
            <User className="w-12 h-12 text-slate-500" />
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-white tracking-tight">Vikram Sharma</h1>
              <span className="bg-red-500/20 text-red-400 text-xs font-bold px-2.5 py-1 rounded-full border border-red-500/20 tracking-wider">AT LARGE</span>
            </div>
            
            <div className="flex flex-wrap items-center gap-2 mb-4">
              <span className="text-xs text-slate-400 uppercase tracking-wider">Aliases:</span>
              <span className="bg-slate-800 text-slate-300 text-xs px-2 py-0.5 rounded-md">Vicky</span>
              <span className="bg-slate-800 text-slate-300 text-xs px-2 py-0.5 rounded-md">Bhai</span>
              <span className="bg-slate-800 text-slate-300 text-xs px-2 py-0.5 rounded-md">VS-77</span>
            </div>

            <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-400">
              <div className="flex items-center gap-1.5"><ShieldAlert size={14} className="text-cyan-500" /> <span>CRN: IND-2023-88942</span></div>
              <div className="flex items-center gap-1.5"><User size={14} className="text-cyan-500" /> <span>Age: 42, Male</span></div>
              <div className="flex items-center gap-1.5"><MapPin size={14} className="text-cyan-500" /> <span>LKA: Ranchi, JH</span></div>
            </div>
          </div>

          <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex flex-col items-center justify-center min-w-[140px]">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Risk Score</span>
            <span className="text-4xl font-bold text-red-500 drop-shadow-[0_0_8px_rgba(239,68,68,0.5)]">98</span>
            <div className="w-full bg-slate-800 h-1 mt-2 rounded-full overflow-hidden">
              <div className="bg-red-500 h-full w-[98%]"></div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-white mb-4 border-b border-slate-800 pb-2">Network Influence</h2>
          <div className="space-y-4">
            {[
              { label: 'Degree Centrality', value: 0.92, desc: 'High number of direct contacts', color: 'bg-red-500' },
              { label: 'Betweenness', value: 0.98, desc: 'Critical broker between groups', color: 'bg-red-500' },
              { label: 'Closeness', value: 0.75, desc: 'Quick access to whole network', color: 'bg-amber-500' },
              { label: 'Eigenvector', value: 0.88, desc: 'Connected to other key figures', color: 'bg-red-500' },
              { label: 'Shadow Score', value: 0.95, desc: 'Hidden influence detected', color: 'bg-purple-500' },
            ].map((metric, i) => (
              <div key={i}>
                <div className="flex justify-between items-end mb-1">
                  <span className="text-sm font-medium text-slate-300">{metric.label}</span>
                  <span className="text-xs font-mono text-cyan-400">{metric.value.toFixed(2)}</span>
                </div>
                <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden mb-1 border border-slate-800">
                  <div className={`h-full ${metric.color}`} style={{ width: `${metric.value * 100}%` }}></div>
                </div>
                <p className="text-[10px] text-slate-500">{metric.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden">
           <div className="flex border-b border-slate-800 overflow-x-auto hide-scrollbar">
             {[
               { icon: Phone, label: 'Phones (4)' },
               { icon: Banknote, label: 'Accounts (2)' },
               { icon: User, label: 'Associates (14)' },
               { icon: FileText, label: 'FIRs (3)' }
             ].map((tab, i) => (
               <button key={i} className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${i === 0 ? 'border-cyan-500 text-cyan-400 bg-slate-800/30' : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/10'}`}>
                 <tab.icon size={16} /> {tab.label}
               </button>
             ))}
           </div>
           
           <div className="p-5 flex-1 overflow-y-auto">
             <div className="space-y-3">
               {[
                 { num: '+91-98765-43210', provider: 'Jio', status: 'ACTIVE', imei: '354892019384752', lastActive: '2 hrs ago' },
                 { num: '+91-87654-32109', provider: 'Airtel', status: 'BURNER SUSPECTED', imei: '869302194857211', lastActive: '1 day ago' },
                 { num: '+91-76543-21098', provider: 'Vi', status: 'INACTIVE', imei: '358291038475612', lastActive: '2 months ago' },
               ].map((phone, i) => (
                 <div key={i} className="bg-slate-950 border border-slate-800 rounded-lg p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 group hover:border-slate-700 transition-colors">
                   <div className="flex items-center gap-3">
                     <div className="w-10 h-10 rounded-full bg-slate-900 flex items-center justify-center border border-slate-800">
                       <Phone size={18} className="text-slate-400" />
                     </div>
                     <div>
                       <h4 className="text-white font-mono font-medium tracking-wider">{phone.num}</h4>
                       <div className="flex gap-2 text-xs mt-1">
                         <span className="text-slate-400">{phone.provider}</span>
                         <span className="text-slate-600">•</span>
                         <span className="text-slate-500 font-mono">IMEI: {phone.imei}</span>
                       </div>
                     </div>
                   </div>
                   <div className="flex flex-col sm:items-end">
                     <span className={`text-[10px] px-2 py-0.5 rounded bg-slate-900 border font-bold tracking-wider mb-1 ${phone.status === 'ACTIVE' ? 'text-emerald-400 border-emerald-900' : phone.status.includes('BURNER') ? 'text-red-400 border-red-900' : 'text-slate-400 border-slate-700'}`}>{phone.status}</span>
                     <span className="text-[10px] text-slate-500">Last active: {phone.lastActive}</span>
                   </div>
                 </div>
               ))}
             </div>
           </div>
        </div>

        <div className="lg:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-white mb-6 border-b border-slate-800 pb-2">Recent Activity Timeline</h2>
          <div className="relative pl-6 border-l border-slate-800 space-y-6">
            {[
              { date: 'Oct 24, 2023 - 14:30', title: 'High-Value Transfer', desc: '₹5,00,000 transferred to Ramesh K. (Suspected Hawala Node)', icon: Banknote, color: 'text-amber-500', bg: 'bg-amber-950' },
              { date: 'Oct 22, 2023 - 02:15', title: 'Co-location Alert', desc: 'Phone #2 detected at same tower as Jimmy D. in South Delhi.', icon: MapPin, color: 'text-red-500', bg: 'bg-red-950' },
              { date: 'Oct 18, 2023 - 18:45', title: 'Burner Phone Activated', desc: 'New SIM (+91-87654-32109) activated on known IMEI.', icon: Phone, color: 'text-cyan-500', bg: 'bg-cyan-950' },
              { date: 'Sep 12, 2023', title: 'FIR Filed', desc: 'Named as primary suspect in FIR-2023-049 (Extortion).', icon: FileText, color: 'text-slate-400', bg: 'bg-slate-800' },
            ].map((event, i) => (
              <div key={i} className="relative">
                <div className={`absolute -left-9 top-1 w-6 h-6 rounded-full flex items-center justify-center border border-slate-700 ${event.bg}`}>
                  <event.icon size={12} className={event.color} />
                </div>
                <div>
                  <span className="text-[10px] font-medium text-cyan-500 uppercase tracking-wider">{event.date}</span>
                  <h4 className="text-sm font-medium text-white mt-0.5">{event.title}</h4>
                  <p className="text-xs text-slate-400 mt-1">{event.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
