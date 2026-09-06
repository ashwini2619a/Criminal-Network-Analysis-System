import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Layers, Calendar, Clock, Crosshair } from 'lucide-react';
import L from 'leaflet';

const iconPerson = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const iconTower = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

export default function CDRMapView() {
  const mapCenter: [number, number] = [28.6139, 77.2090]; // Delhi

  const polylineCoords: [number, number][] = [
    [28.6139, 77.2090],
    [28.5355, 77.2410],
    [28.4595, 77.0266]
  ];

  return (
    <div className="h-full flex flex-col space-y-4">
      <header>
        <h1 className="text-2xl font-bold text-white tracking-tight">Cell Tower Sector Hop Sequence & Dwell Time Analysis</h1>
        <p className="text-xs text-slate-400">CDR tower azimuth sector telemetry (call/SMS event timestamps — non-GPS tracking).</p>
      </header>

      <div className="flex-1 flex gap-4 min-h-0">
        <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden relative shadow-xl">
          <MapContainer center={mapCenter} zoom={11} className="w-full h-full" zoomControl={false}>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            
            <Marker position={[28.6139, 77.2090]} icon={iconTower}>
              <Popup className="custom-popup">
                <div className="bg-slate-900 text-white p-1">
                  <div className="font-bold text-cyan-400">Tower ID: DL-8842</div>
                  <div className="text-xs">Connaught Place</div>
                </div>
              </Popup>
            </Marker>
            
            <Marker position={[28.4595, 77.0266]} icon={iconPerson}>
              <Popup>
                <div className="bg-slate-900 text-white p-1">
                  <div className="font-bold text-red-400">Suspect: Vikram S.</div>
                  <div className="text-xs">Last Ping: 14:30</div>
                </div>
              </Popup>
            </Marker>

            <Polyline positions={polylineCoords} color="#ef4444" weight={3} dashArray="5, 10" opacity={0.7} />
          </MapContainer>

          <div className="absolute top-4 right-4 z-[400] flex flex-col gap-2">
             <button className="bg-slate-900/90 backdrop-blur border border-slate-700 p-2 text-white rounded hover:bg-slate-800 shadow-lg"><Layers size={20} /></button>
             <button className="bg-slate-900/90 backdrop-blur border border-slate-700 p-2 text-white rounded hover:bg-slate-800 shadow-lg"><Crosshair size={20} /></button>
          </div>
          
          <div className="absolute bottom-4 right-4 z-[400] bg-slate-900/95 backdrop-blur border border-slate-700 p-3 rounded-lg shadow-xl text-xs">
            <h4 className="font-semibold text-white mb-2 uppercase tracking-wider text-[10px]">Legend</h4>
            <div className="space-y-2">
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-blue-500 border border-blue-300"></div><span className="text-slate-300">Cell Tower</span></div>
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-red-500 border border-red-300"></div><span className="text-slate-300">Tower Sector Event</span></div>
              <div className="flex items-center gap-2"><div className="w-4 h-0.5 bg-red-500 border-t border-dashed border-red-900"></div><span className="text-slate-300">Tower Hop Sequence</span></div>
            </div>
          </div>
        </div>

        <div className="w-80 flex flex-col gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shrink-0">
            <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2"><Calendar size={16} /> Filters</h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Target Number</label>
                <select className="w-full bg-slate-950 border border-slate-700 text-sm rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500">
                  <option>+91-98765-43210 (Vikram)</option>
                  <option>+91-87654-32109 (Unknown)</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Date</label>
                <input type="date" defaultValue="2023-10-24" className="w-full bg-slate-950 border border-slate-700 text-sm rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500" />
              </div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex-1 overflow-hidden flex flex-col">
            <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2"><Clock size={16} /> Co-location Alerts</h2>
            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
              {[
                { time: '14:30', tower: 'DL-8842', peers: ['Jimmy D.', 'Unknown (+91-87...)'], dist: '< 50m' },
                { time: '09:15', tower: 'DL-3921', peers: ['Ramesh K.'], dist: '< 100m' },
                { time: '02:00', tower: 'HR-9922', peers: ['Abdul R.'], dist: '< 500m' }
              ].map((alert, i) => (
                <div key={i} className="bg-slate-950 border border-red-900/50 rounded-lg p-3 hover:border-red-500/50 transition-colors cursor-pointer">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-mono text-cyan-400">{alert.time}</span>
                    <span className="text-[10px] bg-red-500/20 text-red-400 px-1.5 py-0.5 rounded uppercase font-bold">Alert</span>
                  </div>
                  <div className="text-sm text-white mb-1">Tower: {alert.tower}</div>
                  <div className="text-xs text-slate-400">With: {alert.peers.join(', ')}</div>
                  <div className="text-xs text-slate-500 mt-1">Est. Distance: {alert.dist}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
