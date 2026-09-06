import React from 'react';
import { Search, FileText, Download, QrCode, ShieldCheck, User } from 'lucide-react';

export default function DossierGenerator() {
  return (
    <div className="space-y-6 h-full flex flex-col">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight">Court-Ready Dossier</h1>
        <p className="text-slate-400">Generate tamper-evident, Section 63 BSA / 65B IEA certified evidentiary dossiers.</p>
      </header>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
        <span className="text-sm font-medium text-slate-400 uppercase tracking-wider">Target Subject:</span>
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
          <input type="text" defaultValue="Vikram Sharma (P-89241)" className="w-full bg-slate-950 border border-slate-700 text-sm rounded-lg pl-9 pr-3 py-2 text-white focus:outline-none focus:border-cyan-500" />
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6 flex-1 min-h-0">
        <div className="flex-[2] bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden">
           <div className="p-4 border-b border-slate-800 bg-slate-800/30 flex justify-between items-center">
             <h2 className="font-semibold text-white">Report Preview</h2>
             <span className="text-xs font-mono text-slate-400">Page 1 of 5</span>
           </div>
           
           <div className="flex-1 overflow-y-auto p-8 bg-slate-950 flex justify-center">
             <div className="bg-white w-full max-w-[800px] h-[1000px] shadow-2xl p-12 relative">
               <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.03]">
                 <ShieldCheck size={400} className="text-slate-900" />
               </div>
               
               <div className="text-center border-b-2 border-slate-800 pb-6 mb-8">
                 <h1 className="text-3xl font-serif font-bold text-slate-900 uppercase tracking-widest">Sentinel Intelligence Report</h1>
                 <p className="text-slate-600 mt-2 font-mono text-sm">CLASSIFIED // EVIDENTIARY USE ONLY</p>
               </div>

               <div className="flex gap-8 mb-8">
                 <div className="w-32 h-40 bg-slate-200 border-2 border-slate-300 flex items-center justify-center">
                   <User size={48} className="text-slate-400" />
                 </div>
                 <div className="flex-1 text-slate-900 font-serif">
                   <table className="w-full text-sm">
                     <tbody>
                       <tr className="border-b border-slate-200"><td className="py-2 font-bold w-1/3">Subject Name:</td><td className="py-2">Vikram Sharma</td></tr>
                       <tr className="border-b border-slate-200"><td className="py-2 font-bold">Aliases:</td><td className="py-2">Vicky, Bhai</td></tr>
                       <tr className="border-b border-slate-200"><td className="py-2 font-bold">System ID:</td><td className="py-2 font-mono">P-89241</td></tr>
                       <tr className="border-b border-slate-200"><td className="py-2 font-bold">Risk Assessment:</td><td className="py-2 text-red-600 font-bold">CRITICAL (98/100)</td></tr>
                       <tr className="border-b border-slate-200"><td className="py-2 font-bold">Date Generated:</td><td className="py-2 font-mono">2023-10-24 16:45 UTC</td></tr>
                     </tbody>
                   </table>
                 </div>
               </div>

               <div className="text-slate-900">
                 <h3 className="font-bold text-lg border-b border-slate-300 pb-1 mb-3 uppercase">Executive Summary</h3>
                 <p className="text-sm leading-relaxed text-slate-700 text-justify">
                   Subject identified as central node in Ranchi syndicate operations. Network centrality analysis indicates 98th percentile betweenness, acting as primary broker between shell corporate entities and ground operators. Analysis of CDRs and financial flows corroborates structured layering of funds consistent with money laundering typologies.
                 </p>
               </div>
             </div>
           </div>
        </div>

        <div className="flex-1 flex flex-col gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h2 className="text-sm font-semibold text-white mb-4">Export Options</h2>
            <div className="space-y-4">
               <div>
                 <label className="text-xs text-slate-400 block mb-2">Format</label>
                 <select className="w-full bg-slate-950 border border-slate-700 text-sm rounded-lg px-3 py-2 text-white">
                   <option>PDF Document (.pdf)</option>
                   <option>Raw Data Export (.json)</option>
                   <option>Spreadsheet (.xlsx)</option>
                 </select>
               </div>
               <button className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-medium py-3 rounded-lg transition-colors flex items-center justify-center gap-2">
                 <Download size={18} /> Generate & Sign Dossier
               </button>
            </div>
            
            <div className="mt-6 p-4 border border-emerald-900 bg-emerald-950/30 rounded-lg flex items-start gap-4">
               <div className="bg-white p-1 rounded-sm"><QrCode size={40} className="text-slate-900" /></div>
               <div>
                 <h4 className="text-xs font-bold text-emerald-400 uppercase">Section 63 BSA Certification</h4>
                 <p className="text-[10px] text-slate-400 mt-1">Cryptographic SHA-256 seal and QR verification compliant with Bharatiya Sakshya Adhiniyam, 2023.</p>
               </div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl flex-1 flex flex-col overflow-hidden">
            <div className="p-4 border-b border-slate-800">
              <h2 className="text-sm font-semibold text-white">Evidence Vault</h2>
            </div>
            <div className="flex-1 overflow-auto">
              <table className="w-full text-sm text-left whitespace-nowrap">
                <thead className="text-[10px] text-slate-400 uppercase bg-slate-800/50">
                  <tr>
                    <th className="px-4 py-2">File</th>
                    <th className="px-4 py-2">SHA-256 Hash</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {[
                    { name: 'FIR_049.pdf', hash: 'e3b0c442...b855' },
                    { name: 'CDR_Log_Q3.csv', hash: '8f434346...c321' },
                    { name: 'Bank_Stmt.xlsx', hash: 'a1b2c3d4...e5f6' }
                  ].map((f, i) => (
                    <tr key={i} className="hover:bg-slate-800/30">
                      <td className="px-4 py-3 text-slate-300 flex items-center gap-2 text-xs"><FileText size={12} className="text-cyan-500"/> {f.name}</td>
                      <td className="px-4 py-3 font-mono text-[10px] text-emerald-400 flex items-center gap-1"><ShieldCheck size={10} /> {f.hash}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
