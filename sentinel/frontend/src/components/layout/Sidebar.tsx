import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  UploadCloud,
  Network,
  Map,
  PhoneCall,
  Landmark,
  History,
  Bot,
  UserCheck,
  ShieldCheck,
  AlertTriangle,
  FileSpreadsheet,
  Kanban,
  Settings,
  ChevronLeft,
  ChevronRight,
  ScanFace,
  PersonStanding
} from 'lucide-react';

interface SidebarProps {
  unackAlertsCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ unackAlertsCount = 10 }) => {
  const [collapsed, setCollapsed] = useState(false);

  const navSections = [
    {
      group: 'OPERATIONAL COMMAND',
      items: [
        { path: '/', label: 'Tactical Dashboard', icon: LayoutDashboard },
        { path: '/ingest', label: 'Smart Ingestion', icon: UploadCloud, badge: 'AUTO' },
        { path: '/graph', label: 'Graph Explorer', icon: Network, badge: 'CORE' },
        { path: '/map', label: 'Geo-Intelligence', icon: Map, badge: '8 LAYERS' },
      ]
    },
    {
      group: 'INTELLIGENCE DEEP DIVE',
      items: [
        { path: '/cdr', label: 'CDR Analysis', icon: PhoneCall },
        { path: '/financial', label: 'Financial Flow', icon: Landmark, badge: 'AML' },
        { path: '/timeline', label: 'Timeline Reconstruct', icon: History },
        { path: '/chat', label: 'AI Investigation Chat', icon: Bot, badge: 'NL' },
        { path: '/suspect', label: 'Suspect Dossier', icon: UserCheck },
        { path: '/faces', label: 'Face Tracker', icon: ScanFace, badge: 'AI' },
        { path: '/persons', label: 'Person Tracker', icon: PersonStanding, badge: 'LIVE' },
      ]
    },
    {
      group: 'EVIDENCE & CASE WORKFLOW',
      items: [
        { path: '/alerts', label: 'Alert Center', icon: AlertTriangle, alertCount: unackAlertsCount },
        { path: '/caseboard', label: 'Case Board', icon: Kanban, badge: 'KANBAN' },
        { path: '/evidence', label: 'Evidence Vault', icon: ShieldCheck, badge: 'SHA-256' },
        { path: '/reports', label: 'Report Generator', icon: FileSpreadsheet, badge: 'PDF' },
        { path: '/admin', label: 'Admin & Audit', icon: Settings },
      ]
    }
  ];

  return (
    <aside
      className={`animate-slide-in h-[calc(100vh-53px)] bg-white/95 backdrop-blur-xl border-r border-slate-200/90 flex flex-col justify-between transition-all duration-300 z-20 select-none ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Navigation List */}
      <div className="flex-1 overflow-y-auto py-3 space-y-5 px-2.5">
        {navSections.map((section, sIdx) => (
          <div key={sIdx}>
            {!collapsed && (
              <div className="px-3 mb-2 text-[10px] font-mono uppercase tracking-widest text-slate-400 font-extrabold flex items-center justify-between">
                <span>{section.group}</span>
                <span className="w-1.5 h-1.5 rounded-full bg-slate-300" />
              </div>
            )}
            <div className="space-y-1">
              {section.items.map((item) => {
                const IconComponent = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200 group ${
                        isActive
                          ? 'bg-gradient-to-r from-sky-50 via-sky-50/70 to-white text-sky-950 border-l-[3.5px] border-sky-600 shadow-2xs font-bold'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70 hover:translate-x-1'
                      }`
                    }
                    title={collapsed ? item.label : undefined}
                  >
                    <div className="flex items-center space-x-3">
                      <IconComponent className="w-4 h-4 text-sky-600 shrink-0 group-hover:scale-110 group-hover:text-sky-700 transition-all duration-200" />
                      {!collapsed && <span className="truncate tracking-wide font-medium group-hover:font-semibold">{item.label}</span>}
                    </div>

                    {!collapsed && (
                      <div className="flex items-center space-x-1.5">
                        {item.badge && (
                          <span className={`px-1.5 py-0.5 text-[9px] font-mono rounded font-bold border transition-transform group-hover:scale-105 ${
                            item.badge === 'CORE' || item.badge === 'AUTO' ? 'bg-sky-50 text-sky-800 border-sky-200' :
                            item.badge === 'AML' ? 'bg-amber-50 text-amber-800 border-amber-200' :
                            item.badge === '8 LAYERS' ? 'bg-indigo-50 text-indigo-800 border-indigo-200' :
                            item.badge === 'SHA-256' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' :
                            'bg-slate-100 text-slate-700 border-slate-200'
                          }`}>
                            {item.badge}
                          </span>
                        )}
                        {item.alertCount !== undefined && item.alertCount > 0 && (
                          <span className="px-1.5 py-0.2 text-[10px] font-black font-mono rounded-full bg-rose-600 text-white shadow-2xs animate-pulse">
                            {item.alertCount}
                          </span>
                        )}
                      </div>
                    )}
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Footer / Collapse Toggle */}
      <div className="p-3 border-t border-slate-200 bg-slate-50/90 flex items-center justify-between">
        {!collapsed && (
          <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-600">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse-subtle" />
            <span className="tracking-wider font-semibold">NCRB // SENTINEL-V2</span>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg bg-white hover:bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200 transition-all ml-auto shadow-2xs hover:shadow-xs active:scale-95 cursor-pointer"
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4 text-sky-600" /> : <ChevronLeft className="w-4 h-4 text-slate-600" />}
        </button>
      </div>
    </aside>
  );
};
