import React, { useState, useEffect, useRef } from 'react';
import { Activity, Camera, Shield, Clock, Wifi } from 'lucide-react';
import Alerts from './components/Alerts';
import MapView from './components/MapView';
import VideoFeed from './components/VideoFeed';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

function App() {
  const [time, setTime] = useState(new Date());
  const [connected, setConnected] = useState(false);
  const [cameras, setCameras] = useState([]);
  const [activeCameraId, setActiveCameraId] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [bops, setBops] = useState([]);
  const [stats, setStats] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch initial data
  useEffect(() => {
    const fetchCameras = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/cameras`);
        if (res.ok) {
          const data = await res.json();
          setCameras(data);
          if (data.length > 0) setActiveCameraId(data[0].id);
        } else {
          setCameras([]);
        }
      } catch (err) {
        console.error("Failed to fetch cameras", err);
        setCameras([]);
      }
    };

    const fetchBops = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/bops`);
        if (res.ok) {
          const data = await res.json();
          setBops(data);
        } else {
          setBops([]);
        }
      } catch (err) {
        console.error("Failed to fetch bops", err);
        setBops([]);
      }
    };

    fetchCameras();
    fetchBops();
  }, []);

  // Fetch stats periodically
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/stats`);
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (err) {
        console.error("Failed to fetch stats", err);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket for alerts
  useEffect(() => {
    let reconnectAttempts = 0;

    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(`${WS_BASE}/ws/alerts`);
        wsRef.current = ws;

        ws.onopen = () => {
          setConnected(true);
          reconnectAttempts = 0;
        };

        ws.onmessage = (event) => {
          try {
            const newAlert = JSON.parse(event.data);
            setAlerts((prev) => [newAlert, ...prev].slice(0, 200));
          } catch (err) {
            console.error("Failed to parse alert", err);
          }
        };

        ws.onclose = () => {
          setConnected(false);
          // Exponential backoff
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
          reconnectAttempts++;
          reconnectTimeoutRef.current = setTimeout(connectWebSocket, delay);
        };

        ws.onerror = (err) => {
          console.error("WebSocket error", err);
          ws.close();
        };
      } catch (err) {
        console.error("Failed to connect websocket", err);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  const handleVerifyHash = async (alertId, hash) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_id: alertId, test_hash: hash })
      });
      if (res.ok) {
        const data = await res.json();
        return data.verified === true;
      }
      return false;
    } catch (err) {
      console.error("Failed to verify hash", err);
      return false;
    }
  };

  const handleTripwireDrawn = async (coords) => {
    console.log("Tripwire drawn:", coords);
    try {
      await fetch(`${API_BASE}/api/v1/zones/tripwire`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ points: coords })
      });
    } catch (err) {
      console.error("Failed to post tripwire", err);
    }
  };

  const handleZoneDrawn = async (coords, type) => {
    console.log("Zone drawn:", coords, type);
    try {
      await fetch(`${API_BASE}/api/v1/zones/${type || 'inclusion'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ points: coords, type })
      });
    } catch (err) {
      console.error("Failed to post zone", err);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-tactical-dark text-white overflow-hidden p-2 gap-2">
      
      <header className="glass-panel h-14 rounded-lg flex items-center justify-between px-4 shrink-0 z-10">
        <div className="flex items-center space-x-3">
          <Shield className="w-6 h-6 text-cyan-accent" />
          <h1 className="font-mono font-bold text-lg tracking-widest text-cyan-accent drop-shadow-[0_0_8px_rgba(0,240,255,0.8)]">
            IBVAP // COMMAND & CONTROL
          </h1>
        </div>

        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <Camera className="w-4 h-4 text-gray-400" />
            <span className="font-mono text-sm">
              <span className={cameras.length > 0 ? "text-alert-green" : "text-alert-red"}>{cameras.length}</span> / {cameras.length} ONLINE
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-gray-400" />
            <span className="font-mono text-sm">THREAT: <span className="text-alert-amber">ELEVATED</span></span>
          </div>
          
          <div className="h-6 w-px bg-tactical-border mx-2"></div>

          <div className="flex items-center space-x-3 font-mono text-sm">
            <Clock className="w-4 h-4 text-cyan-accent" />
            <span>{time.toLocaleTimeString('en-US', { hour12: false })}</span>
            <span className="text-gray-500 text-xs">{time.toLocaleDateString()}</span>
          </div>

          <div className="flex items-center space-x-2 bg-black/40 px-3 py-1 rounded-full border border-tactical-border/50">
            <Wifi className={`w-3 h-3 ${connected ? 'text-alert-green' : 'text-alert-red'}`} />
            <span className={`text-[10px] font-mono font-bold ${connected ? 'text-alert-green' : 'text-alert-red'}`}>
              {connected ? 'SYS SECURE' : 'DISCONNECTED'}
            </span>
          </div>
        </div>
      </header>

      <div className="flex flex-1 gap-2 min-h-0">
        
        <div className="w-[20%] flex flex-col gap-2 shrink-0">
          <div className="glass-panel p-2 flex items-center justify-between rounded-t-lg border-b-0 pb-1">
             <span className="font-mono text-xs text-cyan-accent font-bold">FEEDS // SURVEILLANCE</span>
             <span className="font-mono text-[10px] text-gray-400">GRID: 2x2</span>
          </div>
          <div className="flex-1 glass-panel rounded-b-lg p-2 overflow-y-auto no-scrollbar grid grid-cols-1 gap-2 content-start">
            {cameras.map(cam => (
              <div 
                key={cam.id} 
                className={`relative rounded overflow-hidden transition-all ${activeCameraId === cam.id ? 'ring-2 ring-cyan-accent ring-offset-1 ring-offset-tactical-dark' : 'opacity-80 hover:opacity-100'}`}
              >
                <VideoFeed 
                  cameraId={cam.id}
                  cameraName={cam.name}
                  isMain={false}
                  onClick={() => setActiveCameraId(cam.id)}
                />
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1 flex flex-col gap-2 min-w-0">
          <div className="h-[60%] glass-panel rounded-lg p-1 relative">
            {activeCameraId && (
              <VideoFeed 
                cameraId={activeCameraId}
                cameraName={cameras.find(c => c.id === activeCameraId)?.name || 'UNKNOWN'}
                isMain={true}
                overlayData={{
                  bounding_boxes: [],
                  tripwires: []
                }}
              />
            )}
            <div className="absolute bottom-4 left-4 right-4 flex justify-between pointer-events-none">
              <div className="bg-black/50 backdrop-blur px-3 py-1.5 rounded border border-tactical-border/50 font-mono text-xs">
                <span className="text-gray-400 block mb-1 text-[10px]">AI ANALYSIS</span>
                <span className="text-alert-red font-bold animate-pulse">MONITORING</span>
              </div>
            </div>
          </div>
          
          <div className="h-[40%] glass-panel rounded-lg p-1">
             <MapView 
               bops={bops}
               alerts={alerts}
               cameras={cameras}
               onTripwireDrawn={handleTripwireDrawn}
               onZoneDrawn={handleZoneDrawn}
             />
          </div>
        </div>

        <div className="w-[25%] shrink-0">
          <Alerts alerts={alerts} onVerifyHash={handleVerifyHash} />
        </div>

      </div>
    </div>
  );
}

export default App;
