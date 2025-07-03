// Type definitions for Electron API exposed via preload script

export interface ElectronAPI {
  getBackendUrl: () => Promise<string>;
  getBackendStatus: () => Promise<{ ready: boolean; port: number }>;
  checkOllama: () => Promise<boolean>;
  getPlatform: () => string;
  getVersions: () => {
    node: string;
    chrome: string;
    electron: string;
  };
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

export {};