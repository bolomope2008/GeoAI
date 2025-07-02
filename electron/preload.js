const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Get the backend URL from the main process
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
  
  // Get backend status
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  
  // Check if Ollama is running
  checkOllama: () => ipcRenderer.invoke('check-ollama'),
  
  // Platform information
  getPlatform: () => process.platform,
  
  // Version information
  getVersions: () => ({
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron
  })
});