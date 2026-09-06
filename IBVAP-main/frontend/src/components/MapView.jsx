import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, Polyline, Polygon, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const createBopIcon = () => {
  return L.divIcon({
    className: 'custom-bop-icon',
    html: `<div class="w-6 h-6 bg-tactical-panel border-2 border-cyan-accent rounded-sm flex items-center justify-center rotate-45 shadow-[0_0_10px_rgba(0,240,255,0.5)]"><div class="w-2 h-2 bg-cyan-accent rounded-full"></div></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12],
  });
};

function DrawTools({ onTripwireDrawn, onZoneDrawn }) {
  const [drawingMode, setDrawingMode] = useState(null);
  const [currentPoints, setCurrentPoints] = useState([]);
  const map = useMapEvents({
    click(e) {
      if (drawingMode) {
        setCurrentPoints(prev => [...prev, [e.latlng.lat, e.latlng.lng]]);
      }
    },
    dblclick(e) {
      if (drawingMode === 'tripwire' && currentPoints.length > 0) {
        onTripwireDrawn([...currentPoints, [e.latlng.lat, e.latlng.lng]]);
        setCurrentPoints([]);
        setDrawingMode(null);
      } else if (drawingMode === 'zone' && currentPoints.length > 2) {
        onZoneDrawn([...currentPoints, [e.latlng.lat, e.latlng.lng]]);
        setCurrentPoints([]);
        setDrawingMode(null);
      }
    }
  });

  return (
    <div className="absolute top-4 right-4 z-[400] flex flex-col space-y-2">
      <button 
        onClick={(e) => { e.stopPropagation(); setDrawingMode(drawingMode === 'tripwire' ? null : 'tripwire'); setCurrentPoints([]); }}
        className={`px-3 py-1.5 font-mono text-xs border rounded transition-colors ${drawingMode === 'tripwire' ? 'bg-cyan-accent text-black border-cyan-accent' : 'bg-tactical-panel text-cyan-accent border-tactical-border hover:bg-[rgba(0,240,255,0.1)]'}`}
      >
        DRAW TRIPWIRE
      </button>
      <button 
        onClick={(e) => { e.stopPropagation(); setDrawingMode(drawingMode === 'zone' ? null : 'zone'); setCurrentPoints([]); }}
        className={`px-3 py-1.5 font-mono text-xs border rounded transition-colors ${drawingMode === 'zone' ? 'bg-alert-red text-black border-alert-red' : 'bg-tactical-panel text-alert-red border-alert-red/50 hover:bg-[rgba(255,51,102,0.1)]'}`}
      >
        DRAW EXCLUSION ZONE
      </button>

      {drawingMode === 'tripwire' && currentPoints.length > 0 && (
        <Polyline positions={currentPoints} color="#00f0ff" weight={2} dashArray="5, 10" />
      )}
      {drawingMode === 'zone' && currentPoints.length > 0 && (
        <Polygon positions={currentPoints} color="#ff3366" fillColor="#ff3366" fillOpacity={0.2} weight={2} dashArray="5, 5" />
      )}
    </div>
  );
}

function MapBoundsManager({ bops }) {
  const map = useMap();
  useEffect(() => {
    if (bops && bops.length > 0) {
      const bounds = L.latLngBounds(bops.map(b => [b.lat, b.lng]));
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [bops, map]);
  return null;
}

export default function MapView({ bops, alerts, cameras, onTripwireDrawn, onZoneDrawn }) {
  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'CRITICAL': return '#ff3366';
      case 'HIGH': return '#ffaa00';
      case 'MEDIUM': return '#ffaa00';
      case 'LOW': return '#00f0ff';
      default: return '#00f0ff';
    }
  };

  return (
    <div className="w-full h-full relative rounded-lg overflow-hidden border border-tactical-border">
      <MapContainer 
        center={[28.6139, 77.2090]} 
        zoom={13} 
        className="w-full h-full z-0"
        zoomControl={false}
        doubleClickZoom={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />

        <MapBoundsManager bops={bops} />

        {bops && bops.map(bop => (
          <Marker key={bop.id} position={[bop.lat, bop.lng]} icon={createBopIcon()}>
            <Popup className="font-mono text-xs">
              <strong className="text-cyan-accent">{bop.name}</strong><br />
              Status: <span className="text-alert-green">ONLINE</span><br />
              Cameras: {bop.cameraCount}
            </Popup>
          </Marker>
        ))}

        {alerts && alerts.map(alert => (
          alert.lat && alert.lng && (
            <CircleMarker 
              key={alert.id}
              center={[alert.lat, alert.lng]}
              radius={8}
              color={getSeverityColor(alert.severity)}
              fillColor={getSeverityColor(alert.severity)}
              fillOpacity={0.6}
              weight={2}
              className={`pulse-${alert.severity === 'CRITICAL' ? 'red' : alert.severity === 'HIGH' ? 'amber' : 'green'}`}
            >
              <Popup className="font-mono text-xs">
                <strong style={{color: getSeverityColor(alert.severity)}}>{alert.type}</strong><br/>
                {alert.description}<br/>
                Time: {new Date(alert.timestamp).toLocaleTimeString()}
              </Popup>
            </CircleMarker>
          )
        ))}

        <DrawTools onTripwireDrawn={onTripwireDrawn} onZoneDrawn={onZoneDrawn} />
      </MapContainer>
    </div>
  );
}
