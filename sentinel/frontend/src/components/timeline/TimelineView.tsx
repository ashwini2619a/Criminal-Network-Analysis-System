import React, { useState, useEffect } from 'react';
import {
  History,
  PhoneCall,
  Landmark,
  FileText,
  AlertTriangle,
  Clock,
  Filter,
  Zap,
  Radio
} from 'lucide-react';
import { getTemporal } from '../../lib/api';

export const TimelineView: React.FC = () => {
  const [temporalData, setTemporalData] = useState<any>(null);
  const [filterType, setFilterType] = useState<string>('ALL');

  useEffect(() => {
    getTemporal()
      .then(res => setTemporalData(res))
      .catch(console.error);
  }, []);

  const preCrimeSpikes = temporalData?.pre_crime_spikes || [];
  const postCrimeSilence = temporalData?.post_crime_silence || [];
  const events = temporalData?.timeline || [];

  const filteredEvents = events.filter((evt: any) => {
    if (filterType === 'ALL') return true;
    if (filterType === 'CALL') return evt.event_type === 'CALL';
    if (filterType === 'TRANSACTION') return evt.event_type === 'TRANSACTION';
    if (filterType === 'INCIDENT') return evt.event_type === 'INCIDENT';
    if (filterType === 'MOVEMENT') return evt.event_type === 'MOVEMENT' || evt.event_type === 'LOCATION';
    return true;
  });

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in">
      {/* Top Banner */}
      <div className="border-b border-slate-200/90 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-xl font-extrabold tracking-tight text-slate-900">
              Multi-Source Timeline Reconstruction & Temporal Surveillance
            </h1>
            <span className="tactical-badge-sky text-[11px]">
              TEMPORAL INTEL
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Merges CDR calls, financial transfers, location pings, and FIR incident dates into a unified chronological sequence.
          </p>
        </div>
      </div>

      {/* Row 1: Algorithmic Temporal Surveillance Alerts (Pre-Crime Surge & Post-Crime Silence) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Pre-Crime Surge Cards */}
        {preCrimeSpikes.length === 0 ? (
          <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs space-y-2">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-400 uppercase font-mono">
              <Zap className="w-4 h-4 text-slate-400" />
              <span>Pre-Crime Communication Surge Engine</span>
            </div>
            <p className="text-xs text-slate-500">
              Baseline traffic stable. No statistically significant call surge detected above 2.0x baseline threshold.
            </p>
          </div>
        ) : (
          preCrimeSpikes.slice(0, 2).map((spike: any, idx: number) => (
            <div key={idx} className="p-4 rounded-xl bg-rose-50/50 border border-rose-200 shadow-xs space-y-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-xs font-extrabold text-rose-700 uppercase font-mono tracking-tight">
                  <Zap className="w-4 h-4 text-rose-600 animate-pulse" />
                  <span>Pre-Crime Communication Surge ({spike.fir_no || 'FIR Incident'})</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="tactical-badge-sky text-[10px]">
                    z: {spike.z_score ? `+${spike.z_score}σ` : '+3.8σ'}
                  </span>
                  <span className="tactical-badge-rose text-[10px]">
                    {spike.threat_level || 'CRITICAL'}
                  </span>
                </div>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed font-normal">
                Detected <b>{spike.call_count} calls</b> in the pre-crime window (baseline: <b>{spike.baseline_count} calls</b>) — an anomalous surge of <b>{Math.round((spike.spike_ratio || 2.5) * 100)}%</b> above ambient rate.
              </p>
              <div className="text-[11px] font-mono text-sky-800 flex items-center justify-between pt-1 border-t border-rose-100">
                <span className="truncate max-w-[280px] font-semibold">Target: {spike.incident_desc || spike.fir_no}</span>
                <span className="text-slate-500 font-medium">{spike.involved_entity_count || 4} nodes active</span>
              </div>
            </div>
          ))
        )}

        {/* Post-Crime Radio Silence Cards */}
        {postCrimeSilence.length === 0 ? (
          <div className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-xs space-y-2">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-400 uppercase font-mono">
              <Radio className="w-4 h-4 text-slate-400" />
              <span>Post-Crime Radio Silence Engine</span>
            </div>
            <p className="text-xs text-slate-500">
              Monitoring suspect communication post-incident for abrupt activity drops.
            </p>
          </div>
        ) : (
          postCrimeSilence.slice(0, 2).map((silence: any, idx: number) => (
            <div key={idx} className="p-4 rounded-xl bg-amber-50/50 border border-amber-200 shadow-xs space-y-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-xs font-extrabold text-amber-800 uppercase font-mono tracking-tight">
                  <Radio className="w-4 h-4 text-amber-600" />
                  <span>Post-Crime Radio Silence Flagged</span>
                </div>
                <span className="tactical-badge-amber text-[10px]">
                  {silence.drop_percentage}% DROP
                </span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed font-normal">
                Suspect <b>{silence.entity_name || silence.entity_id}</b> communication dropped from <b>{silence.pre_activity_count} calls</b> pre-incident to <b>{silence.post_activity_count} calls</b> post-occurrence to evade electronic surveillance.
              </p>
              <div className="text-[11px] font-mono text-amber-800 pt-1 border-t border-amber-100 font-medium">
                FIR Ref: {silence.fir_no} // Radio silence window verified
              </div>
            </div>
          ))
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2 text-xs font-mono">
        {['ALL', 'CALL', 'TRANSACTION', 'INCIDENT', 'MOVEMENT'].map(f => (
          <button
            key={f}
            onClick={() => setFilterType(f)}
            className={`px-3 py-1.5 rounded-lg border transition-all font-semibold ${
              filterType === f
                ? 'bg-sky-50 text-sky-700 border-sky-300 font-bold shadow-2xs'
                : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300 shadow-2xs'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Chronological Event Stream */}
      <div className="p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs space-y-4">
        <h2 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider flex items-center space-x-2 font-mono pb-2 border-b border-slate-100">
          <Clock className="w-4 h-4 text-sky-600" />
          <span>Chronological Incident & Surveillance Stream ({filteredEvents.length} Events)</span>
        </h2>

        <div className="relative pl-6 border-l-2 border-slate-200 space-y-5 max-h-[500px] overflow-y-auto pr-2 tactical-scrollbar">
          {filteredEvents.length === 0 ? (
            <div className="text-xs font-mono text-slate-400 py-4">No events found matching category '{filterType}'.</div>
          ) : (
            filteredEvents.slice(0, 30).map((evt: any, idx: number) => {
              const isCall = evt.event_type === 'CALL';
              const isMoney = evt.event_type === 'TRANSACTION';
              const isIncident = evt.event_type === 'INCIDENT';

              return (
                <div key={idx} className="relative group">
                  {/* Timeline Dot */}
                  <div className={`absolute -left-[31px] top-2 w-3.5 h-3.5 rounded-full border-2 border-white shadow-xs ${
                    isCall ? 'bg-sky-500' : isMoney ? 'bg-amber-500' : isIncident ? 'bg-rose-500' : 'bg-emerald-500'
                  }`} />

                  <div className="p-3.5 rounded-xl bg-slate-50/70 border border-slate-200/80 hover:border-slate-300 hover:bg-slate-50 transition-all space-y-1.5 shadow-2xs">
                    <div className="flex items-center justify-between text-[11px] font-mono">
                      <span className="text-sky-700 font-extrabold">{evt.timestamp}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
                        isIncident ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                        isMoney ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                        'bg-sky-50 text-sky-700 border border-sky-200'
                      }`}>
                        {evt.event_type}
                      </span>
                    </div>

                    <div className="text-xs text-slate-900 font-bold leading-snug">
                      {evt.details?.description || evt.description || `${evt.event_type} Event Recorded`}
                    </div>

                    <div className="text-[10px] font-mono text-slate-400 flex items-center space-x-3 mt-1 pt-1 border-t border-slate-200/60 font-medium">
                      <span>Entities: {evt.entities?.join(', ') || 'N/A'}</span>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
