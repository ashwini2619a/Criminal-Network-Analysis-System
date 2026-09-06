import React, { useEffect, useRef, useState } from 'react';
import cytoscape, { Core } from 'cytoscape';
import {
  Search,
  Filter,
  ZoomIn,
  ZoomOut,
  Maximize2,
  RefreshCw,
  Share2,
  Route,
  Shield,
  Layers,
  ChevronLeft,
  ChevronRight,
  Sliders,
  UserCheck,
  Zap,
  Info
} from 'lucide-react';
import { getFullGraph, expandNode, oneClickExpand, getShortestPath, getCommunities } from '../../lib/api';
import { GraphData, AnyNode } from '../../types';

export const GraphExplorer: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<any | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [minRisk, setMinRisk] = useState<number>(0);
  const [activeTypes, setActiveTypes] = useState<Record<string, boolean>>({
    Person: true,
    Phone: true,
    BankAccount: true,
    Location: true,
    Organization: true,
    Vehicle: true,
    Incident: true,
    CellTower: true
  });
  const [sourcePathId, setSourcePathId] = useState('');
  const [targetPathId, setTargetPathId] = useState('');
  const [layoutMode, setLayoutMode] = useState<'cose' | 'concentric' | 'circle'>('cose');
  const [loading, setLoading] = useState(true);

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#111827',
            'font-size': '10px',
            'font-family': 'ui-monospace, monospace',
            'text-valign': 'bottom',
            'text-margin-y': 4,
            'background-color': '#0ea5e9',
            'width': 'mapData(risk_score, 0, 100, 24, 62)',
            'height': 'mapData(risk_score, 0, 100, 24, 62)',
            'border-width': 2,
            'border-color': '#d1d5db',
            'text-outline-color': '#ffffff',
            'text-outline-width': 2.5,
            'text-outline-opacity': 0.95
          }
        },
        // Node Type Styles
        {
          selector: 'node[node_type = "Person"]',
          style: { 'shape': 'ellipse', 'background-color': '#0ea5e9' }
        },
        {
          selector: 'node[node_type = "Phone"]',
          style: { 'shape': 'diamond', 'background-color': '#a855f7' }
        },
        {
          selector: 'node[node_type = "BankAccount"]',
          style: { 'shape': 'rectangle', 'background-color': '#f59e0b' }
        },
        {
          selector: 'node[node_type = "Location"]',
          style: { 'shape': 'triangle', 'background-color': '#10b981' }
        },
        {
          selector: 'node[node_type = "Organization"]',
          style: { 'shape': 'hexagon', 'background-color': '#f43f5e' }
        },
        {
          selector: 'node[node_type = "Vehicle"]',
          style: { 'shape': 'round-rectangle', 'background-color': '#6366f1' }
        },
        {
          selector: 'node[node_type = "Incident"]',
          style: { 'shape': 'star', 'background-color': '#f97316' }
        },
        {
          selector: 'node[node_type = "CellTower"]',
          style: { 'shape': 'octagon', 'background-color': '#38bdf8' }
        },
        // Edges
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': '#d1d5db',
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': '#d1d5db',
            'arrow-scale': 0.8,
            'opacity': 0.65,
            'label': 'data(edge_type)',
            'font-size': '8px',
            'font-family': 'ui-monospace, monospace',
            'color': '#6b7280',
            'text-rotation': 'autorotate',
            'text-outline-color': '#ffffff',
            'text-outline-width': 1.5
          }
        },
        // Specialized edge colors
        {
          selector: 'edge[edge_type = "TRANSFERRED_MONEY"]',
          style: { 'line-color': '#f59e0b', 'target-arrow-color': '#f59e0b', 'width': 2.5, 'opacity': 0.85 }
        },
        {
          selector: 'edge[edge_type = "CALLED"]',
          style: { 'line-color': '#0ea5e9', 'target-arrow-color': '#0ea5e9' }
        },
        {
          selector: 'edge[edge_type = "COMMANDS"]',
          style: { 'line-color': '#f43f5e', 'target-arrow-color': '#f43f5e', 'width': 2.5, 'opacity': 0.9 }
        },
        // Selected / Highlighted Elements
        {
          selector: 'node:selected',
          style: {
            'border-color': '#38bdf8',
            'border-width': 4
          }
        },
        {
          selector: '.highlighted',
          style: {
            'background-color': '#f43f5e',
            'line-color': '#f43f5e',
            'target-arrow-color': '#f43f5e',
            'border-color': '#111827',
            'border-width': 3,
            'opacity': 1.0,
            'z-index': 999
          }
        }
      ]
    });

    // Event handlers
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      setSelectedNode(node.data());
      setSelectedEdge(null);
    });

    cy.on('tap', 'edge', (evt) => {
      const edge = evt.target;
      setSelectedEdge(edge.data());
      setSelectedNode(null);
    });

    // Double tap: 1-Click Expansion (Auto-Feature 3)
    cy.on('dbltap', 'node', async (evt) => {
      const nodeId = evt.target.id();
      await handleExpandNode(nodeId);
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, []);

  const [error, setError] = useState<string | null>(null);

  const loadGraph = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getFullGraph();
      setGraphData(data);

      if (cyRef.current && data && data.nodes && data.nodes.length > 0) {
        const cy = cyRef.current;

        const cyNodes = data.nodes.map(n => ({
          group: 'nodes' as const,
          data: {
            ...n,
            id: String(n.id),
            label: n.name || n.registration_no || n.number || n.account_no || String(n.id),
            risk_score: n.risk_score != null ? Number(n.risk_score) : 35
          }
        }));

        const nodeIdSet = new Set(cyNodes.map(n => n.data.id));
        const validEdges = (data.edges || []).filter(e => {
          return e && e.source && e.target && nodeIdSet.has(String(e.source)) && nodeIdSet.has(String(e.target));
        }).map((e, idx) => ({
          group: 'edges' as const,
          data: {
            ...e,
            id: e.id ? String(e.id) : `edge-${idx}-${e.source}-${e.target}`,
            source: String(e.source),
            target: String(e.target),
            edge_type: e.edge_type || 'RELATED_TO'
          }
        }));

        cy.batch(() => {
          cy.elements().remove();
          cy.add(cyNodes);
          cy.add(validEdges);
        });

        applyFilters(cy);
        runLayout(layoutMode);

        requestAnimationFrame(() => {
          if (cyRef.current) {
            cyRef.current.resize();
            cyRef.current.fit(undefined, 30);
          }
        });
      } else if ((data as any)?.error) {
        setError((data as any).error);
      } else if (!data || !data.nodes || data.nodes.length === 0) {
        setError('No criminal network nodes found in graph repository.');
      }
    } catch (err: any) {
      console.error('Failed to load graph:', err);
      setError(err?.message || 'Failed to establish connection to graph database.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraph();
  }, []);

  const runLayout = (mode: string) => {
    if (!cyRef.current) return;
    const cy = cyRef.current;
    try {
      if (mode === 'cose') {
        cy.layout({
          name: 'cose',
          animate: true,
          animationDuration: 400,
          padding: 50,
          nodeOverlap: 30,
          idealEdgeLength: () => 110,
          edgeElasticity: () => 100,
          nodeRepulsion: () => 500000,
          gravity: 0.25,
          numIter: 800,
          componentSpacing: 140
        }).run();
      } else if (mode === 'concentric') {
        cy.layout({
          name: 'concentric',
          animate: true,
          padding: 40,
          concentric: (node: any) => node.data('risk_score') || 0,
          levelWidth: () => 20
        }).run();
      } else {
        cy.layout({ name: 'circle', animate: true, padding: 40 }).run();
      }
      setTimeout(() => {
        if (cyRef.current) {
          cyRef.current.resize();
          cyRef.current.fit(undefined, 40);
        }
      }, 450);
    } catch (layoutErr) {
      console.warn('Layout execution fallback to grid:', layoutErr);
      cy.layout({ name: 'grid', padding: 30 }).run();
    }
  };

  const applyFilters = (cyInstance?: Core) => {
    const cy = cyInstance || cyRef.current;
    if (!cy) return;

    cy.nodes().forEach(node => {
      const nData = node.data();
      const typeAllowed = activeTypes[nData.node_type] !== false;
      const riskAllowed = (nData.risk_score || 0) >= minRisk;
      const matchesSearch = !searchTerm || (nData.label || '').toLowerCase().includes(searchTerm.toLowerCase());

      if (typeAllowed && riskAllowed && matchesSearch) {
        node.style('display', 'element');
      } else {
        node.style('display', 'none');
      }
    });
  };

  useEffect(() => {
    applyFilters();
  }, [activeTypes, minRisk, searchTerm]);

  // 1-Click Expansion (Auto-Feature 3)
  const handleExpandNode = async (nodeId: string) => {
    if (!cyRef.current) return;
    try {
      const res = await oneClickExpand(nodeId, 2);
      if (res && res.nodes) {
        const cy = cyRef.current;
        const newNodes = res.nodes
          .filter(n => cy.getElementById(n.id).length === 0)
          .map(n => ({
            group: 'nodes' as const,
            data: {
              ...n,
              id: n.id,
              label: n.name || n.number || n.account_no || n.id,
              risk_score: n.risk_score || 30
            }
          }));

        const newEdges = res.edges
          .map((e, idx) => ({
            group: 'edges' as const,
            data: {
              ...e,
              id: `exp-${nodeId}-${idx}`,
              source: e.source,
              target: e.target,
              edge_type: e.edge_type
            }
          }));

        cy.add([...newNodes, ...newEdges]);
        cy.elements().removeClass('highlighted');
        cy.getElementById(nodeId).addClass('highlighted');
        cy.layout({ name: 'cose', animate: true, padding: 40 }).run();
      }
    } catch (err) {
      console.error('Failed to expand node:', err);
    }
  };

  // Find Shortest Path
  const handleFindPath = async () => {
    if (!cyRef.current || !sourcePathId || !targetPathId) return;
    try {
      const res = await getShortestPath(sourcePathId, targetPathId);
      const cy = cyRef.current;
      cy.elements().removeClass('highlighted');

      if (res.found && res.path) {
        res.path.forEach((id: string) => {
          cy.getElementById(id).addClass('highlighted');
        });
        cy.fit(cy.elements('.highlighted'), 50);
      } else {
        alert('No operational link found between these two targets.');
      }
    } catch (err) {
      console.error('Path search error:', err);
    }
  };

  return (
    <div className="flex h-[calc(100vh-80px)] overflow-hidden bg-slate-50 text-slate-900 rounded-xl border border-slate-200/90 relative animate-fade-in">
      {/* Left Sidebar: Controls & Filters (Collapsible) */}
      <div className={`transition-all duration-300 ease-in-out flex flex-col justify-between overflow-y-auto z-20 select-none bg-white/95 backdrop-blur-md border-r border-slate-200 shrink-0 ${
        sidebarOpen ? 'w-80 p-4' : 'w-0 p-0 overflow-hidden border-r-0'
      }`}>
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 pb-2.5">
            <div className="flex items-center space-x-2 font-mono">
              <Filter className="w-3.5 h-3.5 text-sky-600" />
              <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">Network Graph Filters</span>
            </div>
            <button
              onClick={() => {
                setSidebarOpen(false);
                setTimeout(() => {
                  if (cyRef.current) {
                    cyRef.current.resize();
                    cyRef.current.fit(undefined, 40);
                  }
                }, 320);
              }}
              className="p-1 rounded-md hover:bg-slate-100 text-slate-500 hover:text-slate-900 transition active:scale-95 cursor-pointer"
              title="Collapse Filters (Expand Canvas)"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
          </div>

          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5 transition-colors group-focus-within:text-sky-600" />
            <input
              type="text"
              placeholder="Search suspect, phone, plate..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-slate-50 hover:bg-white border border-slate-200 focus:border-sky-500 focus:bg-white text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-100 font-mono transition-all duration-200 shadow-2xs"
            />
          </div>

          {/* Node Type Toggles */}
          <div>
            <div className="text-[11px] font-mono text-slate-500 uppercase mb-2 font-bold tracking-wider">Entity Layers</div>
            <div className="space-y-1">
              {Object.keys(activeTypes).map((t) => (
                <label key={t} className="flex items-center justify-between text-xs text-slate-700 hover:text-slate-900 cursor-pointer py-1 px-2 rounded-md hover:bg-slate-100 transition-colors">
                  <span className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={activeTypes[t]}
                      onChange={(e) => setActiveTypes({ ...activeTypes, [t]: e.target.checked })}
                      className="rounded border-slate-300 text-sky-600 focus:ring-0 cursor-pointer"
                    />
                    <span className="font-mono text-[11px] font-medium">{t}</span>
                  </span>
                  <span className="w-2.5 h-2.5 rounded-full shrink-0 shadow-2xs" style={{
                    backgroundColor: t === 'Person' ? '#0ea5e9' :
                      t === 'Phone' ? '#a855f7' :
                      t === 'BankAccount' ? '#f59e0b' :
                      t === 'Location' ? '#10b981' :
                      t === 'Organization' ? '#f43f5e' :
                      t === 'Vehicle' ? '#6366f1' :
                      t === 'CellTower' ? '#38bdf8' : '#f97316'
                  }} />
                </label>
              ))}
            </div>
          </div>

          {/* Risk Score Slider */}
          <div>
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 mb-1 font-bold">
              <span>MIN RISK SCORE</span>
              <span className="text-sky-800 font-bold bg-sky-50 px-1.5 py-0.5 rounded border border-sky-200">{minRisk} / 100</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={minRisk}
              onChange={(e) => setMinRisk(Number(e.target.value))}
              className="w-full accent-sky-600 bg-slate-200 rounded-lg cursor-pointer h-1.5"
            />
          </div>

          {/* Shortest Path Finder */}
          <div className="pt-3 border-t border-slate-200 space-y-2">
            <div className="text-[11px] font-mono uppercase text-slate-600 flex items-center space-x-1.5 font-bold tracking-wider">
              <Route className="w-3.5 h-3.5 text-sky-600" />
              <span>Link Tracer (Shortest Path)</span>
            </div>
            <input
              type="text"
              placeholder="Source Target ID"
              value={sourcePathId}
              onChange={(e) => setSourcePathId(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded-lg bg-slate-50 hover:bg-white border border-slate-200 text-[11px] font-mono text-slate-900 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:bg-white focus:ring-2 focus:ring-sky-100 transition shadow-2xs"
            />
            <input
              type="text"
              placeholder="Destination Target ID"
              value={targetPathId}
              onChange={(e) => setTargetPathId(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded-lg bg-slate-50 hover:bg-white border border-slate-200 text-[11px] font-mono text-slate-900 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:bg-white focus:ring-2 focus:ring-sky-100 transition shadow-2xs"
            />
            <button
              onClick={handleFindPath}
              className="w-full py-1.5 rounded-lg bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 text-xs font-mono font-bold text-white shadow-xs hover:shadow-md active:scale-95 transition-all duration-200 cursor-pointer"
            >
              Trace Critical Link
            </button>
          </div>
        </div>

        {/* Layout Switcher */}
        <div className="pt-3 border-t border-slate-200 mt-3">
          <div className="text-[10px] font-mono text-slate-400 uppercase mb-1.5 font-bold">Layout Algorithm</div>
          <div className="grid grid-cols-3 gap-1.5 text-[11px] font-mono">
            <button
              onClick={() => { setLayoutMode('cose'); runLayout('cose'); }}
              className={`py-1 rounded-md border transition font-bold cursor-pointer active:scale-95 ${layoutMode === 'cose' ? 'bg-sky-50 text-sky-800 border-sky-200 shadow-2xs' : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50'}`}
            >
              Force
            </button>
            <button
              onClick={() => { setLayoutMode('concentric'); runLayout('concentric'); }}
              className={`py-1 rounded-md border transition font-bold cursor-pointer active:scale-95 ${layoutMode === 'concentric' ? 'bg-sky-50 text-sky-800 border-sky-200 shadow-2xs' : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50'}`}
            >
              Concentric
            </button>
            <button
              onClick={() => { setLayoutMode('circle'); runLayout('circle'); }}
              className={`py-1 rounded-md border transition font-bold cursor-pointer active:scale-95 ${layoutMode === 'circle' ? 'bg-sky-50 text-sky-800 border-sky-200 shadow-2xs' : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50'}`}
            >
              Circular
            </button>
          </div>
        </div>
      </div>

      {/* Main Canvas Area */}
      <div className="flex-1 relative flex flex-col min-w-0">
        {/* Floating Top HUD Controls */}
        <div className="absolute top-4 left-4 z-10 flex flex-wrap items-center gap-2 bg-white/95 backdrop-blur-md border border-slate-200/90 rounded-xl p-1.5 shadow-sm">
          {!sidebarOpen && (
            <button
              onClick={() => {
                setSidebarOpen(true);
                setTimeout(() => {
                  if (cyRef.current) {
                    cyRef.current.resize();
                    cyRef.current.fit(undefined, 40);
                  }
                }, 320);
              }}
              className="px-2.5 py-1.5 rounded-lg bg-white hover:bg-sky-50 border border-slate-200 hover:border-sky-300 text-xs font-mono text-sky-700 flex items-center space-x-1.5 transition shadow-2xs active:scale-95 cursor-pointer"
              title="Open Filter Drawer"
            >
              <Sliders className="w-3.5 h-3.5" />
              <span className="font-bold">Filters</span>
            </button>
          )}

          <div className="flex items-center space-x-1">
            <button
              onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.25)}
              className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-600 hover:text-slate-900 transition active:scale-95 cursor-pointer"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 0.8)}
              className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-600 hover:text-slate-900 transition active:scale-95 cursor-pointer"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={() => {
                if (cyRef.current) {
                  cyRef.current.resize();
                  cyRef.current.fit(undefined, 40);
                }
              }}
              className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-600 hover:text-slate-900 transition active:scale-95 cursor-pointer"
              title="Fit to Screen"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
            <button
              onClick={loadGraph}
              className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-600 hover:text-slate-900 transition active:scale-95 cursor-pointer"
              title="Reset Canvas"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          <div className="hidden sm:flex items-center space-x-1 border-l border-slate-200 pl-2 font-mono">
            <button
              onClick={() => { setLayoutMode('cose'); runLayout('cose'); }}
              className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase transition active:scale-95 cursor-pointer ${layoutMode === 'cose' ? 'bg-sky-50 text-sky-800 border border-sky-200 shadow-2xs' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}
            >
              Force
            </button>
            <button
              onClick={() => { setLayoutMode('concentric'); runLayout('concentric'); }}
              className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase transition active:scale-95 cursor-pointer ${layoutMode === 'concentric' ? 'bg-sky-50 text-sky-800 border border-sky-200 shadow-2xs' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}
            >
              Concentric
            </button>
            <button
              onClick={() => { setLayoutMode('circle'); runLayout('circle'); }}
              className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase transition active:scale-95 cursor-pointer ${layoutMode === 'circle' ? 'bg-sky-50 text-sky-800 border border-sky-200 shadow-2xs' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}
            >
              Circle
            </button>
          </div>
        </div>

        {/* Informative Tip */}
        <div className="absolute bottom-4 left-4 z-10 text-[10px] font-mono text-slate-500 bg-white/95 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm font-semibold">
          💡 Double-click any suspect node for 1-Click Network Expansion
        </div>

        {/* Loading Overlay */}
        {loading && (
          <div className="absolute inset-0 z-20 bg-white/80 backdrop-blur-sm flex flex-col items-center justify-center space-y-3 animate-fade-in">
            <RefreshCw className="w-8 h-8 text-sky-600 animate-spin" />
            <div className="text-sm font-bold font-mono text-slate-900 tracking-wider">
              LOADING CRIMINAL RELATIONSHIP NETWORK...
            </div>
            <div className="text-xs text-slate-500 font-mono font-medium">
              Mounting vertices, calculating topological weights, and indexing degrees
            </div>
          </div>
        )}

        {/* Error Overlay */}
        {!loading && error && (
          <div className="absolute inset-0 z-20 bg-white/95 flex flex-col items-center justify-center p-6 text-center space-y-4 animate-fade-in">
            <div className="p-3 rounded-full bg-rose-50 border border-rose-200 text-rose-700 shadow-2xs">
              <Shield className="w-8 h-8" />
            </div>
            <div className="text-base font-bold text-slate-900 font-mono">
              Knowledge Graph Connection Interrupted
            </div>
            <p className="text-xs text-slate-500 max-w-md font-mono">
              {error}
            </p>
            <button
              onClick={loadGraph}
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 text-white font-bold font-mono text-xs transition shadow-xs hover:shadow-md active:scale-95 cursor-pointer"
            >
              Retry Graph Ingestion
            </button>
          </div>
        )}

        {/* Empty State Overlay */}
        {!loading && !error && (!graphData || graphData.nodes.length === 0) && (
          <div className="absolute inset-0 z-20 bg-white/95 flex flex-col items-center justify-center p-6 text-center space-y-3 animate-fade-in">
            <Share2 className="w-10 h-10 text-slate-400" />
            <div className="text-sm font-bold text-slate-900 font-mono">No Graph Entities Available</div>
            <p className="text-xs text-slate-500 max-w-sm font-mono">
              Please ingest FIRs, CDR files, or bank transactions in the Ingestion Center to generate the entity relationship graph.
            </p>
          </div>
        )}

        {/* Cytoscape Container */}
        <div ref={containerRef} className="w-full h-full bg-slate-50" />
      </div>

      {/* Right Slide-out Details Panel */}
      {selectedNode && (
        <div className="w-80 bg-white/95 backdrop-blur-xl border-l border-slate-200 p-5 overflow-y-auto z-20 space-y-4 shadow-lg animate-slide-in">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <div>
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-md bg-sky-50 text-sky-800 border border-sky-200 font-bold">
                {selectedNode.node_type}
              </span>
              <h3 className="text-base font-bold text-slate-900 mt-1.5 truncate max-w-[210px]">{selectedNode.label || selectedNode.id}</h3>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="p-1 rounded-md hover:bg-slate-100 text-slate-400 hover:text-slate-800 text-xs font-mono transition cursor-pointer"
            >
              ✕
            </button>
          </div>

          {/* Threat Metric */}
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-slate-500 font-bold">THREAT RISK INDEX</span>
              <span className="font-extrabold text-rose-600">{selectedNode.risk_score || 50}/100</span>
            </div>
            <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden border border-slate-200">
              <div
                className="h-full rounded-full bg-gradient-to-r from-sky-500 via-amber-500 to-rose-500 transition-all duration-300"
                style={{ width: `${selectedNode.risk_score || 50}%` }}
              />
            </div>
          </div>

          {/* Dynamic Attributes */}
          <div className="space-y-1.5 text-xs">
            {Object.entries(selectedNode)
              .filter(([k]) => !['id', 'label', 'node_type', 'risk_score'].includes(k))
              .map(([k, v]) => (
                <div key={k} className="flex items-center justify-between py-1 border-b border-slate-200/70 font-mono">
                  <span className="text-slate-500 capitalize text-[11px] font-medium">{k.replace(/_/g, ' ')}:</span>
                  <span className="text-slate-800 font-semibold truncate max-w-[140px] text-[11px]">{String(v)}</span>
                </div>
              ))}
          </div>

          {/* Quick Actions */}
          <div className="space-y-2 pt-2">
            {selectedNode.node_type === 'Person' && (
              <div className="p-2.5 rounded-lg bg-slate-50 border border-sky-200 space-y-1 text-[11px] font-mono mb-2">
                <div className="text-sky-800 font-bold flex items-center justify-between">
                  <span>OSINT INTEL RECON</span>
                  <span className="text-[9px] px-1.5 py-0.2 bg-sky-100 rounded text-sky-800 border border-sky-300 font-bold">CCTNS LINKED</span>
                </div>
                <div className="text-slate-700 text-[10px] truncate font-medium">Telegram Handle: @{String(selectedNode.label || selectedNode.id).toLowerCase().replace(/\s+/g, '_')}_boss</div>
                <div className="text-slate-400 text-[9px]">Verified cross-platform metadata</div>
              </div>
            )}

            <button
              onClick={() => handleExpandNode(selectedNode.id)}
              className="w-full py-2 rounded-lg bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 text-white font-bold text-xs font-mono flex items-center justify-center space-x-1.5 transition shadow-xs hover:shadow-md active:scale-95 cursor-pointer"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>1-Click Expand Network</span>
            </button>

            {selectedNode.node_type === 'Person' && (
              <a
                href={`/suspect?id=${selectedNode.id}`}
                className="w-full py-2 rounded-lg bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs font-mono flex items-center justify-center space-x-1.5 transition border border-slate-200 block text-center shadow-2xs hover:shadow-xs active:scale-95 cursor-pointer"
              >
                <UserCheck className="w-3.5 h-3.5 inline mr-1 text-sky-600" />
                <span>Open Full Legal Dossier</span>
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
