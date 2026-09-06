const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openFileDialog: () => ipcRenderer.invoke('dialog:openFile'),
  saveFileDialog: (defaultName) => ipcRenderer.invoke('dialog:saveFile', defaultName),
  printToPDF: () => ipcRenderer.invoke('print:pdf'),
  getAppVersion: () => ipcRenderer.invoke('app:version'),
  openExternal: (url) => ipcRenderer.invoke('shell:openExternal', url),
  onBackendReady: (callback) => ipcRenderer.on('backend:ready', (_event, value) => callback(value)),
  platform: process.platform
});

/**
 * TypeScript definitions
 * 
 * declare global {
 *   interface Window {
 *     electronAPI: {
 *       openFileDialog: () => Promise<Electron.OpenDialogReturnValue>;
 *       saveFileDialog: (defaultName: string) => Promise<Electron.SaveDialogReturnValue>;
 *       printToPDF: () => Promise<{ success: boolean; filePath?: string; error?: string }>;
 *       getAppVersion: () => Promise<string>;
 *       openExternal: (url: string) => Promise<void>;
 *       onBackendReady: (callback: (value: any) => void) => void;
 *       platform: string;
 *     }
 *   }
 * }
 */
