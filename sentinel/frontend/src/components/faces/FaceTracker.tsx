import React, { useState, useEffect, useRef } from 'react';
import {
  Upload,
  ScanFace,
  Search,
  Download,
  Trash2,
  Eye,
  Shield,
  Hash,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Clock
} from 'lucide-react';
import {
  uploadFaceImage,
  registerFaceProfile,
  searchFaceMatches,
  getAllFaceProfiles,
  deleteFaceProfile,
  getFaceMatchReport,
  scanAllEvidenceFaces
} from '../../lib/api';
import { DetectedFace, FaceProfile, FaceMatchResult, FaceScanSummary } from '../../types';

export const FaceTracker: React.FC = () => {
  const [profiles, setProfiles] = useState<FaceProfile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<FaceProfile | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [detectedFaces, setDetectedFaces] = useState<DetectedFace[]>([]);
  const [registerName, setRegisterName] = useState('');
  const [minSimilarity, setMinSimilarity] = useState(60);
  const [scanSummary, setScanSummary] = useState<FaceScanSummary | null>(null);
  const [scanning, setScanning] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const loadProfiles = async () => {
    try {
      const res = await getAllFaceProfiles();
      setProfiles(res);
    } catch (err) {
      console.error('Failed to load profiles', err);
    }
  };

  useEffect(() => {
    loadProfiles();
  }, []);

  const handleFileSelect = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    const imageUrl = URL.createObjectURL(file);
    setUploadedImage(imageUrl);
    
    try {
      setUploading(true);
      const res = await uploadFaceImage(file);
      if (res && res.faces && res.faces.length > 0) {
        setDetectedFaces(res.faces);
        drawBoundingBoxes(imageUrl, res.faces);
      } else {
        alert('Photo uploaded and sealed with SHA-256. No distinct faces detected in photo.');
      }
    } catch (err: any) {
      console.error('Upload failed:', err);
      alert('Face upload failed: ' + (err.message || err));
    } finally {
      setUploading(false);
    }
  };

  const drawBoundingBoxes = (imageUrl: string, faces: DetectedFace[]) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
      
      faces.forEach((face, idx) => {
        const box = face.bounding_box || ((face as any).bbox ? {
          x: (face as any).bbox.left || 0,
          y: (face as any).bbox.top || 0,
          width: ((face as any).bbox.right - (face as any).bbox.left) || 80,
          height: ((face as any).bbox.bottom - (face as any).bbox.top) || 80
        } : { x: 20, y: 20, width: 100, height: 100 });

        const { x, y, width, height } = box;
        ctx.strokeStyle = '#38bdf8'; // sky-400
        ctx.lineWidth = 3;
        ctx.strokeRect(x, y, width, height);
        
        ctx.fillStyle = '#0284c7'; // sky-600
        ctx.fillRect(x, Math.max(0, y - 20), width, 20);
        ctx.fillStyle = '#ffffff';
        ctx.font = '12px monospace';
        const conf = face.confidence ? Math.round(face.confidence * 100) : 95;
        ctx.fillText(`FACE ${idx + 1} (${conf}%)`, x + 4, Math.max(14, y - 6));
      });
    };
    img.src = imageUrl;
  };

  const handleRegister = async (faceId: string) => {
    if (!registerName) {
      alert('Please enter a name or label');
      return;
    }
    try {
      await registerFaceProfile(faceId, registerName);
      setRegisterName('');
      setUploadedImage(null);
      setDetectedFaces([]);
      await loadProfiles();
      alert('Profile registered successfully');
    } catch (err) {
      console.error('Registration failed:', err);
      alert('Failed to register face profile');
    }
  };

  const handleScan = async (faceId: string) => {
    try {
      setScanning(true);
      const res = await scanAllEvidenceFaces(faceId, minSimilarity);
      setScanSummary(res);
    } catch (err) {
      console.error('Scan failed:', err);
      alert('Scan failed');
    } finally {
      setScanning(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Delete this profile?')) return;
    try {
      await deleteFaceProfile(id);
      if (selectedProfile?.id === id) {
        setSelectedProfile(null);
        setScanSummary(null);
      }
      await loadProfiles();
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const handleExport = async (faceId: string) => {
    try {
      const blob = await getFaceMatchReport(faceId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `face_match_report_${faceId}.pdf`;
      a.click();
    } catch (err) {
      console.error('Export failed:', err);
      alert('Failed to export report');
    }
  };

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in flex flex-col h-full">
      <div className="border-b border-slate-200/90 pb-4">
        <h1 className="text-xl font-bold tracking-tight text-slate-900 flex items-center space-x-2">
          <ScanFace className="w-6 h-6 text-sky-600" />
          <span>Biometric Face Tracker</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1 font-mono">
          AI-powered facial recognition across evidentiary assets. Cross-reference suspect faces with CCTV, social media, and surveillance feeds.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0 overflow-y-auto">
        {/* Left Column */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5">
            <h2 className="text-lg font-bold text-slate-900 tracking-tight flex items-center space-x-2 mb-4">
              <Upload className="w-5 h-5 text-sky-600" />
              <span>Reference Face Upload</span>
            </h2>
            
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragging(false);
                handleFileSelect(e.dataTransfer.files);
              }}
              onClick={() => fileInputRef.current?.click()}
              className={`p-6 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-300 flex flex-col items-center justify-center text-center ${
                isDragging ? 'border-sky-500 bg-sky-50' : 'border-slate-300 hover:border-sky-400 bg-slate-50 hover:bg-sky-50/50'
              }`}
            >
              <input ref={fileInputRef} type="file" className="hidden" accept=".jpg,.jpeg,.png" onChange={(e) => handleFileSelect(e.target.files)} />
              {uploading ? <Loader2 className="w-8 h-8 text-sky-600 animate-spin mb-2" /> : <Upload className="w-8 h-8 text-sky-600 mb-2" />}
              <div className="text-sm font-bold text-slate-900">{uploading ? 'Processing...' : 'Drag & Drop Face Image'}</div>
              <div className="text-xs text-slate-500 mt-1">Accepts JPG, PNG up to 10MB</div>
            </div>

            {uploadedImage && (
              <div className="mt-4 space-y-4">
                <div className="relative w-full rounded-lg overflow-hidden border border-slate-200 bg-slate-100 flex justify-center">
                  <canvas ref={canvasRef} className="max-w-full max-h-64 object-contain" />
                </div>
                
                {detectedFaces.map((face, idx) => (
                  <div key={face.face_id} className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-3">
                    <div className="flex justify-between items-center text-sm font-bold">
                      <span>Face #{idx + 1}</span>
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                        CONFIDENCE: {Math.round(face.confidence * 100)}%
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        placeholder="Suspect Name / Label"
                        className="flex-1 text-sm border border-slate-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-sky-500"
                        value={registerName}
                        onChange={(e) => setRegisterName(e.target.value)}
                      />
                      <button
                        onClick={() => handleRegister(face.face_id)}
                        className="bg-sky-600 hover:bg-sky-700 text-white px-3 py-1.5 rounded-lg text-sm font-semibold whitespace-nowrap transition-colors"
                      >
                        Register Face
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Registered Faces Table Summary */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 flex flex-col min-h-[300px]">
            <h2 className="text-[10px] font-mono uppercase tracking-widest text-slate-400 font-extrabold mb-3">Registered Profiles ({profiles.length})</h2>
            <div className="flex-1 overflow-y-auto pr-1">
              <div className="space-y-2">
                {profiles.map(p => (
                  <div key={p.id} onClick={() => { setSelectedProfile(p); setScanSummary(null); }} className={`p-2.5 rounded-lg border flex items-center justify-between cursor-pointer transition-colors ${selectedProfile?.id === p.id ? 'border-sky-500 bg-sky-50' : 'border-slate-200 hover:bg-slate-50'}`}>
                    <div className="flex items-center space-x-3">
                      <img src={p.thumbnail_url} alt={p.label} className="w-10 h-10 rounded-md object-cover border border-slate-300" />
                      <div>
                        <div className="font-bold text-slate-900 text-sm">{p.label}</div>
                        <div className="text-[10px] font-mono text-slate-500">{p.total_matches} matches</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button onClick={(e) => { e.stopPropagation(); handleDelete(p.id); }} className="p-1.5 text-slate-400 hover:text-rose-600 transition-colors">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="lg:col-span-7">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 h-full flex flex-col">
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-4">
              <h2 className="text-lg font-bold text-slate-900 tracking-tight flex items-center space-x-2">
                <Search className="w-5 h-5 text-sky-600" />
                <span>Evidence Match Analysis</span>
              </h2>
              {selectedProfile && (
                <button onClick={() => handleExport(selectedProfile.id)} className="bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 px-3 py-1.5 rounded-lg text-sm font-semibold flex items-center space-x-2 transition-colors">
                  <Download className="w-4 h-4" />
                  <span>Export Report</span>
                </button>
              )}
            </div>

            {selectedProfile ? (
              <div className="flex-1 flex flex-col">
                <div className="flex items-center justify-between bg-slate-50 p-4 rounded-lg border border-slate-200 mb-4">
                  <div className="flex items-center space-x-4">
                    <img src={selectedProfile.thumbnail_url} alt={selectedProfile.label} className="w-12 h-12 rounded-lg object-cover border-2 border-sky-300" />
                    <div>
                      <div className="font-bold text-slate-900">{selectedProfile.label}</div>
                      <div className="text-xs font-mono text-slate-500">ID: {selectedProfile.id}</div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] font-mono uppercase tracking-widest text-slate-500">Threshold: {minSimilarity}%</span>
                      <input type="range" min="40" max="95" value={minSimilarity} onChange={(e) => setMinSimilarity(Number(e.target.value))} className="w-24 accent-sky-600" />
                    </div>
                    <button onClick={() => handleScan(selectedProfile.id)} disabled={scanning} className="bg-sky-600 hover:bg-sky-700 text-white px-4 py-2 rounded-lg text-sm font-semibold flex items-center space-x-2 transition-colors disabled:opacity-50">
                      {scanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <ScanFace className="w-4 h-4" />}
                      <span>{scanning ? 'Scanning...' : 'Scan All Evidence'}</span>
                    </button>
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto pr-1">
                  {scanSummary ? (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between text-[10px] font-mono uppercase text-slate-500">
                        <span>{scanSummary.total_matches} MATCHES FOUND IN {scanSummary.total_evidence_scanned} ASSETS</span>
                        <span>DURATION: {scanSummary.scan_duration_ms}ms</span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {scanSummary.matches.map(m => (
                          <div key={m.match_id} className="p-3 rounded-lg border border-slate-200 bg-white shadow-2xs space-y-3">
                            <div className="flex justify-between items-start">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${
                                m.similarity_score > 85 ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                                m.similarity_score > 60 ? 'bg-amber-50 text-amber-700 border-amber-200' :
                                'bg-rose-50 text-rose-700 border-rose-200'
                              }`}>
                                {m.similarity_score.toFixed(1)}% MATCH
                              </span>
                              <span className="text-[10px] font-mono text-slate-400" title={m.blockchain_hash}>
                                <Hash className="w-3 h-3 inline mr-1" />
                                {m.blockchain_hash ? m.blockchain_hash.slice(0, 8) : 'NO-HASH'}
                              </span>
                            </div>
                            <img src={m.matched_image_url} alt="Match" className="w-full h-32 object-cover rounded-md border border-slate-200" />
                            <div className="text-xs font-mono truncate font-medium text-slate-700">
                              📄 {m.evidence_file_name}
                            </div>
                            <div className="text-[10px] text-slate-500 flex items-center">
                              <Clock className="w-3 h-3 mr-1" /> {new Date(m.source_upload_timestamp).toLocaleString()}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="h-full flex flex-col items-center justify-center text-slate-400">
                      <Search className="w-12 h-12 mb-3 opacity-50" />
                      <div className="text-sm font-bold">Ready to scan evidence vault</div>
                      <div className="text-xs">Select "Scan All Evidence" to begin</div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-400">
                <ScanFace className="w-12 h-12 mb-3 opacity-50" />
                <div className="text-sm font-bold">Select a face profile to view matches</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
