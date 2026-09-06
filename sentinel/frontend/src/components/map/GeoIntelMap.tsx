import React, { useState, useEffect } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Circle,
  Polyline,
  Tooltip as LeafletTooltip,
  LayersControl
} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  Layers,
  Radio,
  Navigation,
  Play,
  Pause,
  RotateCcw,
  Sliders,
  AlertTriangle,
  Eye,
  Crosshair,
  Shield,
  Activity
} from 'lucide-react';
import {
  getCellTowers,
  getSuspectTrail,
  getColocations,
  getGeofences,
  getMapIncidents
} from '../../lib/api';
import { SuspectTrail, CoLocationEvent } from '../../types';

// Custom Tactical Pin Icons
const createCustomIcon = (color: string, label: string = '') => {
  return L.divIcon({
    className: 'custom-map-marker',
    html: `
      <div style="
        background-color: ${color};
        width: 18px;
        height: 18px;
        border-radius: 50%;
        border: 2px solid #d1d5db;
        box-shadow: 0 0 10px ${color};
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 9px;
        font-weight: bold;
        color: white;
      ">
        ${label}
      </div>
    `,
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  });
};

const towerIcon = L.divIcon({
  className: 'tower-icon',
  html: `
    <div style="
      background-color: #38bdf8;
      width: 14px;
      height: 14px;
      clip-path: polygon(50% 0%, 100% 100%, 0% 100%);
      box-shadow: 0 0 8px #38bdf8;
    "></div>
  `,
  iconSize: [14, 14],
  iconAnchor: [7, 7]
});

export const GeoIntelMap: React.FC = () => {
  // Layer Toggles (8 Layers)
  const [layers, setLayers] = useState({
    satellite: false,
    crimeMarkers: true,
    cellTowers: true,
    geofences: true,
    movementTrail: true,
    colocations: true,
    jurisdiction: true
  });

  const [towers, setTowers] = useState<any[]>([]);
  const [incidents, setIncidents] = useState<any[]>([]);
  const [geofences, setGeofences] = useState<any[]>([]);
  const [colocations, setColocations] = useState<CoLocationEvent[]>([]);
  const [trail, setTrail] = useState<SuspectTrail | null>(null);
  const [activePhone, setActivePhone] = useState<string>('+91-9876500001');

  // CDR Replay State
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  // Initial Data Load
  useEffect(() => {
    Promise.all([
      getCellTowers(),
      getMapIncidents(),
      getGeofences(),
      getColocations(),
      getSuspectTrail(activePhone)
    ]).then(([t, inc, gf, coloc, tr]) => {
      setTowers(t || []);
      setIncidents(inc || []);
      setGeofences(gf || []);
      setColocations(coloc || []);
      setTrail(tr || null);
    }).catch(console.error);
  }, []);

  // When active phone changes, reload trail
  useEffect(() => {
    getSuspectTrail(activePhone)
      .then(tr => {
        setTrail(tr);
        setCurrentStep(0);
        setIsPlaying(false);
      })
      .catch(console.error);
  }, [activePhone]);

  // CDR Replay loop
  useEffect(() => {
    let timer: any;
    if (isPlaying && trail && trail.waypoints.length > 0) {
      timer = setInterval(() => {
        setCurrentStep(prev => {
          if (prev >= trail.waypoints.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [isPlaying, trail]);

  // Center coordinate around Jharkhand (Ranchi/Dhanbad corridor)
  const mapCenter: [number, number] = [23.5500, 85.7500];

  const visibleWaypoints = trail ? trail.waypoints.slice(0, currentStep + 1) : [];
  const currentWaypoint = visibleWaypoints[visibleWaypoints.length - 1];

  return (
    <div className="h-[calc(100vh-80px)] flex flex-col bg-slate-50 text-slate-900 rounded-xl border border-slate-200/90 overflow-hidden relative animate-fade-in">
      {/* Top Floating Control Bar */}
      <div className="bg-white/95 backdrop-blur-md border-b border-slate-200/90 px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 z-20 select-none shadow-2xs">
        <div className="flex flex-wrap items-center gap-3 min-w-0">
          <div className="flex items-center space-x-2">
            <Navigation className="w-4 h-4 text-sky-600" />
            <span className="font-extrabold text-xs uppercase tracking-wider text-slate-900 font-sans">Cell Tower Sector Hop & Dwell Map</span>
            <span className="tactical-badge-sky text-[10px]" title="Telemetry derived from CDR Cell Global Identifier (CGI) azimuth sectors during call/SMS events">
              CDR TOWER TELEMETRY (NON-GPS)
            </span>
          </div>

          {/* Suspect Phone Selector */}
          <div className="flex items-center space-x-1.5 pl-3 border-l border-slate-200 text-xs font-mono">
            <span className="text-slate-400 font-bold uppercase text-[10px]">TARGET PHONE:</span>
            <select
              value={activePhone}
              onChange={(e) => setActivePhone(e.target.value)}
              className="bg-slate-50 border border-slate-200 text-sky-700 font-bold rounded-lg px-2.5 py-1 text-xs focus:outline-none focus:border-sky-500 transition cursor-pointer shadow-2xs"
            >
              <option value="+91-9876500001" className="bg-white text-slate-900">+91-9876500001 (Vikram Sinha)</option>
              <option value="+91-9876500002" className="bg-white text-slate-900">+91-9876500002 (Burner B1)</option>
              <option value="+91-9876500003" className="bg-white text-slate-900">+91-9876500003 (Burner B2)</option>
              <option value="+91-9835012345" className="bg-white text-slate-900">+91-9835012345 (Anita Devi)</option>
              <option value="+91-9431109876" className="bg-white text-slate-900">+91-9431109876 (Sunil @ Bullet)</option>
            </select>
          </div>
        </div>

        {/* 8-Layer Toggles */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono">
          <button
            onClick={() => setLayers({ ...layers, satellite: !layers.satellite })}
            className={`px-2.5 py-1 rounded-lg border text-[11px] font-bold transition-all ${layers.satellite ? 'bg-sky-50 text-sky-700 border-sky-300 shadow-2xs' : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900'}`}
          >
            Satellite
          </button>
          <button
            onClick={() => setLayers({ ...layers, crimeMarkers: !layers.crimeMarkers })}
            className={`px-2.5 py-1 rounded-lg border text-[11px] font-bold transition-all ${layers.crimeMarkers ? 'bg-sky-50 text-sky-700 border-sky-300 shadow-2xs' : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900'}`}
          >
            Crimes ({incidents.length})
          </button>
          <button
            onClick={() => setLayers({ ...layers, cellTowers: !layers.cellTowers })}
            className={`px-2.5 py-1 rounded-lg border text-[11px] font-bold transition-all ${layers.cellTowers ? 'bg-sky-50 text-sky-700 border-sky-300 shadow-2xs' : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900'}`}
          >
            Towers ({towers.length})
          </button>
          <button
            onClick={() => setLayers({ ...layers, geofences: !layers.geofences })}
            className={`px-2.5 py-1 rounded-lg border text-[11px] font-bold transition-all ${layers.geofences ? 'bg-sky-50 text-sky-700 border-sky-300 shadow-2xs' : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900'}`}
          >
            Geofences ({geofences.length})
          </button>
          <button
            onClick={() => setLayers({ ...layers, colocations: !layers.colocations })}
            className={`px-2.5 py-1 rounded-lg border text-[11px] font-bold transition-all ${layers.colocations ? 'bg-rose-50 text-rose-700 border-rose-200 shadow-2xs' : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900'}`}
          >
            Co-Locations ({colocations.length})
          </button>
        </div>
      </div>

      {/* Main Map Container */}
      <div className="flex-1 relative">
        <MapContainer
          center={mapCenter}
          zoom={9}
          style={{ width: '100%', height: '100%', backgroundColor: '#f8fafc' }}
        >
          {/* Base Layer 1: Esri World Light Gray Canvas or Satellite */}
          {layers.satellite ? (
            <TileLayer
              attribution='&copy; Esri &mdash; World Imagery'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              maxZoom={19}
            />
          ) : (
            <TileLayer
              attribution='&copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"
              maxZoom={16}
            />
          )}

          {/* Layer 2: Crime Scene Markers */}
          {layers.crimeMarkers && incidents.map((inc, idx) => (
            <Marker
              key={`inc-${idx}`}
              position={[inc.lat || 23.3441, inc.lon || 85.3096]}
              icon={createCustomIcon(
                inc.severity === 'CRITICAL' ? '#e11d48' : inc.severity === 'HIGH' ? '#f59e0b' : '#38bdf8',
                '!'
              )}
            >
              <Popup className="tactical-popup">
                <div className="text-slate-900 p-1 text-xs font-sans">
                  <div className="font-extrabold text-rose-600 font-mono">{inc.fir_no}</div>
                  <div className="font-bold text-slate-800">{inc.crime_type} • {inc.police_station}</div>
                  <div className="text-[11px] text-slate-600 mt-1">{inc.description}</div>
                  <div className="text-[10px] font-mono text-slate-400 mt-1">IPC: {inc.ipc_sections?.join(', ')}</div>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Layer 3: Cell Towers */}
          {layers.cellTowers && towers.map((tw, idx) => (
            <React.Fragment key={`tw-${idx}`}>
              <Marker position={[tw.lat, tw.lon]} icon={towerIcon}>
                <Popup>
                  <div className="text-slate-900 p-1 text-xs font-sans">
                    <div className="font-extrabold text-sky-700 font-mono">{tw.tower_id}</div>
                    <div className="font-bold">{tw.name}</div>
                    <div className="text-[11px] text-slate-500">Operator: {tw.operator} ({tw.sector || 'Sector A'})</div>
                    <div className="text-[10px] font-mono text-slate-400">Azimuth: {tw.azimuth || 120}° | Radius: {tw.range_m || 2500}m</div>
                  </div>
                </Popup>
              </Marker>
              <Circle
                center={[tw.lat, tw.lon]}
                radius={tw.range_m || 2500}
                pathOptions={{ color: '#0284c7', fillColor: '#0284c7', fillOpacity: 0.08, weight: 1, dashArray: '4' }}
              />
            </React.Fragment>
          ))}

          {/* Layer 4: Geofences around Safehouses / Hideouts */}
          {layers.geofences && geofences.map((gf, idx) => (
            <React.Fragment key={`gf-${idx}`}>
              <Marker
                position={[gf.lat, gf.lon]}
                icon={createCustomIcon('#059669', 'G')}
              >
                <Popup>
                  <div className="text-slate-900 p-1 text-xs font-sans">
                    <div className="font-extrabold text-emerald-700 font-mono">{gf.name}</div>
                    <div className="text-[11px] text-slate-700 font-medium">{gf.location_type} • {gf.district}</div>
                    <div className="text-[10px] font-mono text-slate-400">Perimeter Radius: {gf.geofence_radius_m || 500}m</div>
                  </div>
                </Popup>
              </Marker>
              <Circle
                center={[gf.lat, gf.lon]}
                radius={gf.geofence_radius_m || 500}
                pathOptions={{ color: '#059669', fillColor: '#059669', fillOpacity: 0.12, weight: 1.5 }}
              />
            </React.Fragment>
          ))}

          {/* Layer 5: Suspect Movement Trail & Replay Polyline */}
          {layers.movementTrail && trail && visibleWaypoints.length > 0 && (
            <>
              <Polyline
                positions={visibleWaypoints.map(w => [w.lat, w.lon])}
                pathOptions={{ color: '#0284c7', weight: 3.5, opacity: 0.85 }}
              />
              {visibleWaypoints.map((w, idx) => (
                <Marker
                  key={`wp-${idx}`}
                  position={[w.lat, w.lon]}
                  icon={createCustomIcon(w.color, `${w.sequence}`)}
                >
                  <LeafletTooltip direction="top">
                    <div className="text-xs font-mono font-bold">
                      <span>Seq #{w.sequence}</span> • {w.formatted_time}<br/>
                      <span className="font-normal text-slate-500">Tower: {w.tower_id} ({w.district})</span>
                    </div>
                  </LeafletTooltip>
                </Marker>
              ))}
            </>
          )}

          {/* Layer 7: Co-Location Events Highlight */}
          {layers.colocations && colocations.map((col, idx) => (
            <Circle
              key={`coloc-${idx}`}
              center={[col.lat, col.lon]}
              radius={col.distance_meters || 500}
              pathOptions={{ color: '#e11d48', fillColor: '#e11d48', fillOpacity: 0.25, weight: 2 }}
            >
              <Popup>
                <div className="text-slate-900 p-1 text-xs font-sans">
                  <div className="font-extrabold text-rose-700 font-mono">🚨 {col.alert_title}</div>
                  <div className="text-[11px] text-slate-700 font-medium">{col.alert_description}</div>
                  <div className="text-[10px] font-mono text-slate-400 mt-1">Time Delta: {col.time_difference_min} min | Tower: {col.tower_id}</div>
                </div>
              </Popup>
            </Circle>
          ))}
        </MapContainer>

        {/* Floating Dwell Time & Legend Widget */}
        <div className="absolute top-4 right-4 z-20 bg-white/95 border border-slate-200/90 rounded-2xl p-4 shadow-md max-w-xs text-xs space-y-3 select-none backdrop-blur-xs">
          <div className="font-extrabold uppercase tracking-wider text-[11px] text-sky-700 font-mono flex items-center justify-between">
            <span>Sector Hop Dwell Breakdown</span>
            <Activity className="w-3.5 h-3.5 text-sky-600" />
          </div>
          <div className="text-[10px] text-slate-500 font-mono leading-tight bg-slate-50 p-2 rounded-lg border border-slate-200/80">
            📡 <strong>Telecommunication Dwell:</strong> Computed from duration and frequency at cell tower azimuths during CDR event windows. Not continuous GPS tracking.
          </div>

          {trail && trail.dwell_percentages && Object.keys(trail.dwell_percentages).length > 0 ? (
            <div className="space-y-1.5 font-mono text-[11px]">
              {Object.entries(trail.dwell_percentages).map(([dist, pct]) => (
                <div key={dist} className="flex items-center justify-between bg-slate-50 px-2.5 py-1.5 rounded-lg border border-slate-200/80">
                  <span className="text-slate-500 font-semibold">{dist}:</span>
                  <span className="font-extrabold text-slate-900">{pct}%</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-slate-400 font-mono text-[11px] py-1">No target trail selected</div>
          )}

          <div className="pt-2.5 border-t border-slate-100 space-y-1.5 text-[10px] font-mono text-slate-500">
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 shrink-0" />
              <span className="font-medium">Morning (06:00 - 12:00)</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-orange-400 shrink-0" />
              <span className="font-medium">Afternoon (12:00 - 18:00)</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shrink-0" />
              <span className="font-medium">Night (18:00 - 06:00)</span>
            </div>
          </div>
        </div>

        {/* Bottom Floating CDR Replay Bar */}
        {trail && trail.waypoints.length > 0 && (
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 bg-white/95 border border-slate-200/90 rounded-2xl p-3.5 shadow-lg backdrop-blur-md flex items-center space-x-4 max-w-xl w-full select-none">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="tactical-btn p-2 rounded-xl text-white font-bold shadow-xs"
              title={isPlaying ? 'Pause' : 'Play CDR Replay'}
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>

            <button
              onClick={() => { setCurrentStep(0); setIsPlaying(false); }}
              className="tactical-btn-secondary p-2 rounded-xl text-slate-600 shadow-2xs"
              title="Reset Timeline"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            <div className="flex-1 space-y-1.5">
              <div className="flex items-center justify-between text-[11px] font-mono">
                <span className="text-sky-700 font-extrabold">
                  {currentWaypoint ? currentWaypoint.formatted_time : 'START'}
                </span>
                <span className="text-slate-500 font-medium">
                  Step {currentStep + 1} / {trail.waypoints.length}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max={trail.waypoints.length - 1}
                value={currentStep}
                onChange={(e) => {
                  setCurrentStep(Number(e.target.value));
                  setIsPlaying(false);
                }}
                className="w-full accent-sky-600 bg-slate-200 rounded-lg cursor-pointer h-1.5"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
