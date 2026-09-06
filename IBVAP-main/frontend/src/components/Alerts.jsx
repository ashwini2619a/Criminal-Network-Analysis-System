import React, { useState, useEffect } from 'react';
import { ShieldAlert, AlertTriangle, AlertCircle, Info, ChevronDown, ChevronUp, CheckCircle, XCircle } from 'lucide-react';

const SeverityIcon = ({ severity }) => {
  switch (severity) {
    case 'CRITICAL': return <ShieldAlert className="w-5 h-5 text-alert-red" />;
    case 'HIGH': return <AlertTriangle className="w-5 h-5 text-alert-amber" />;
    case 'MEDIUM': return <AlertCircle className="w-5 h-5 text-alert-amber opacity-80" />;
    case 'LOW': return <Info className="w-5 h-5 text-cyan-accent" />;
    default: return <Info className="w-5 h-5 text-gray-400" />;
  }
};

const SeverityBorder = ({ severity }) => {
  switch (severity) {
    case 'CRITICAL': return 'border-l-4 border-l-alert-red';
    case 'HIGH': return 'border-l-4 border-l-alert-amber';
    case 'MEDIUM': return 'border-l-4 border-l-[#ffcc00]';
    case 'LOW': return 'border-l-4 border-l-cyan-accent';
    default: return 'border-l-4 border-l-gray-600';
  }
};

const AlertCard = ({ alert, onVerifyHash }) => {
  const [expanded, setExpanded] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState(null);

  const handleVerify = async (e) => {
    e.stopPropagation();
    setVerificationStatus('loading');
    try {
      const result = await onVerifyHash(alert.id, alert.sha256_hash);
      setVerificationStatus(result ? 'success' : 'failed');
    } catch (err) {
      setVerificationStatus('failed');
    }
  };

  return (
    <div 
      className={`bg-tactical-panel/80 border border-tactical-border/30 rounded mb-2 cursor-pointer transition-colors hover:bg-tactical-panel ${SeverityBorder({ severity: alert.severity })}`}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="p-3 flex items-start gap-3">
        <div className="mt-1">
          <SeverityIcon severity={alert.severity} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start">
            <h4 className="font-sans font-semibold text-sm text-white truncate">{alert.type}</h4>
            <span className="font-mono text-[10px] text-gray-400 whitespace-nowrap ml-2">
              {new Date(alert.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <div className="text-xs font-mono text-cyan-accent/80 mt-1 flex justify-between">
            <span>{alert.cameraName}</span>
            <span className="text-gray-500">{alert.bopName}</span>
          </div>
          <p className="text-xs text-gray-300 mt-2 line-clamp-2">{alert.description}</p>
        </div>
        <div>
          {expanded ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
        </div>
      </div>

      {expanded && (
        <div className="px-3 pb-3 pt-1 border-t border-tactical-border/20 bg-black/20">
          {alert.thumbnail_b64 && (
            <img 
              src={`data:image/jpeg;base64,${alert.thumbnail_b64}`} 
              alt="Alert snapshot" 
              className="w-full h-auto rounded border border-tactical-border/40 mt-2 mb-3"
            />
          )}
          
          <div className="grid grid-cols-2 gap-2 text-xs font-mono mb-3">
            <div className="bg-black/40 p-1.5 rounded text-gray-300">
              <span className="text-gray-500 block text-[9px] uppercase">Track ID</span>
              {alert.trackId || 'N/A'}
            </div>
            <div className="bg-black/40 p-1.5 rounded text-gray-300">
              <span className="text-gray-500 block text-[9px] uppercase">Confidence</span>
              {(alert.confidence * 100).toFixed(1)}%
            </div>
          </div>

          <div className="bg-black/60 p-2 rounded border border-tactical-border/30">
            <span className="text-gray-500 block text-[9px] font-mono uppercase mb-1">SHA-256 Signature</span>
            <div className="font-mono text-[10px] text-cyan-accent break-all select-all">
              {alert.sha256_hash || 'N/A'}
            </div>
            
            <div className="mt-3 flex items-center justify-between">
              <button 
                onClick={handleVerify}
                disabled={verificationStatus === 'loading'}
                className="bg-tactical-dark border border-cyan-accent/50 text-cyan-accent hover:bg-cyan-accent/10 px-3 py-1 rounded text-xs font-mono transition-colors disabled:opacity-50"
              >
                {verificationStatus === 'loading' ? 'VERIFYING...' : 'VERIFY HASH'}
              </button>
              
              {verificationStatus === 'success' && (
                <div className="flex items-center text-alert-green text-xs font-mono">
                  <CheckCircle className="w-4 h-4 mr-1" /> VERIFIED
                </div>
              )}
              {verificationStatus === 'failed' && (
                <div className="flex items-center text-alert-red text-xs font-mono">
                  <XCircle className="w-4 h-4 mr-1" /> TAMPERED
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default function Alerts({ alerts, onVerifyHash }) {
  const [filter, setFilter] = useState('ALL');
  
  useEffect(() => {
    const criticalAlerts = alerts.filter(a => a.severity === 'CRITICAL');
    if (criticalAlerts.length > 0) {
      try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        oscillator.type = 'square';
        oscillator.frequency.setValueAtTime(880, audioCtx.currentTime);
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        
        oscillator.start();
        setTimeout(() => oscillator.stop(), 200);
      } catch (e) {
        console.log("Audio not supported or auto-play blocked");
      }
    }
  }, [alerts.length]);

  const filteredAlerts = alerts.filter(a => filter === 'ALL' || a.severity === filter);

  return (
    <div className="flex flex-col h-full bg-tactical-panel backdrop-blur-md rounded-lg border border-tactical-border overflow-hidden">
      <div className="glass-header p-3 flex justify-between items-center shrink-0">
        <h2 className="font-mono font-bold text-cyan-accent tracking-wider flex items-center">
          <ShieldAlert className="w-4 h-4 mr-2" />
          ALERT FEED
        </h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-alert-red pulse-red"></div>
          <span className="text-[10px] font-mono text-gray-400">LIVE</span>
        </div>
      </div>
      
      <div className="p-2 border-b border-tactical-border/30 flex space-x-1 overflow-x-auto shrink-0 no-scrollbar">
        {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(level => (
          <button
            key={level}
            onClick={() => setFilter(level)}
            className={`px-2 py-1 text-[10px] font-mono rounded border ${
              filter === level 
                ? 'bg-cyan-accent/20 border-cyan-accent text-cyan-accent' 
                : 'bg-transparent border-tactical-border/50 text-gray-400 hover:border-cyan-accent/50'
            }`}
          >
            {level}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {filteredAlerts.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-500 font-mono text-xs opacity-50">
            <ShieldAlert className="w-8 h-8 mb-2" />
            NO ALERTS DETECTED
          </div>
        ) : (
          filteredAlerts.map(alert => (
            <AlertCard key={alert.id} alert={alert} onVerifyHash={onVerifyHash} />
          ))
        )}
      </div>
    </div>
  );
}
