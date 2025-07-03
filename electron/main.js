const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const net = require('net');

// Keep a global reference of the window object
let mainWindow;
let backendProcess;
let backendPort = 8000;
let backendReady = false;

// Determine if we're in development or production
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

// Get platform-specific user data paths
function getUserDataPath() {
  const userDataPath = app.getPath('userData');
  
  // Create necessary directories
  const dirs = {
    knowledge_base: path.join(userDataPath, 'knowledge_base'),
    chroma_db: path.join(userDataPath, 'chroma_db'),
    config: userDataPath
  };
  
  // Ensure directories exist
  Object.values(dirs).forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
  
  return dirs;
}

// Find an available port
async function findAvailablePort(startPort = 8000) {
  return new Promise((resolve) => {
    const server = net.createServer();
    
    server.listen(startPort, '127.0.0.1', () => {
      const port = server.address().port;
      server.close(() => {
        resolve(port);
      });
    });
    
    server.on('error', () => {
      // Port is in use, try the next one
      resolve(findAvailablePort(startPort + 1));
    });
  });
}

// Start the Python backend
async function startBackend() {
  try {
    // Get available port
    backendPort = await findAvailablePort(8000);
    console.log(`Starting backend on port ${backendPort}`);
    
    // Get user data paths
    const userPaths = getUserDataPath();
    
    // Set environment variables for the backend
    const env = {
      ...process.env,
      KNOWLEDGE_BASE_DIR: userPaths.knowledge_base,
      CHROMA_DB_DIR: userPaths.chroma_db,
      CONFIG_DIR: userPaths.config,
      BACKEND_PORT: backendPort.toString(),
      PYTHONUNBUFFERED: '1',
      PYTHONNOUSERSITE: '1'
    };
    
    let backendCommand;
    let backendArgs = [];
    let backendCwd;
    
    if (isDev) {
      // Development mode - use system Python
      backendCommand = 'python3';
      backendArgs = [path.join(__dirname, '..', 'backend', 'start.py')];
      backendCwd = path.join(__dirname, '..', 'backend');
    } else {
      // Production mode - use bundled Python environment
      const platform = process.platform;
      const bundledPythonPath = platform === 'win32' 
        ? path.join(process.resourcesPath, 'backend', 'venv', 'Scripts', 'python.exe')
        : path.join(process.resourcesPath, 'backend', 'venv', 'bin', 'python');
        
      backendCommand = bundledPythonPath;
      backendArgs = [path.join(process.resourcesPath, 'backend', 'start.py')];
      backendCwd = path.join(process.resourcesPath, 'backend');
    }
    
    // Spawn the backend process
    backendProcess = spawn(backendCommand, backendArgs, {
      cwd: backendCwd,
      env: env,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    // Handle backend output
    backendProcess.stdout.on('data', (data) => {
      console.log(`Backend: ${data.toString()}`);
      if (data.toString().includes('Uvicorn running') || data.toString().includes('Started server')) {
        backendReady = true;
        console.log('Backend is ready');
      }
    });
    
    backendProcess.stderr.on('data', (data) => {
      console.error(`Backend Error: ${data.toString()}`);
    });
    
    backendProcess.on('error', (error) => {
      console.error('Failed to start backend:', error);
      dialog.showErrorBox('Backend Error', `Failed to start backend: ${error.message}`);
    });
    
    backendProcess.on('exit', (code, signal) => {
      console.log(`Backend exited with code ${code} and signal ${signal}`);
      backendReady = false;
      
      // Restart backend if it crashed and app is still running
      if (mainWindow && !mainWindow.isDestroyed()) {
        console.log('Backend crashed, restarting in 5 seconds...');
        setTimeout(() => startBackend(), 5000);
      }
    });
    
    // Wait for backend to be ready
    await waitForBackend();
    
  } catch (error) {
    console.error('Error starting backend:', error);
    dialog.showErrorBox('Backend Error', `Failed to start backend: ${error.message}`);
  }
}

// Wait for backend to be ready
async function waitForBackend(maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const response = await fetch(`http://127.0.0.1:${backendPort}/health`);
      if (response.ok) {
        console.log('Backend is responding');
        backendReady = true;
        return true;
      }
    } catch (error) {
      // Backend not ready yet
    }
    
    // Wait 1 second before next attempt
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error('Backend failed to start after 30 seconds');
}

// Stop the backend process
function stopBackend() {
  if (backendProcess) {
    console.log('Stopping backend...');
    backendProcess.kill('SIGTERM');
    backendProcess = null;
    backendReady = false;
  }
}

// Create the main application window
function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true
    },
    icon: path.join(__dirname, '..', 'assets', 'icon.png'),
    titleBarStyle: 'hiddenInset',
    show: false
  });
  
  // Load the frontend
  if (isDev) {
    // Development - load built static files (since we're not running Next.js dev server)
    mainWindow.loadFile(path.join(__dirname, '..', 'frontend', 'my-app', 'out', 'index.html'));
  } else {
    // Production - frontend files are bundled in the app package
    // In packaged app, files are at app.asar/frontend/my-app/out/
    const frontendPath = path.join(__dirname, 'frontend', 'my-app', 'out', 'index.html');
    console.log('Loading frontend from:', frontendPath);
    mainWindow.loadFile(frontendPath);
  }
  
  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
  
  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// IPC handlers
ipcMain.handle('get-backend-url', () => {
  return `http://127.0.0.1:${backendPort}`;
});

ipcMain.handle('get-backend-status', () => {
  return { ready: backendReady, port: backendPort };
});

ipcMain.handle('check-ollama', async () => {
  try {
    const response = await fetch('http://localhost:11434/api/tags');
    return response.ok;
  } catch (error) {
    return false;
  }
});

// App event handlers
app.whenReady().then(async () => {
  // Start backend first
  await startBackend();
  
  // Then create window
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
  stopBackend();
});

// Handle certificate errors (for development)
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  if (isDev) {
    // Ignore certificate errors in development
    event.preventDefault();
    callback(true);
  } else {
    // Use default behavior in production
    callback(false);
  }
});