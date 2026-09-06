import React, { useRef, useEffect } from 'react';
import { Camera, Radio } from 'lucide-react';

export default function VideoFeed({ cameraId, cameraName, isMain, overlayData, onClick }) {
  const canvasRef = useRef(null);
  const overlayRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    // In a real scenario, this connects to the backend streaming WebSocket
    const wsBase = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const wsUrl = `${wsBase}/ws/stream/${cameraId}`;
    
    try {
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onmessage = (event) => {
        if (typeof event.data === 'string' && event.data.startsWith('data:image/jpeg;base64,')) {
          const img = new Image();
          img.onload = () => {
            if (canvasRef.current) {
              const ctx = canvasRef.current.getContext('2d');
              ctx.drawImage(img, 0, 0, canvasRef.current.width, canvasRef.current.height);
            }
          };
          img.src = event.data;
        }
      };
    } catch (e) {
      console.error("Error connecting to video stream:", e);
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [cameraId]);

  useEffect(() => {
    if (!overlayRef.current || !overlayData) return;
    
    const canvas = overlayRef.current;
    const ctx = canvas.getContext('2d');
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (overlayData.bounding_boxes) {
      overlayData.bounding_boxes.forEach(box => {
        ctx.strokeStyle = box.color || '#ff3366';
        ctx.lineWidth = 2;
        ctx.strokeRect(box.x, box.y, box.w, box.h);
        
        ctx.fillStyle = box.color || '#ff3366';
        ctx.font = '12px "JetBrains Mono"';
        ctx.fillText(box.label || 'Unknown', box.x, box.y - 5);
      });
    }

    if (overlayData.tripwires) {
      overlayData.tripwires.forEach(line => {
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(line.x1, line.y1);
        ctx.lineTo(line.x2, line.y2);
        ctx.stroke();
      });
    }

  }, [overlayData]);

  return (
    <div 
      className={`relative bg-black rounded-lg overflow-hidden border border-tactical-border cursor-pointer group ${isMain ? 'w-full h-full' : 'w-full aspect-video'} transition-all`}
      onClick={onClick}
    >
      <canvas 
        ref={canvasRef} 
        width={1920} 
        height={1080} 
        className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
      />
      
      <canvas
        ref={overlayRef}
        width={1920}
        height={1080}
        className="absolute inset-0 w-full h-full object-cover pointer-events-none"
      />

      <div className="absolute top-2 left-2 flex items-center space-x-2 bg-black/60 backdrop-blur-sm px-2 py-1 rounded border border-tactical-border/50">
        <Camera className="w-4 h-4 text-cyan-accent" />
        <span className="text-xs font-mono text-cyan-accent font-bold">{cameraName}</span>
      </div>

      <div className="absolute top-2 right-2 flex items-center space-x-2 bg-black/60 backdrop-blur-sm px-2 py-1 rounded border border-tactical-border/50">
        <div className="w-2 h-2 rounded-full bg-alert-red pulse-red"></div>
        <span className="text-xs font-mono text-white">REC</span>
        <span className="text-xs font-mono text-cyan-accent ml-2">30 FPS</span>
      </div>

      {!isMain && (
        <div className="absolute bottom-2 left-2 flex items-center space-x-1">
           <Radio className="w-3 h-3 text-alert-green pulse-green" />
           <span className="text-[10px] font-mono text-alert-green">LIVE</span>
        </div>
      )}
      
      <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(0,240,255,0.03)_1px,transparent_1px)] bg-[length:100%_4px]"></div>
    </div>
  );
}
