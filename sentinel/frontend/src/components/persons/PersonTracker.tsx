import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  PersonStanding,
  Upload,
  Video,
  Play,
  Square,
  Camera,
  Activity,
  History,
  Download,
  AlertTriangle,
  Loader2
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip
} from 'recharts';
import {
  detectPersonsInImage,
  detectPersonsInFrame,
  captureAndSaveFrame,
  getPersonDetectionHistory,
  batchDetectPersons,
  exportDetectionLog
} from '../../lib/api';
import { PersonDetectionResult, LiveDetectionFrame, DetectedPerson } from '../../types';

export const PersonTracker: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'evidence' | 'live'>('evidence');
  
  // Evidence State
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [evidenceResult, setEvidenceResult] = useState<PersonDetectionResult | null>(null);
  const [evidenceImageUrl, setEvidenceImageUrl] = useState<string | null>(null);
  const evidenceCanvasRef = useRef<HTMLCanvasElement>(null);
  
  // Live State
  const [isLiveActive, setIsLiveActive] = useState(false);
  const isLiveActiveRef = useRef(false);
  const isProcessingRef = useRef(false);
  const [fps, setFps] = useState(0);
  const [chartData, setChartData] = useState<any[]>([]);
  const [liveLog, setLiveLog] = useState<any[]>([]);
  const videoRef = useRef<HTMLVideoElement>(null);
  const liveCanvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const loopRef = useRef<number | null>(null);

  const drawBoundingBox = (ctx: CanvasRenderingContext2D, bbox: any, index: number, confidence: number, mode: 'live'|'uploaded') => {
    if (!bbox) return;
    const { x, y, width, height } = bbox;
    const isLive = mode === 'live';
    const color = isLive ? '#22c55e' : '#ef4444'; // Bright GREEN for live, Bright RED for uploaded
    const fillStyle = isLive ? 'rgba(34, 197, 94, 0.16)' : 'rgba(239, 68, 68, 0.16)';
    
    // Translucent Target Fill
    ctx.fillStyle = fillStyle;
    ctx.fillRect(x, y, width, height);
    
    // Perimeter Box Outline
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.strokeRect(x, y, width, height);
    
    // High-visibility Tactical Corner Brackets
    ctx.lineWidth = 4;
    const l = Math.max(8, Math.min(22, width / 4, height / 4));
    ctx.beginPath();
    // Top-left
    ctx.moveTo(x, y + l); ctx.lineTo(x, y); ctx.lineTo(x + l, y);
    // Top-right
    ctx.moveTo(x + width - l, y); ctx.lineTo(x + width, y); ctx.lineTo(x + width, y + l);
    // Bottom-left
    ctx.moveTo(x, y + height - l); ctx.lineTo(x, y + height); ctx.lineTo(x + l, y + height);
    // Bottom-right
    ctx.moveTo(x + width - l, y + height); ctx.lineTo(x + width, y + height); ctx.lineTo(x + width, y + height - l);
    ctx.stroke();

    // High-visibility Identification Pill
    ctx.fillStyle = color;
    const label = isLive ? `LIVE #${index}` : `PERSON #${index}`;
    const confText = `${label} ${Math.round(confidence * 100)}%`;
    ctx.font = 'bold 12px ui-monospace, monospace';
    const textWidth = ctx.measureText(confText).width;
    const pillHeight = 22;
    const pillY = y >= pillHeight + 4 ? y - pillHeight - 2 : y + 2;
    ctx.fillRect(x, pillY, textWidth + 16, pillHeight);
    
    // White text
    ctx.fillStyle = '#ffffff';
    ctx.fillText(confText, x + 8, pillY + 15);
  };

  // --- EVIDENCE LOGIC ---
  const handleEvidenceUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    const url = URL.createObjectURL(file);
    setEvidenceImageUrl(url);
    
    try {
      setUploading(true);
      const res = await detectPersonsInImage(file);
      setEvidenceResult(res);
      
      // Draw immediately after image loads
      const img = new Image();
      img.onload = () => {
        const cvs = evidenceCanvasRef.current;
        if (!cvs) return;
        const ctx = cvs.getContext('2d');
        if (!ctx) return;
        cvs.width = img.width;
        cvs.height = img.height;
        ctx.drawImage(img, 0, 0);
        if (res?.persons && Array.isArray(res.persons)) {
          res.persons.forEach((p: any) => {
            drawBoundingBox(ctx, p.bounding_box, p.person_index, p.confidence, 'uploaded');
          });
        }
      };
      img.src = url;
    } catch (err) {
      console.error('Evidence detection error:', err);
      alert('Detection failed. Please check backend connection.');
    } finally {
      setUploading(false);
    }
  };

  // --- LIVE LOGIC ---
  const scheduleNextLiveFrame = (delayMs: number = 120) => {
    if (!isLiveActiveRef.current) return;
    if (loopRef.current) clearTimeout(loopRef.current);
    loopRef.current = window.setTimeout(processLiveFrame, delayMs);
  };

  const startLive = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 } }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play().catch(() => {});
      }
      streamRef.current = stream;
      isLiveActiveRef.current = true;
      setIsLiveActive(true);
      scheduleNextLiveFrame(150);
    } catch (err) {
      console.error('Camera access error:', err);
      alert('Camera access denied or unavailable.');
    }
  };

  const stopLive = () => {
    isLiveActiveRef.current = false;
    setIsLiveActive(false);
    if (loopRef.current) {
      clearTimeout(loopRef.current);
      loopRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    const canvas = liveCanvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx?.clearRect(0, 0, canvas.width, canvas.height);
    }
  };

  useEffect(() => {
    return () => {
      stopLive();
    };
  }, []);

  const processLiveFrame = async () => {
    if (!isLiveActiveRef.current || !videoRef.current || !liveCanvasRef.current) return;
    if (isProcessingRef.current) {
      scheduleNextLiveFrame(100);
      return;
    }
    
    const video = videoRef.current;
    const canvas = liveCanvasRef.current;
    if (video.videoWidth === 0 || video.videoHeight === 0 || video.readyState < 2) {
      scheduleNextLiveFrame(100);
      return;
    }

    if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    }

    isProcessingRef.current = true;
    const t0 = performance.now();

    // Use offscreen canvas for frame capture to prevent flicker
    const offscreen = document.createElement('canvas');
    offscreen.width = video.videoWidth;
    offscreen.height = video.videoHeight;
    const offCtx = offscreen.getContext('2d');
    if (!offCtx) {
      isProcessingRef.current = false;
      scheduleNextLiveFrame(120);
      return;
    }
    offCtx.drawImage(video, 0, 0, offscreen.width, offscreen.height);

    offscreen.toBlob(async (blob) => {
      try {
        if (!blob || !isLiveActiveRef.current) return;
        const res = await detectPersonsInFrame(blob);
        
        const ctx = canvas.getContext('2d');
        if (ctx && isLiveActiveRef.current) {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          if (res?.persons && Array.isArray(res.persons)) {
            res.persons.forEach((p: any) => {
              drawBoundingBox(ctx, p.bounding_box, p.person_index, p.confidence, 'live');
            });
          }
        }
        
        const elapsed = performance.now() - t0;
        const currentFps = Math.max(1, Math.round(1000 / elapsed));
        setFps(currentFps);
        
        const timestamp = new Date().toLocaleTimeString();
        const count = res?.persons_count ?? res?.persons?.length ?? 0;
        setChartData(prev => [...prev.slice(-30), { time: timestamp, count }]);
        
        if (count > 0) {
          setLiveLog(prev => [{ time: timestamp, count }, ...prev.slice(0, 19)]);
        }
      } catch (err) {
        console.warn('Frame detection skipped:', err);
      } finally {
        isProcessingRef.current = false;
        if (isLiveActiveRef.current) {
          scheduleNextLiveFrame(120);
        }
      }
    }, 'image/jpeg', 0.7);
  };

  const captureFrame = async () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext('2d')?.drawImage(videoRef.current, 0, 0);
    canvas.toBlob(async (blob) => {
      if (blob) {
        await captureAndSaveFrame(blob);
        alert('Live frame captured with cryptographic seal.');
      }
    }, 'image/jpeg');
  };

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in flex flex-col h-full">
      <div className="border-b border-slate-200/90 pb-4 flex justify-between items-end">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 flex items-center space-x-2">
            <PersonStanding className="w-6 h-6 text-sky-600" />
            <span>Tactical Person Tracker</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1 font-mono">
            YOLOv8-powered human detection. Analyze static evidence or monitor live CCTV/webcam feeds.
          </p>
        </div>
        <div className="flex space-x-2">
          <button onClick={() => setActiveTab('evidence')} className={`px-4 py-2 text-xs font-bold font-mono rounded-lg transition-colors ${activeTab === 'evidence' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-slate-50 text-slate-600 border border-slate-200'}`}>
            📸 Evidence Analysis
          </button>
          <button onClick={() => setActiveTab('live')} className={`px-4 py-2 text-xs font-bold font-mono rounded-lg transition-colors ${activeTab === 'live' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-slate-50 text-slate-600 border border-slate-200'}`}>
            🎥 Live Camera
          </button>
        </div>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto">
        {activeTab === 'evidence' ? (
          <div className="space-y-6">
            <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5">
              <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setIsDragging(false);
                  handleEvidenceUpload(e.dataTransfer.files);
                }}
                className={`p-6 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-300 flex flex-col items-center justify-center text-center ${
                  isDragging ? 'border-red-500 bg-red-50' : 'border-slate-300 hover:border-red-400 bg-slate-50 hover:bg-red-50/50'
                }`}
              >
                <input type="file" className="hidden" id="file-upload" accept="image/*" onChange={(e) => handleEvidenceUpload(e.target.files)} />
                <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
                  {uploading ? <Loader2 className="w-8 h-8 text-red-500 animate-spin mb-2" /> : <Upload className="w-8 h-8 text-red-500 mb-2" />}
                  <div className="text-sm font-bold text-slate-900">{uploading ? 'Analyzing Image...' : 'Upload Evidence Image'}</div>
                </label>
              </div>

              {evidenceImageUrl && (
                <div className="mt-6">
                  <div className="relative rounded-lg overflow-hidden border border-slate-200 bg-slate-100 flex justify-center">
                    <canvas ref={evidenceCanvasRef} className="max-w-full h-auto max-h-[60vh] object-contain" />
                  </div>
                  {evidenceResult && (
                    <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-lg">
                      <div className="text-[10px] font-mono uppercase text-slate-500 font-bold mb-2">Detection Summary</div>
                      <div className="grid grid-cols-3 gap-4 font-mono text-sm">
                        <div>
                          <div className="text-slate-400 text-[10px]">TOTAL PERSONS</div>
                          <div className="font-bold text-red-600 text-lg">{evidenceResult.total_persons}</div>
                        </div>
                        <div>
                          <div className="text-slate-400 text-[10px]">PROCESSING TIME</div>
                          <div className="font-bold text-slate-800">{evidenceResult.processing_time_ms}ms</div>
                        </div>
                        <div>
                          <div className="text-slate-400 text-[10px]">SHA-256 HASH</div>
                          <div className="font-bold text-slate-800 truncate text-xs">{evidenceResult.sha256_hash?.slice(0,16)}</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full">
            <div className="lg:col-span-8 bg-white rounded-xl border border-slate-200 shadow-xs p-5 flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <div className="flex space-x-2">
                  <button onClick={isLiveActive ? stopLive : startLive} className={`px-4 py-2 rounded-lg text-sm font-semibold flex items-center space-x-2 text-white ${isLiveActive ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}`}>
                    {isLiveActive ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    <span>{isLiveActive ? 'Stop Stream' : 'Start Camera'}</span>
                  </button>
                  <button onClick={captureFrame} disabled={!isLiveActive} className="px-4 py-2 rounded-lg text-sm font-semibold flex items-center space-x-2 bg-slate-100 hover:bg-slate-200 text-slate-700 disabled:opacity-50 border border-slate-300">
                    <Camera className="w-4 h-4" />
                    <span>Capture Frame</span>
                  </button>
                </div>
                <div className="text-xs font-mono font-bold bg-slate-100 px-3 py-1.5 rounded-full text-slate-600 border border-slate-200">
                  {fps} FPS
                </div>
              </div>

              <div className="relative flex-1 rounded-lg overflow-hidden bg-slate-950 flex items-center justify-center border border-slate-300 min-h-[420px]">
                <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-contain" />
                <canvas ref={liveCanvasRef} className="absolute inset-0 w-full h-full object-contain pointer-events-none" />
                {!isLiveActive && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400 bg-slate-900 z-10">
                    <Video className="w-12 h-12 mb-2 opacity-60" />
                    <span className="font-mono text-sm tracking-wider font-semibold">LIVE CAMERA OFFLINE</span>
                    <span className="font-mono text-xs text-slate-500 mt-1">Click "Start Camera" to initiate live surveillance detection</span>
                  </div>
                )}
              </div>
            </div>

            <div className="lg:col-span-4 flex flex-col space-y-4">
              <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 flex-1 min-h-[200px]">
                <h2 className="text-[10px] font-mono uppercase tracking-widest text-slate-400 font-extrabold mb-3">Live Crowd Density</h2>
                <ResponsiveContainer width="100%" height="80%">
                  <AreaChart data={chartData}>
                    <XAxis dataKey="time" hide />
                    <YAxis hide />
                    <Tooltip contentStyle={{ fontSize: '10px', fontFamily: 'monospace' }} />
                    <Area type="stepAfter" dataKey="count" stroke="#22c55e" fill="rgba(34, 197, 94, 0.2)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 flex-1 overflow-y-auto">
                <h2 className="text-[10px] font-mono uppercase tracking-widest text-slate-400 font-extrabold mb-3 flex justify-between">
                  <span>Detection Log</span>
                  <Activity className="w-3.5 h-3.5 text-green-500 animate-pulse" />
                </h2>
                <div className="space-y-2">
                  {liveLog.map((log, i) => (
                    <div key={i} className="flex justify-between items-center text-xs font-mono p-2 rounded bg-slate-50 border border-slate-100">
                      <span className="text-slate-400">{log.time}</span>
                      <span className="font-bold text-slate-700">{log.count} Person(s) Detected</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
