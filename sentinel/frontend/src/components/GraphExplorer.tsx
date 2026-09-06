import React, { useEffect, useRef, useState } from 'react';
import { Search, Filter, Layers, ZoomIn, ZoomOut, Maximize, Share2, Download, Info, Network } from 'lucide-react';

export default function GraphExplorer() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [panelOpen, setPanelOpen] = useState(false);

  useEffect(() => {
    // Placeholder for GraphEngine initialization
  }, []);

  return (
    <div className="flex h-full space-x-4">
      <div className="w-72 bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden shrink-0">
        <div className="p-4 border-b border-slate-800">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Filter size={18} /> Analytics Filters
          </h2>
        </div>
        
        <div className="p-4 flex-1 overflow-y-auto space-y-6">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">Search Node</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
              <input type="text" placeholder="Name, ID, Phone..." className="w-full bg-slate-950 border border-slate-700 text-sm rounded-lg pl-9 pr-3 py-2 text-white focus:outline-none focus:border-cyan-500" />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">Entity Types</label>
            <div className="space-y-2">
              {['Person', 'Phone Number', 'Bank Account', 'Location', 'Organization'].map(type => (
                <label key={type} className="flex items-center gap-3 text-sm text-slate-300 hover:text-white cursor-pointer">
                  <input type="checkbox" defaultChecked className="form-checkbox bg-slate-950 border-slate-700 text-cyan-500 rounded focus:ring-0 focus:ring-offset-0 w-4 h-4" />
                  {type}
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex justify-between block">
              <span>Risk Threshold</span>
              <span className="text-cyan-400 font-mono">&gt; 50</span>
            </label>
            <input type="range" min="0" max="100" defaultValue="50" className="w-full accent-cyan-500 h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer" />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
              <span>0</span><span>100</span>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">Interaction Date</label>
            <div className="grid grid-cols-2 gap-2">
              <input type="date" className="bg-slate-950 border border-slate-700 text-xs rounded-lg px-2 py-1.5 text-slate-300 focus:outline-none focus:border-cyan-500" />
              <input type="date" className="bg-slate-950 border border-slate-700 text-xs rounded-lg px-2 py-1.5 text-slate-300 focus:outline-none focus:border-cyan-500" />
            </div>
          </div>
        </div>
        
        <div className="p-4 border-t border-slate-800 bg-slate-900">
          <button className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-medium py-2 rounded-lg transition-colors text-sm">
            Apply Filters
          </button>
        </div>
      </div>

      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl relative overflow-hidden flex flex-col">
        <div ref={containerRef} className="flex-1 w-full bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-800 to-slate-950 cursor-crosshair">
          <div className="absolute inset-0 flex items-center justify-center opacity-20 pointer-events-none">
            <Network className="w-64 h-64 text-cyan-500" />
          </div>
        </div>

        <div className="absolute top-4 right-4 bg-slate-900/90 backdrop-blur border border-slate-700 p-1.5 rounded-lg flex space-x-1 shadow-xl">
          <button className="p-2 hover:bg-slate-800 rounded text-slate-300 hover:text-white transition" title="Force Layout"><Layers size={18} /></button>
          <div className="w-px bg-slate-700 mx-1"></div>
          <button className="p-2 hover:bg-slate-800 rounded text-slate-300 hover:text-white transition" title="Zoom In"><ZoomIn size={18} /></button>
          <button className="p-2 hover:bg-slate-800 rounded text-slate-300 hover:text-white transition" title="Zoom Out"><ZoomOut size={18} /></button>
          <button className="p-2 hover:bg-slate-800 rounded text-slate-300 hover:text-white transition" title="Fit to Screen"><Maximize size={18} /></button>
          <div className="w-px bg-slate-700 mx-1"></div>
          <button className="p-2 hover:bg-slate-800 rounded text-slate-300 hover:text-white transition" title="Export PNG"><Download size={18} /></button>
        </div>

        <div className="absolute top-4 left-4 flex gap-2">
           <div className="bg-slate-900/90 backdrop-blur border border-slate-700 px-3 py-1.5 rounded-lg shadow-xl text-xs font-mono text-slate-300">
             Nodes: <span className="text-cyan-400 font-bold">1,204</span>
           </div>
           <div className="bg-slate-900/90 backdrop-blur border border-slate-700 px-3 py-1.5 rounded-lg shadow-xl text-xs font-mono text-slate-300">
             Edges: <span className="text-cyan-400 font-bold">3,842</span>
           </div>
        </div>

        <button 
          onClick={() => setPanelOpen(!panelOpen)}
          className="absolute right-4 bottom-4 bg-cyan-600 hover:bg-cyan-500 text-white p-3 rounded-full shadow-lg shadow-cyan-900/50 transition-all z-10"
        >
          <Info size={24} />
        </button>

        <div className={`absolute top-0 right-0 h-full w-80 bg-slate-900/95 backdrop-blur-md border-l border-slate-700 shadow-2xl transition-transform duration-300 transform ${panelOpen ? 'translate-x-0' : 'translate-x-full'}`}>
          <div className="p-5">
             <div className="flex justify-between items-start mb-6">
                <div>
                  <span className="bg-red-500/20 text-red-400 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full">Suspect (Person)</span>
                  <h3 className="text-xl font-bold text-white mt-2">Vikram Sharma</h3>
                </div>
                <button onClick={() => setPanelOpen(false)} className="text-slate-400 hover:text-white">✕</button>
             </div>
             
             <div className="space-y-4">
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 border-b border-slate-700 pb-1">Attributes</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex justify-between"><span className="text-slate-400">ID:</span> <span className="text-slate-200 font-mono">P-89241</span></li>
                    <li className="flex justify-between"><span className="text-slate-400">Risk Score:</span> <span className="text-red-400 font-bold">98/100</span></li>
                    <li className="flex justify-between"><span className="text-slate-400">Aliases:</span> <span className="text-slate-200">Vicky, Bhai</span></li>
                    <li className="flex justify-between"><span className="text-slate-400">Last Seen:</span> <span className="text-slate-200">2023-10-22</span></li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 border-b border-slate-700 pb-1">Connections Summary</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex justify-between items-center"><span className="text-slate-400">Phones:</span> <span className="bg-slate-800 text-cyan-400 px-2 py-0.5 rounded text-xs font-mono">4</span></li>
                    <li className="flex justify-between items-center"><span className="text-slate-400">Accounts:</span> <span className="bg-slate-800 text-cyan-400 px-2 py-0.5 rounded text-xs font-mono">2</span></li>
                    <li className="flex justify-between items-center"><span className="text-slate-400">Associates:</span> <span className="bg-slate-800 text-amber-400 px-2 py-0.5 rounded text-xs font-mono">14</span></li>
                  </ul>
                </div>
                
                <div className="pt-4 space-y-2">
                  <button className="w-full bg-slate-800 hover:bg-slate-700 text-white font-medium py-2 rounded transition-colors text-sm border border-slate-700">View Full Profile</button>
                  <button className="w-full bg-slate-800 hover:bg-slate-700 text-white font-medium py-2 rounded transition-colors text-sm border border-slate-700 flex justify-center items-center gap-2"><Share2 size={16} /> Find Shortest Path</button>
                </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
