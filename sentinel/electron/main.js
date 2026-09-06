const { app, BrowserWindow, ipcMain, dialog, shell, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let backendProcess;

const isDev = process.env.ELECTRON_IS_DEV === '1' || !app.isPackaged;

function startBackend() {
  const backendDir = path.join(__dirname, '..', 'backend');
  const fs = require('fs');
  const venvPython = process.platform === 'win32'
    ? path.join(backendDir, '.venv', 'Scripts', 'python.exe')
    : path.join(backendDir, '.venv', 'bin', 'python');
  const pythonCmd = fs.existsSync(venvPython) ? venvPython : 'python';

  backendProcess = spawn(pythonCmd, ['-m', 'uvicorn', 'main:app', '--port', '8000'], {
    cwd: backendDir,
    shell: true
  });

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend stdout: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend stderr: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 1000,
    minWidth: 1200,
    minHeight: 800,
    backgroundColor: '#0f172a',
    title: 'SENTINEL — Criminal Network Analysis System',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  const template = [
    {
      label: 'File',
      submenu: [
        { label: 'Export', click: () => { /* Export logic */ } },
        { label: 'Print to PDF', click: async () => { await printToPDF(); } },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About SENTINEL',
          click: async () => {
            const { dialog } = require('electron');
            dialog.showMessageBox({
              title: 'About SENTINEL',
              message: 'SENTINEL — AI-Powered Criminal Network Analysis System\nVersion: ' + app.getVersion(),
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'frontend', 'dist', 'index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

async function printToPDF() {
  if (!mainWindow) return { success: false, error: 'No main window' };
  try {
    const { filePath } = await dialog.showSaveDialog({
      title: 'Save PDF',
      defaultPath: 'sentinel_export.pdf',
      filters: [{ name: 'PDF', extensions: ['pdf'] }]
    });

    if (filePath) {
      const data = await mainWindow.webContents.printToPDF({
        printBackground: true,
        pageSize: 'A4'
      });
      const fs = require('fs');
      fs.writeFileSync(filePath, data);
      return { success: true, filePath };
    }
    return { success: false, error: 'Cancelled' };
  } catch (error) {
    console.error('Failed to write PDF', error);
    return { success: false, error: error.message };
  }
}

app.whenReady().then(() => {
  if (!isDev) {
    startBackend();
  }
  
  ipcMain.handle('dialog:openFile', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile', 'multiSelections'],
      filters: [
        { name: 'Documents', extensions: ['pdf', 'txt', 'csv', 'xlsx'] },
        { name: 'Images', extensions: ['jpg', 'png', 'jpeg'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
    return result;
  });

  ipcMain.handle('dialog:saveFile', async (event, defaultName) => {
    const result = await dialog.showSaveDialog(mainWindow, {
      defaultPath: defaultName,
      filters: [{ name: 'PDF', extensions: ['pdf'] }]
    });
    return result;
  });

  ipcMain.handle('print:pdf', async () => {
    return await printToPDF();
  });

  ipcMain.handle('app:version', () => {
    return app.getVersion();
  });

  ipcMain.handle('shell:openExternal', async (event, url) => {
    await shell.openExternal(url);
  });

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});
