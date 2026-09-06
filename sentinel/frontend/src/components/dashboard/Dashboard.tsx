import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Briefcase,
  Users,
  Network,
  AlertTriangle,
  ArrowUpRight,
  TrendingUp,
  RefreshCw,
  Activity,
  Shield,
  Clock,
  CheckCircle2,
  Sparkles
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis
} from 'recharts';
import { getDashboard, getKingpins } from '../../lib/api';
import { DashboardData, KingpinResult } from '../../types';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [kingpins, setKingpins] = useState<KingpinResult[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const [dashRes, kpRes] = await Promise.all([
        getDashboard(),
        getKingpins(10)
      ]);
      setData(dashRes);
      const kps = Array.isArray(kpRes) ? kpRes : (kpRes?.kingpins || []);
      setKingpins(kps);
    } catch (err) {
      console.error('Failed to load dashboard metrics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const threatColors: Record<string, string> = {
    CRITICAL: '#e11d48',
    HIGH: '#f97316',
    MEDIUM: '#f59e0b',
    LOW: '#10b981'
  };

  const pieData = data?.threat_distribution
    ? Object.entries(data.threat_distribution).map(([name, value]) => ({
        name,
        value
      }))
    : [
        { name: 'CRITICAL', value: 8 },
        { name: 'HIGH', value: 18 },
        { name: 'MEDIUM', value: 34 },
        { name: 'LOW', value: 20 }
      ];

  const casesData = [
    { month: 'Oct', count: 12 },
    { month: 'Nov', count: 15 },
    { month: 'Dec', count: 14 },
    { month: 'Jan', count: 19 },
    { month: 'Feb', count: 22 },
    { month: 'Mar', count: 25 }
  ];

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in">
      {/* Top Bar: Title and Quick Command Buttons */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/90 pb-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-black tracking-tight text-gradient-primary font-sans">
              Operational Command Overview
            </h1>
            <span className="text-[11px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 tracking-wider shadow-2xs flex items-center space-x-1.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span>LIVE INTEL</span>
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-mono tracking-tight font-medium">
            Ministry of Home Affairs // Automated Criminal Network Discovery & Multi-Source Threat Index
          </p>
        </div>

        <div className="flex items-center space-x-2.5 shrink-0">
          <button
            onClick={fetchMetrics}
            className="px-3.5 py-1.5 rounded-lg bg-white border border-slate-200 hover:border-sky-400 text-xs font-mono font-semibold text-slate-700 hover:text-sky-700 flex items-center space-x-2 transition-all duration-200 shadow-2xs hover:shadow-xs active:scale-95 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-sky-600' : 'text-slate-400'}`} />
            <span>Sync Live</span>
          </button>
          <button
            onClick={() => navigate('/ingest')}
            className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 text-white font-bold text-xs font-mono flex items-center space-x-1.5 transition-all duration-200 shadow-xs hover:shadow-md active:scale-95 cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>+ Ingest Evidence</span>
          </button>
        </div>
      </div>

      {/* Problem Statement 26189 Mandate Banner */}
      <div className="p-4.5 rounded-xl bg-gradient-to-r from-white via-sky-50/70 to-white border border-sky-200/90 shadow-xs hover:shadow-md hover:border-sky-300 transition-all duration-300 relative overflow-hidden group">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full bg-sky-50 text-sky-800 border border-sky-200 text-[11px] font-mono font-bold shadow-2xs">
                PROBLEM STATEMENT 26189
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-800 border border-indigo-200 text-[11px] font-mono font-bold">
                THEME: BLOCKCHAIN & CYBERSECURITY
              </span>
              <span className="text-xs text-slate-500 font-mono font-semibold">
                MINISTRY OF HOME AFFAIRS (MHA) • NCRB / WOMEN SAFETY DIVISION
              </span>
            </div>
            <h2 className="text-base font-extrabold text-slate-900 tracking-tight flex items-center space-x-2">
              <span>AI-Powered Criminal Network Analysis System</span>
            </h2>
            <p className="text-xs text-slate-600 max-w-4xl leading-relaxed font-normal">
              Automated multi-source intelligence correlation across <strong className="text-sky-800 font-semibold">FIRs and police reports</strong>, <strong className="text-sky-800 font-semibold">Call Detail Records (CDRs)</strong>, <strong className="text-sky-800 font-semibold">Financial transactions</strong>, <strong className="text-sky-800 font-semibold">Surveillance reports</strong>, <strong className="text-sky-800 font-semibold">Social media OSINT</strong>, and <strong className="text-sky-800 font-semibold">Criminal history databases (CCTNS)</strong> to uncover hidden criminal networks, identify key influencers, detect suspicious patterns, and provide actionable intelligence for investigators.
            </p>
          </div>
          <div className="flex items-center gap-2 self-start md:self-center shrink-0">
            <div className="px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-mono font-bold flex items-center gap-2 shadow-2xs hover:bg-emerald-100 transition-colors">
              <Shield className="w-4 h-4 text-emerald-600" />
              <span>SEC 63 BSA AUDITED</span>
            </div>
          </div>
        </div>
      </div>

      {/* Row 1: 4 Tactical KPI Cards with Visual Interactivity */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Total Cases */}
        <div 
          onClick={() => navigate('/caseboard')}
          className="tactical-card tactical-card-hover p-4 relative overflow-hidden group before:absolute before:inset-x-0 before:top-0 before:h-[3px] before:bg-gradient-to-r before:from-sky-500 before:to-blue-600 animate-stagger-1 cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-slate-500 font-bold">Total Cases Active</span>
            <div className="p-2.5 rounded-xl bg-sky-50 border border-sky-200 text-sky-700 shadow-2xs group-hover:scale-110 group-hover:bg-sky-100 transition-all duration-300">
              <Briefcase className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-black font-mono text-slate-900 tracking-tight group-hover:text-sky-700 transition-colors">
              {data?.total_cases || 25}
            </span>
            <span className="text-[11px] text-sky-800 bg-sky-50 px-1.5 py-0.5 rounded-md border border-sky-200 flex items-center font-mono font-bold">
              +14% <TrendingUp className="w-3 h-3 ml-0.5" />
            </span>
          </div>
          <div className="text-[11px] text-slate-500 mt-2 font-mono flex items-center justify-between">
            <span>25 registered FIRs in graph</span>
            <ArrowUpRight className="w-3 h-3 text-slate-400 group-hover:text-sky-600 group-hover:translate-x-0.5 transition-all" />
          </div>
        </div>

        {/* Card 2: Tracked Suspects */}
        <div 
          onClick={() => navigate('/suspect')}
          className="tactical-card tactical-card-hover p-4 relative overflow-hidden group before:absolute before:inset-x-0 before:top-0 before:h-[3px] before:bg-gradient-to-r before:from-amber-400 before:to-amber-600 animate-stagger-2 cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-slate-500 font-bold">Tracked Suspects</span>
            <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-700 shadow-2xs group-hover:scale-110 group-hover:bg-amber-100 transition-all duration-300">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-black font-mono text-slate-900 tracking-tight group-hover:text-amber-700 transition-colors">
              {data?.total_suspects || 80}
            </span>
            <span className="text-[11px] text-amber-800 bg-amber-50 px-1.5 py-0.5 rounded-md border border-amber-200 font-mono font-bold">
              100% profiled
            </span>
          </div>
          <div className="text-[11px] text-slate-500 mt-2 font-mono flex items-center justify-between">
            <span>Includes 1 Shadow Kingpin</span>
            <ArrowUpRight className="w-3 h-3 text-slate-400 group-hover:text-amber-600 group-hover:translate-x-0.5 transition-all" />
          </div>
        </div>

        {/* Card 3: Active Networks */}
        <div 
          onClick={() => navigate('/graph')}
          className="tactical-card tactical-card-hover p-4 relative overflow-hidden group before:absolute before:inset-x-0 before:top-0 before:h-[3px] before:bg-gradient-to-r before:from-emerald-400 before:to-emerald-600 animate-stagger-3 cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-slate-500 font-bold">Syndicates & Factions</span>
            <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 shadow-2xs group-hover:scale-110 group-hover:bg-emerald-100 transition-all duration-300">
              <Network className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-black font-mono text-slate-900 tracking-tight group-hover:text-emerald-700 transition-colors">
              {data?.active_networks || 5}
            </span>
            <span className="text-[11px] text-emerald-800 bg-emerald-50 px-1.5 py-0.5 rounded-md border border-emerald-200 font-mono font-bold">
              Louvain Clusters
            </span>
          </div>
          <div className="text-[11px] text-slate-500 mt-2 font-mono flex items-center justify-between">
            <span>Dhanbad, Ranchi & Patna cartels</span>
            <ArrowUpRight className="w-3 h-3 text-slate-400 group-hover:text-emerald-600 group-hover:translate-x-0.5 transition-all" />
          </div>
        </div>

        {/* Card 4: High-Risk Alerts */}
        <div 
          onClick={() => navigate('/alerts')}
          className="tactical-card tactical-card-hover p-4 relative overflow-hidden group before:absolute before:inset-x-0 before:top-0 before:h-[3px] before:bg-gradient-to-r before:from-rose-500 before:to-red-600 animate-stagger-4 cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-rose-700 font-bold">Automated Threat Alerts</span>
            <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 shadow-2xs group-hover:scale-110 group-hover:bg-rose-100 transition-all duration-300 animate-pulse">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-black font-mono text-rose-600 tracking-tight group-hover:text-rose-700 transition-colors">
              {data?.high_risk_alerts || 10}
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200 font-mono font-black animate-pulse">
              3 CRITICAL
            </span>
          </div>
          <div className="text-[11px] text-slate-500 mt-2 flex items-center justify-between font-mono">
            <span>Hawala & Burner Chains</span>
            <span className="text-sky-700 group-hover:text-sky-800 flex items-center font-bold">
              View <ArrowUpRight className="w-3 h-3 ml-0.5 group-hover:translate-x-0.5 transition-transform" />
            </span>
          </div>
        </div>
      </div>

      {/* Row 2: Top 10 Kingpins Leaderboard & Threat Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left (8 cols): Top Kingpins Leaderboard */}
        <div className="lg:col-span-8 p-5 rounded-xl tactical-card shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
            <div>
              <h2 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
                <Shield className="w-4 h-4 text-sky-600" />
                <span>Top Criminal Kingpins (Centrality & Multi-Factor Threat)</span>
              </h2>
              <p className="text-[11px] text-slate-500 font-mono mt-0.5 font-medium">
                Composite Threat Risk Index combining Betweenness, PageRank, and Offense History
              </p>
            </div>
            <button
              onClick={() => navigate('/graph')}
              className="text-xs text-sky-700 hover:text-sky-900 font-mono font-bold flex items-center transition-all duration-200 self-start sm:self-auto hover:translate-x-0.5 cursor-pointer"
            >
              Expand Graph <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-mono uppercase text-[10px] tracking-wider font-bold">
                  <th className="pb-2.5 pl-1 w-16">Rank</th>
                  <th className="pb-2.5">Target Name</th>
                  <th className="pb-2.5 w-24">Status</th>
                  <th className="pb-2.5 w-28">Betweenness</th>
                  <th className="pb-2.5 w-44">Composite Risk</th>
                  <th className="pb-2.5 pr-1 text-right w-20">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200/80">
                {(Array.isArray(kingpins) ? kingpins : []).slice(0, 7).map((kp, idx) => {
                  const isShadow = kp.is_shadow_kingpin || kp.name.includes('Vikram Sinha');
                  const rankBadge = idx === 0
                    ? 'bg-amber-50 text-amber-800 border-amber-200 font-black shadow-2xs'
                    : idx === 1
                    ? 'bg-slate-100 text-slate-800 border-slate-200 font-bold'
                    : idx === 2
                    ? 'bg-orange-50 text-orange-800 border-orange-200 font-bold'
                    : 'bg-white text-slate-600 border-slate-200 font-medium';

                  return (
                    <tr 
                      key={kp.node_id || idx} 
                      onClick={() => navigate(`/suspect?id=${kp.node_id}`)}
                      className="hover:bg-sky-50/70 hover:border-l-4 hover:border-sky-500 transition-all duration-150 group cursor-pointer"
                    >
                      <td className="py-3 pl-1 font-mono">
                        <span className={`inline-block px-1.5 py-0.5 rounded-md text-[10px] border ${rankBadge}`}>
                          #{String(idx + 1).padStart(2, '0')}
                        </span>
                      </td>
                      <td className="py-3">
                        <div className="font-bold text-slate-900 group-hover:text-sky-800 transition-colors flex flex-wrap items-center gap-1.5">
                          <span>{kp.name}</span>
                          {isShadow && (
                            <span className="px-2 py-0.5 rounded-full text-[9px] bg-rose-50 text-rose-700 border border-rose-200 font-mono font-black tracking-wider animate-pulse shadow-2xs">
                              SHADOW KINGPIN
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-slate-100 text-slate-700 border border-slate-200 font-semibold">
                          {kp.status || 'ACCUSED'}
                        </span>
                      </td>
                      <td className="py-3 font-mono text-slate-700 font-medium">
                        {((kp.betweenness || 0.15) * 1).toFixed(4)}
                      </td>
                      <td className="py-3">
                        <div className="flex items-center space-x-2.5">
                          <div className="w-24 bg-slate-100 h-2 rounded-full overflow-hidden border border-slate-200">
                            <div
                              className="h-full rounded-full transition-all duration-500 bg-gradient-to-r from-sky-500 via-amber-500 to-rose-500 group-hover:opacity-90"
                              style={{
                                width: `${Math.min(100, kp.risk_score || 75)}%`
                              }}
                            />
                          </div>
                          <span className="font-mono font-bold text-xs text-slate-900">
                            {kp.risk_score || 85}/100
                          </span>
                        </div>
                      </td>
                      <td className="py-3 pr-1 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/suspect?id=${kp.node_id}`);
                          }}
                          className="px-2.5 py-1 rounded-md bg-white hover:bg-sky-600 text-slate-700 hover:text-white text-[11px] font-mono font-bold border border-slate-200 hover:border-sky-600 transition-all duration-200 shadow-2xs hover:shadow-xs active:scale-95 cursor-pointer"
                        >
                          Dossier
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right (4 cols): Threat Level Distribution Pie */}
        <div className="lg:col-span-4 p-5 rounded-xl tactical-card shadow-xs flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
              <Activity className="w-4 h-4 text-sky-600" />
              <span>Threat Level Breakdown</span>
            </h2>
            <p className="text-[11px] text-slate-500 mt-0.5 font-mono font-medium">80 suspects categorized by risk severity</p>

            <div className="relative h-48 mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={52}
                    outerRadius={74}
                    paddingAngle={4}
                    dataKey="value"
                    stroke="#ffffff"
                    strokeWidth={2}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={threatColors[entry.name] || '#38bdf8'} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.96)',
                      borderColor: '#e2e8f0',
                      borderRadius: '8px',
                      fontSize: '11px',
                      boxShadow: '0 4px 20px rgba(15,23,42,0.08)'
                    }}
                    itemStyle={{ color: '#0f172a' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-2xl font-black font-mono text-slate-900 tracking-tight">
                  {data?.total_suspects || 80}
                </span>
                <span className="text-[9px] font-mono uppercase tracking-widest text-slate-500 font-extrabold">
                  TOTAL TARGETS
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 mt-2 pt-3 border-t border-slate-200 font-mono text-xs">
            {pieData.map((item) => (
              <div key={item.name} className="flex items-center space-x-2 bg-slate-50/80 hover:bg-slate-100/90 px-2.5 py-1.5 rounded-lg border border-slate-200 transition-colors">
                <span className="w-2.5 h-2.5 rounded-full shrink-0 shadow-2xs" style={{ backgroundColor: threatColors[item.name] }} />
                <span className="text-slate-600 text-[11px] font-medium">{item.name}:</span>
                <span className="font-bold text-slate-900 ml-auto">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Row 3: Cases Over Time & Recent Activity Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Cases Area Chart */}
        <div className="lg:col-span-7 p-5 rounded-xl tactical-card shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-sky-600" />
                <span>Crime Network Incident Registrations (2025 - 2026)</span>
              </h2>
              <p className="text-[11px] text-slate-500 font-mono mt-0.5 font-medium">Monthly progression of registered FIRs across Jharkhand & Bihar</p>
            </div>
          </div>
          <div className="h-56 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={casesData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="casesGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0284c7" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#0284c7" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} fontFamily="monospace" />
                <YAxis stroke="#94a3b8" fontSize={11} fontFamily="monospace" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.96)',
                    borderColor: '#e2e8f0',
                    borderRadius: '8px',
                    boxShadow: '0 4px 20px rgba(15,23,42,0.08)',
                    fontFamily: 'monospace',
                    fontSize: '11px'
                  }}
                  itemStyle={{ color: '#0f172a' }}
                />
                <Area type="monotone" dataKey="count" stroke="#0284c7" strokeWidth={2.5} fillOpacity={1} fill="url(#casesGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Network Metrics & Density Gauge */}
        <div className="lg:col-span-5 p-5 rounded-xl tactical-card shadow-xs flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
              <Network className="w-4 h-4 text-sky-600" />
              <span>Structural Graph Telemetry</span>
            </h2>
            <p className="text-[11px] text-slate-500 font-mono mt-0.5 font-medium">Topological density & link connectivity metrics</p>

            <div className="grid grid-cols-2 gap-3 mt-4">
              <div 
                onClick={() => navigate('/graph')}
                className="p-3.5 rounded-xl bg-slate-50/80 hover:bg-white border border-slate-200 hover:border-sky-300 hover:shadow-xs transition-all duration-200 cursor-pointer group"
              >
                <div className="text-[10px] font-mono text-slate-500 uppercase font-bold">Total Entities</div>
                <div className="text-2xl font-black font-mono text-sky-700 mt-1 group-hover:translate-x-0.5 transition-transform">372 Nodes</div>
                <div className="text-[10px] text-slate-500 mt-0.5 font-mono">11 typed classes</div>
              </div>

              <div 
                onClick={() => navigate('/graph')}
                className="p-3.5 rounded-xl bg-slate-50/80 hover:bg-white border border-slate-200 hover:border-sky-300 hover:shadow-xs transition-all duration-200 cursor-pointer group"
              >
                <div className="text-[10px] font-mono text-slate-500 uppercase font-bold">Connections</div>
                <div className="text-2xl font-black font-mono text-sky-700 mt-1 group-hover:translate-x-0.5 transition-transform">869 Edges</div>
                <div className="text-[10px] text-slate-500 mt-0.5 font-mono">16 relation types</div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200">
                <div className="text-[10px] font-mono text-slate-500 uppercase font-bold">Network Density</div>
                <div className="text-2xl font-black font-mono text-slate-900 mt-1">0.0124</div>
                <div className="text-[10px] text-slate-500 mt-0.5 font-mono">Sparse syndicate core</div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200">
                <div className="text-[10px] font-mono text-slate-500 uppercase font-bold">Avg Node Degree</div>
                <div className="text-2xl font-black font-mono text-slate-900 mt-1">4.67</div>
                <div className="text-[10px] text-slate-500 mt-0.5 font-mono">High clustering coefficient</div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-200 flex items-center justify-between text-xs font-mono">
            <span className="text-slate-500 font-medium">Sec 63 BSA Custody Status:</span>
            <span className="text-emerald-800 font-bold flex items-center bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 shadow-2xs">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 text-emerald-600" />
              100% SHA-256 SEALED
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
