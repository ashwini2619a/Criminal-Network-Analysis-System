import React, { useState, useEffect } from 'react';
import { Shield, Bell, Clock, Activity, Lock, ChevronDown } from 'lucide-react';
import { getAlertsSummary } from '../../lib/api';

interface HeaderProps {
  onAlertClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onAlertClick }) => {
  const [activeRole, setActiveRole] = useState<'INVESTIGATOR' | 'SUPERVISOR' | 'ADMIN'>(() => {
    return (localStorage.getItem('sentinel_active_role') as any) || 'INVESTIGATOR';
  });
  const [timeStr, setTimeStr] = useState('');
  const [unackAlerts, setUnackAlerts] = useState(0);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('en-IN', { hour12: false }) + ' IST');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    getAlertsSummary().then(res => {
      if (res && typeof res.unacknowledged === 'number') {
        setUnackAlerts(res.unacknowledged);
      }
    }).catch(() => {});
  }, []);

  const handleRoleChange = (newRole: 'INVESTIGATOR' | 'SUPERVISOR' | 'ADMIN') => {
    setActiveRole(newRole);
    localStorage.setItem('sentinel_active_role', newRole);
    window.dispatchEvent(new CustomEvent('sentinel_role_changed', { detail: { role: newRole } }));
  };

  const roleConfigs = {
    INVESTIGATOR: {
      name: 'Insp. R. K. Choudhary',
      badge: 'BADGE #4092',
      color: 'text-sky-700',
      border: 'border-sky-300 hover:border-sky-400',
      bg: 'bg-sky-50/80 hover:bg-sky-50',
      avatarBg: 'bg-gradient-to-br from-sky-100 to-sky-200 text-sky-800 border-sky-300',
      label: 'INVESTIGATOR'
    },
    SUPERVISOR: {
      name: 'SP Ananya Sharma (IPS)',
      badge: 'BADGE #1004',
      color: 'text-amber-700',
      border: 'border-amber-300 hover:border-amber-400',
      bg: 'bg-amber-50/80 hover:bg-amber-50',
      avatarBg: 'bg-gradient-to-br from-amber-100 to-amber-200 text-amber-800 border-amber-300',
      label: 'SUPERVISOR'
    },
    ADMIN: {
      name: 'Director V. K. Rao',
      badge: 'CYBER-ROOT #001',
      color: 'text-rose-700',
      border: 'border-rose-300 hover:border-rose-400',
      bg: 'bg-rose-50/80 hover:bg-rose-50',
      avatarBg: 'bg-gradient-to-br from-rose-100 to-rose-200 text-rose-800 border-rose-300',
      label: 'SYSTEM ADMIN'
    }
  };

  const currentConfig = roleConfigs[activeRole];

  return (
    <header className="animate-fade-in bg-white/95 backdrop-blur-xl border-b border-slate-200/90 text-slate-800 px-6 py-2.5 flex items-center justify-between z-30 select-none shadow-xs transition-colors">
      {/* Left: Branding & Classification Banner */}
      <div className="flex items-center space-x-5">
        <div className="flex items-center space-x-3 cursor-pointer group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sky-500 to-blue-600 border border-sky-400 flex items-center justify-center shadow-xs group-hover:scale-105 group-hover:shadow-md transition-all duration-300">
            <Shield className="w-5 h-5 text-white group-hover:rotate-6 transition-transform duration-300" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold tracking-widest text-base font-mono text-gradient-primary">
                SENTINEL
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-sky-50 text-sky-700 border border-sky-200 font-bold shadow-2xs hover:bg-sky-100 hover:scale-105 transition-all cursor-default">
                PS #26189
              </span>
              <span className="hidden lg:inline-block text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold hover:bg-indigo-100 transition-colors cursor-default">
                BLOCKCHAIN & CYBERSECURITY
              </span>
            </div>
            <p className="text-[10px] text-slate-500 font-mono uppercase tracking-wider font-semibold">
              MINISTRY OF HOME AFFAIRS • NCRB (WOMEN SAFETY DIVISION)
            </p>
          </div>
        </div>

        <div className="hidden xl:flex items-center space-x-2 px-3 py-1 bg-rose-50/90 border border-rose-200 rounded-lg text-[11px] font-mono text-rose-700 shadow-2xs hover:border-rose-300 transition-colors">
          <Lock className="w-3.5 h-3.5 text-rose-600 animate-pulse" />
          <span className="tracking-wide font-semibold">CONFIDENTIAL // LAW ENFORCEMENT SENSITIVE // OFFICIAL USE ONLY</span>
        </div>
      </div>

      {/* Right: Telemetry, Clock, Alerts, RBAC Role Switcher & User */}
      <div className="flex items-center space-x-3">
        {/* Core Status with Real-Time Pulse */}
        <div className="hidden md:flex items-center space-x-2 text-xs font-mono text-emerald-800 bg-emerald-50/90 px-3 py-1.5 rounded-lg border border-emerald-200 shadow-2xs hover:bg-emerald-100/90 transition-colors cursor-default">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="font-bold tracking-wider text-[11px]">CORE ONLINE • 372 NODES</span>
        </div>

        {/* Live Clock */}
        <div className="flex items-center space-x-2 text-xs font-mono text-slate-700 bg-white hover:bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200 shadow-2xs transition-colors">
          <Clock className="w-3.5 h-3.5 text-sky-600" />
          <span className="tracking-widest font-semibold text-[11px]">{timeStr}</span>
        </div>

        {/* Interactive Alert Bell */}
        <button
          onClick={onAlertClick}
          className="relative p-2 rounded-lg bg-white hover:bg-slate-50 border border-slate-200 hover:border-rose-400 text-slate-700 hover:text-rose-600 transition-all shadow-2xs hover:shadow-xs group active:scale-95 cursor-pointer"
          title="Automated Pattern Alerts"
        >
          <Bell className="w-4 h-4 group-hover:scale-110 group-hover:rotate-12 transition-transform" />
          {unackAlerts > 0 && (
            <span className="absolute -top-1 -right-1 px-1.5 py-0.2 text-[10px] font-extrabold font-mono bg-rose-600 text-white rounded-full shadow-sm animate-pulse">
              {unackAlerts}
            </span>
          )}
        </button>

        {/* RBAC Role Selector & User Profile */}
        <div className={`flex items-center space-x-2.5 px-3 py-1.5 rounded-xl border ${currentConfig.border} ${currentConfig.bg} transition-all shadow-2xs hover:shadow-xs cursor-pointer`}>
          <div className={`w-7 h-7 rounded-lg border flex items-center justify-center text-xs font-extrabold font-mono shadow-inner ${currentConfig.avatarBg}`}>
            {activeRole === 'ADMIN' ? 'VR' : activeRole === 'SUPERVISOR' ? 'AS' : 'RK'}
          </div>
          <div className="text-left hidden sm:block">
            <div className="text-xs font-bold text-slate-900 leading-tight">{currentConfig.name}</div>
            <div className="flex items-center space-x-1.5 mt-0.5">
              <span className={`text-[10px] font-mono font-black tracking-wider ${currentConfig.color}`}>
                {currentConfig.badge}
              </span>
              <span className="text-slate-300 text-[10px]">•</span>
              {/* Interactive Role Dropdown */}
              <select
                id="activeRoleSelector"
                name="activeRoleSelector"
                aria-label="Switch Active RBAC Role"
                value={activeRole}
                onChange={(e) => handleRoleChange(e.target.value as any)}
                className="bg-transparent text-[10px] font-mono text-slate-800 font-bold cursor-pointer focus:outline-none tracking-wider hover:text-sky-700 transition-colors"
                title="Switch Active RBAC Role"
              >
                <option value="INVESTIGATOR" className="bg-white text-sky-700">INVESTIGATOR</option>
                <option value="SUPERVISOR" className="bg-white text-amber-700">SUPERVISOR</option>
                <option value="ADMIN" className="bg-white text-rose-700">ADMIN</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
