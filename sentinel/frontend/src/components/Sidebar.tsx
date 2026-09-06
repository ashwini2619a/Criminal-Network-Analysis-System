import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Upload, Network, UserSearch, Map, Banknote, Bot, FileText, Settings, Shield, ChevronLeft, ChevronRight, LogOut, User } from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard, alerts: 0 },
  { path: '/ingest', label: 'Data Ingestion', icon: Upload, alerts: 2 },
  { path: '/graph', label: 'Network Graph', icon: Network, alerts: 0 },
  { path: '/suspect', label: 'Suspect Profiles', icon: UserSearch, alerts: 5 },
  { path: '/map', label: 'Geo Intelligence', icon: Map, alerts: 0 },
  { path: '/financial', label: 'Financial Flow', icon: Banknote, alerts: 1 },
  { path: '/chat', label: 'AI Assistant', icon: Bot, alerts: 0 },
  { path: '/dossier', label: 'Dossier & Evidence', icon: FileText, alerts: 0 },
  { path: '/admin', label: 'Admin Panel', icon: Settings, alerts: 0 },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={`flex flex-col bg-slate-900 border-r border-slate-800 transition-all duration-300 ${collapsed ? 'w-20' : 'w-64'}`}>
      <div className="flex items-center justify-between p-4 border-b border-slate-800">
        <div className={`flex items-center space-x-3 overflow-hidden ${collapsed ? 'w-0 opacity-0' : 'w-auto opacity-100'} transition-all duration-300`}>
          <Shield className="w-8 h-8 text-cyan-500 flex-shrink-0" />
          <span className="text-xl font-bold text-white tracking-widest uppercase">Sentinel</span>
        </div>
        <button onClick={() => setCollapsed(!collapsed)} className="p-1 hover:bg-slate-800 rounded-md text-slate-400">
          {collapsed ? <ChevronRight size={24} /> : <ChevronLeft size={24} />}
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-2 px-2">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-3 py-2.5 rounded-lg transition-colors relative group ${
                    isActive ? 'bg-slate-800 text-cyan-400' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    {isActive && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-cyan-500 rounded-r-md"></div>}
                    <item.icon size={22} className={`flex-shrink-0 ${collapsed ? 'mx-auto' : 'mr-3'}`} />
                    {!collapsed && <span className="font-medium whitespace-nowrap flex-1">{item.label}</span>}
                    {!collapsed && item.alerts > 0 && (
                      <span className="bg-red-500/20 text-red-500 text-xs font-bold px-2 py-0.5 rounded-full">
                        {item.alerts}
                      </span>
                    )}
                    {collapsed && (
                       <div className="absolute left-14 bg-slate-800 text-white px-2 py-1 rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity z-50 whitespace-nowrap pointer-events-none">
                         {item.label}
                       </div>
                    )}
                  </>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className={`flex items-center ${collapsed ? 'justify-center' : 'justify-between'}`}>
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center flex-shrink-0 text-cyan-500">
              <User size={20} />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-white">Investigator A.</span>
                <span className="text-xs text-slate-500">Sr. Analyst</span>
              </div>
            )}
          </div>
          {!collapsed && (
            <button className="p-2 hover:bg-slate-800 rounded-md text-red-400 hover:text-red-300 transition-colors">
              <LogOut size={20} />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
}
