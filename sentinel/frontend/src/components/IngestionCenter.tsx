import React, { useState } from 'react';
import { UploadCloud, FileText, FileSpreadsheet, Image as ImageIcon, CheckCircle, AlertCircle, Copy, Search } from 'lucide-react';

export default function IngestionCenter() {
  const [isDragging, setIsDragging] = useState(false);
  const [uploads, setUploads] = useState<any[]>([]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = (files: File[]) => {
    const newUploads = files.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: (file.size / 1024 / 1024).toFixed(2) + ' MB',
      type: file.type,
      progress: 0,
      status: 'uploading',
      hash: ''
    }));

    setUploads(prev => [...newUploads, ...prev]);

    newUploads.forEach(upload => {
      let progress = 0;
      const interval = setInterval(() => {
        progress += Math.random() * 20;
        if (progress >= 100) {
          progress = 100;
          clearInterval(interval);
          setUploads(current => current.map(u => 
            u.id === upload.id ? { ...u, progress: 100, status: 'done', hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' } : u
          ));
        } else {
          setUploads(current => current.map(u => 
            u.id === upload.id ? { ...u, progress, status: progress > 50 ? 'processing' : 'uploading' } : u
          ));
        }
      }, 500);
    });
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight">Data Ingestion Center</h1>
        <p className="text-slate-400">Secure upload and entity extraction via NLP & OCR.</p>
      </header>

      <div 
        className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center transition-colors relative overflow-hidden ${
          isDragging ? 'border-cyan-500 bg-cyan-950/20' : 'border-slate-700 bg-slate-900/50 hover:bg-slate-900 hover:border-slate-600'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input type="file" multiple className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" onChange={handleFileInput} accept=".pdf,.csv,.xlsx,.txt,.jpg,.jpeg,.png" />
        <div className="bg-slate-800 p-4 rounded-full mb-4 text-cyan-500">
          <UploadCloud size={40} />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">Drag files here or click to browse</h3>
        <p className="text-sm text-slate-400 mb-6">Supported formats: PDF, CSV, XLSX, TXT, Images (JPG, PNG)</p>
        
        <div className="flex gap-4 text-slate-500">
          <div className="flex flex-col items-center"><FileText size={24} /><span className="text-[10px] mt-1">PDF/TXT</span></div>
          <div className="flex flex-col items-center"><FileSpreadsheet size={24} /><span className="text-[10px] mt-1">CSV/XLSX</span></div>
          <div className="flex flex-col items-center"><ImageIcon size={24} /><span className="text-[10px] mt-1">Images</span></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 min-h-0">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col min-h-0">
          <h2 className="text-lg font-semibold text-white mb-4">Active Processing</h2>
          <div className="flex-1 overflow-y-auto space-y-3 pr-2">
            {uploads.length === 0 ? (
              <div className="text-slate-500 text-sm flex items-center justify-center h-32 italic">No active uploads.</div>
            ) : (
              uploads.map(upload => (
                <div key={upload.id} className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center gap-2 overflow-hidden">
                      <FileText className="text-cyan-500 shrink-0" size={18} />
                      <span className="text-sm font-medium text-slate-200 truncate">{upload.name}</span>
                      <span className="text-xs text-slate-500">{upload.size}</span>
                    </div>
                    {upload.status === 'done' ? <CheckCircle className="text-emerald-500" size={18} /> : <span className="text-xs text-cyan-400 uppercase tracking-wider animate-pulse">{upload.status}</span>}
                  </div>
                  
                  {upload.status !== 'done' && (
                    <div className="w-full bg-slate-800 rounded-full h-1.5 mb-1 mt-3">
                      <div className="bg-cyan-500 h-1.5 rounded-full transition-all duration-300" style={{ width: `${upload.progress}%` }}></div>
                    </div>
                  )}

                  {upload.status === 'done' && (
                    <div className="mt-3 bg-slate-900 rounded p-2 text-xs flex justify-between items-center border border-slate-800/50">
                      <div className="flex items-center gap-2 truncate pr-2 text-slate-400">
                        <CheckCircle size={12} className="text-emerald-500 shrink-0" />
                        <span className="truncate font-mono">SHA256: {upload.hash}</span>
                      </div>
                      <button className="text-slate-400 hover:text-white shrink-0"><Copy size={14} /></button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden">
          <div className="p-5 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-white">Upload History</h2>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input type="text" placeholder="Search files..." className="bg-slate-950 border border-slate-700 text-sm rounded-lg pl-9 pr-3 py-1.5 text-white focus:outline-none focus:border-cyan-500" />
            </div>
          </div>
          <div className="flex-1 overflow-auto">
            <table className="w-full text-sm text-left whitespace-nowrap">
              <thead className="text-xs text-slate-400 uppercase bg-slate-800/50 sticky top-0">
                <tr>
                  <th className="px-5 py-3">File Name</th>
                  <th className="px-5 py-3">Date</th>
                  <th className="px-5 py-3">Entities</th>
                  <th className="px-5 py-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {[
                  { name: 'CDR_Jio_Feb2023.csv', date: '2023-10-24 14:30', entities: 12450, status: 'PROCESSED' },
                  { name: 'FIR_Ranchi_049.pdf', date: '2023-10-24 09:15', entities: 42, status: 'PROCESSED' },
                  { name: 'Bank_Statement_HDFC.xlsx', date: '2023-10-23 16:45', entities: 312, status: 'PROCESSED' },
                  { name: 'Suspect_Photo_1.jpg', date: '2023-10-22 11:20', entities: 1, status: 'PROCESSED' },
                  { name: 'Corrupted_Log.txt', date: '2023-10-21 18:05', entities: 0, status: 'ERROR' },
                ].map((row, i) => (
                  <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-5 py-3 font-medium text-slate-300 flex items-center gap-2">
                      <FileText size={14} className="text-slate-500" />
                      {row.name}
                    </td>
                    <td className="px-5 py-3 text-slate-400">{row.date}</td>
                    <td className="px-5 py-3 text-cyan-400 font-mono">{row.entities}</td>
                    <td className="px-5 py-3 text-right">
                      {row.status === 'ERROR' ? (
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-bold tracking-wider bg-red-500/20 text-red-400 inline-flex items-center gap-1">
                          <AlertCircle size={10} /> {row.status}
                        </span>
                      ) : (
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-bold tracking-wider bg-emerald-500/20 text-emerald-400 inline-flex items-center gap-1">
                          <CheckCircle size={10} /> {row.status}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
