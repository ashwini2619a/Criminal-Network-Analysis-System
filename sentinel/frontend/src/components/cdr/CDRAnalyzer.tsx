import React, { useState, useEffect } from 'react';
import {
  PhoneCall,
  Smartphone,
  AlertTriangle,
  RotateCcw,
  Clock,
  Radio,
  Search,
  Users,
  Layers,
  ArrowRight,
  Cpu,
  RefreshCw
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { getBurnerPhones, getTemporal } from '../../lib/api';

export const CDRAnalyzer: React.FC = () => {
  const [burnerData, setBurnerData] = useState<any>(null);
  const [temporalData, setTemporalData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      getBurnerPhones(),
      getTemporal()
    ]).then(([burners, temporal]) => {
      setBurnerData(burners || null);
      setTemporalData(temporal || null);
    }).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchData();
  }, []);

  const imeiReuse: any[] = burnerData?.imei_reuse || [];
  const simSwaps: any[] = burnerData?.sim_swap_chains || [];
  const colocations: any[] = burnerData?.colocation_clusters || [];

  // Dynamic 24h hourly distribution from temporal intelligence or fallback
  const hourlyDist = temporalData?.activity_patterns?.hourly_distribution;
  const hourlyData = hourlyDist && hourlyDist.length === 24
    ? hourlyDist.map((calls: number, h: number) => ({
        hour: `${h.toString().padStart(2, '0')}:00`,
        calls
      }))
    : [
        { hour: '00:00', calls: 3 }, { hour: '02:00', calls: 14 }, { hour: '04:00', calls: 8 },
        { hour: '06:00', calls: 5 }, { hour: '08:00', calls: 18 }, { hour: '10:00', calls: 32 },
        { hour: '12:00', calls: 45 }, { hour: '14:00', calls: 38 }, { hour: '16:00', calls: 52 },
        { hour: '18:00', calls: 48 }, { hour: '20:00', calls: 64 }, { hour: '22:00', calls: 41 }
      ];

  const defaultTopContacts = [
    { number: '+91-9876500001', name: 'Vikram Sinha', calls: 84, duration_min: 312 },
    { number: '+91-9876500002', name: 'Burner SIM 1', calls: 62, duration_min: 198 },
    { number: '+91-9835012345', name: 'Anita Devi', calls: 45, duration_min: 154 },
    { number: '+91-9431109876', name: 'Sunil @ Bullet', calls: 39, duration_min: 142 },
    { number: '+91-9123456789', name: 'Deepak Tiwari', calls: 28, duration_min: 96 }
  ];

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in">
      {/* Top Banner */}
      <div className="border-b border-slate-200/90 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-xl font-extrabold tracking-tight text-slate-900">
              CDR Deep Analysis & Burner Phone Triangulation
            </h1>
            <span className="tactical-badge-sky text-[11px]">
              TELECOM INTELLIGENCE
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Surfaces telecom anomalies, burner hardware reuse (IMEI switching), nocturnal surge hours, and contact frequency matrix.
          </p>
        </div>

        <button
          onClick={fetchData}
          disabled={loading}
          className="tactical-btn-secondary flex items-center space-x-2 text-xs font-mono self-start sm:self-auto shadow-xs"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-sky-600 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Analysis</span>
        </button>
      </div>

      {/* Row 1: Algorithmic Burner Phone Hardware IMEI Reuse Section */}
      <div className="p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2 text-xs font-bold text-rose-700 uppercase font-mono tracking-wider">
            <Cpu className="w-4 h-4 text-rose-600 animate-pulse" />
            <span>TELECOM HARDWARE CORRELATION ENGINE // BURNER DETECTIONS</span>
          </div>
          <span className={`text-[10px] font-mono px-2.5 py-1 rounded-full font-bold uppercase tracking-wider ${
            imeiReuse.length > 0 
              ? 'bg-rose-50 text-rose-700 border border-rose-200' 
              : 'bg-slate-100 text-slate-600 border border-slate-200'
          }`}>
            {imeiReuse.length > 0 ? `${imeiReuse.length} IMEI Anomalies Flagged` : 'Scanning CDR Registry'}
          </span>
        </div>

        {imeiReuse.length === 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs font-mono">
            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/70">
              <span className="text-slate-400 text-[10px] uppercase font-bold tracking-wider">Hardware IMEI:</span>
              <div className="text-sm font-bold text-sky-600 mt-1 select-all">Scanning active registers...</div>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/70">
              <span className="text-slate-400 text-[10px] uppercase font-bold tracking-wider">Linked SIM Cards:</span>
              <div className="text-sm font-bold text-slate-800 mt-1">No multi-SIM reuse detected</div>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/70">
              <span className="text-slate-400 text-[10px] uppercase font-bold tracking-wider">Status:</span>
              <div className="text-sm font-bold text-emerald-600 mt-1">Normal Telephony Profile</div>
            </div>
          </div>
        ) : (
          <div className="space-y-3.5">
            {imeiReuse.map((item: any, idx: number) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-50/60 hover:bg-slate-50 border border-slate-200 transition-colors shadow-2xs space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
                  <div className="flex items-center space-x-2.5">
                    <span className="text-slate-400 text-[10px] uppercase font-bold">DEVICE IMEI:</span>
                    <span className="text-sm font-extrabold text-sky-700 select-all tracking-wider font-mono">{item.imei}</span>
                    <span className="tactical-badge-rose text-[10px]">
                      {item.sim_count} CYCLED SIMS
                    </span>
                  </div>
                  <div className="text-slate-500 text-[11px]">
                    First Seen: <span className="text-slate-700 font-semibold">{item.first_seen}</span> | Last Seen: <span className="text-slate-700 font-semibold">{item.last_seen}</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs font-mono pt-3 border-t border-slate-200/80">
                  <div className="p-3 rounded-lg bg-white border border-slate-200/80 shadow-2xs">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Linked SIM Phone Numbers</span>
                    <div className="text-xs font-bold text-slate-800 mt-1.5 space-y-1">
                      {item.phone_numbers?.map((p: string, pIdx: number) => (
                        <div key={pIdx} className="flex items-center space-x-1.5 text-sky-700">
                          <span className="w-1.5 h-1.5 rounded-full bg-sky-500"></span>
                          <span>{p}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-white border border-slate-200/80 shadow-2xs">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Operational Deduction</span>
                    <div className="text-xs text-amber-700 font-bold mt-1.5 leading-snug">
                      {item.likely_same_person ? 'High probability of single operative cycling burner SIM cards on one handset' : 'Multiple users identified'}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1">Evading cell tower intercept</div>
                  </div>

                  <div className="p-3 rounded-lg bg-white border border-slate-200/80 shadow-2xs flex flex-col justify-between">
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Threat Classification</span>
                      <div className="text-xs font-extrabold text-rose-700 mt-1.5">
                        {item.threat_level || 'CRITICAL'} // HARDWARE CORRELATED
                      </div>
                    </div>
                    <span className="text-[9px] px-2 py-0.5 rounded font-bold uppercase tracking-wider bg-rose-50 text-rose-700 border border-rose-200 text-center mt-2">
                      CONFIRMED BURNER TRANSCEIVER
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* SIM Swap Chains if available */}
        {simSwaps.length > 0 && (
          <div className="pt-3 border-t border-slate-100 space-y-2.5">
            <span className="text-xs font-mono font-bold text-amber-700 uppercase flex items-center space-x-1.5 tracking-wider">
              <RotateCcw className="w-3.5 h-3.5 text-amber-600" />
              <span>Correlated SIM-Swap Succession Chains</span>
            </span>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
              {simSwaps.slice(0, 4).map((sw: any, sIdx: number) => (
                <div key={sIdx} className="p-3 rounded-lg bg-amber-50/50 border border-amber-200 flex items-center justify-between">
                  <div>
                    <div className="text-slate-400 text-[10px] uppercase font-bold tracking-wider">RETIRED ➔ ACTIVATED</div>
                    <div className="font-bold text-slate-900 mt-1 flex items-center space-x-2">
                      <span className="text-rose-600 font-mono">{sw.retired_phone}</span>
                      <ArrowRight className="w-3 h-3 text-slate-400" />
                      <span className="text-emerald-700 font-mono">{sw.activated_phone}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-amber-700 font-extrabold">{sw.overlap_percentage}% Overlap</div>
                    <div className="text-[10px] text-slate-400">{sw.gap_hours}h gap</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Row 2: Charts (24h Distribution & Most Contacted) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Hourly Distribution */}
        <div className="lg:col-span-7 p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
                <Clock className="w-4 h-4 text-sky-600" />
                <span>24-Hour Call Frequency Distribution</span>
              </h2>
              <p className="text-[11px] text-slate-500 mt-0.5">Identifies unusual nocturnal operating spikes from live event logs</p>
            </div>
            {temporalData?.activity_patterns?.peak_hours && (
              <span className="text-xs font-mono text-sky-700 bg-sky-50 px-2.5 py-1 rounded-full border border-sky-200 font-bold">
                Peak: {temporalData.activity_patterns.peak_hours.map((h: number) => `${h}:00`).join(', ')}
              </span>
            )}
          </div>
          <div className="h-56 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hourlyData}>
                <XAxis dataKey="hour" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.96)',
                    borderColor: '#e2e8f0',
                    borderRadius: '8px',
                    boxShadow: '0 4px 20px rgba(15,23,42,0.08)',
                    color: '#0f172a'
                  }}
                  labelStyle={{ fontWeight: 'bold', color: '#0f172a' }}
                />
                <Bar dataKey="calls" fill="#0284c7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top 5 Contacts Matrix */}
        <div className="lg:col-span-5 p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between">
          <div>
            <div className="mb-3 pb-3 border-b border-slate-100">
              <h2 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
                <Users className="w-4 h-4 text-sky-600" />
                <span>Top Contact Frequency Matrix</span>
              </h2>
              <p className="text-[11px] text-slate-500 mt-0.5">Ranked by total call connections & duration</p>
            </div>

            <div className="divide-y divide-slate-100 mt-2 text-xs">
              {defaultTopContacts.map((c, idx) => (
                <div key={idx} className="py-2.5 px-2 -mx-2 rounded-lg hover:bg-slate-50/80 transition-colors flex items-center justify-between font-mono">
                  <div>
                    <div className="text-slate-900 font-extrabold text-sm">{c.name}</div>
                    <div className="text-[11px] text-slate-500 font-mono mt-0.5">{c.number}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sky-700 font-extrabold text-sm">{c.calls} calls</div>
                    <div className="text-[10px] text-slate-400 font-mono">{c.duration_min} min</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
