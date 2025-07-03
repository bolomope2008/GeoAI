export interface Source {
  source: string;
  path: string;
  page?: number;
  content?: string;
}

export interface ChatResponse {
  answer: string;
  sources?: Source[];
}

export interface FileInfo {
  name: string;
  size: number;
  type: string;
}

export interface Config {
  ollama_base_url: string;
  embedding_model: string;
  llm_model: string;
  chunk_size: number;
  chunk_overlap: number;
  top_k_chunks: number;
}

export interface StreamResponse {
  type: 'sources' | 'token' | 'done' | 'error';
  content?: string;
  sources?: string;
  error?: string;
}

export const getBaseUrl = async () => {
  if (typeof window !== 'undefined') {
    // Check if we're in Electron environment
    if (window.electronAPI) {
      // Get backend URL from Electron main process
      try {
        return await window.electronAPI.getBackendUrl();
      } catch (error) {
        console.warn('Failed to get backend URL from Electron:', error);
        return 'http://localhost:8000';
      }
    }
    // Browser environment - use hostname with default port
    return `http://${window.location.hostname}:8000`;
  }
  // Server environment
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

class ApiService {
  private baseUrl: string | null = null;

  constructor() {
    // Don't initialize baseUrl in constructor since getBaseUrl is now async
  }
  
  private async getBaseUrlCached(): Promise<string> {
    if (!this.baseUrl) {
      this.baseUrl = await getBaseUrl();
    }
    return this.baseUrl;
  }
  
  // Reset cached URL if needed (e.g., when backend restarts with new port)
  public resetBaseUrl(): void {
    this.baseUrl = null;
  }

  async chat(message: string): Promise<ChatResponse> {
    const baseUrl = await this.getBaseUrlCached();
    const response = await fetch(`${baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get response');
    }

    return response.json();
  }

  async uploadFile(file: File): Promise<{ message: string; details?: unknown }> {
    const baseUrl = await this.getBaseUrlCached();
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${baseUrl}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload file');
    }

    return response.json();
  }

  async searchFiles(query: string = ''): Promise<FileInfo[]> {
    const baseUrl = await this.getBaseUrlCached();
    const response = await fetch(`${baseUrl}/files/search?query=${encodeURIComponent(query)}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to search files');
    }

    const data = await response.json();
    return data.files;
  }

  async refreshDatabase(): Promise<void> {
    const baseUrl = await this.getBaseUrlCached();
    const response = await fetch(`${baseUrl}/refresh`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to refresh database');
    }
  }

  async clearMemory(): Promise<void> {
    const baseUrl = await this.getBaseUrlCached();
    const response = await fetch(`${baseUrl}/clear-memory`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to clear conversation memory');
    }
  }

  async clearDatabase(): Promise<void> {
    const baseUrl = await this.getBaseUrlCached();
    const response = await fetch(`${baseUrl}/clear-database`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to clear database');
    }
  }

  async getConfig(): Promise<Config> {
    const baseUrl = await this.getBaseUrlCached();
    const response = await fetch(`${baseUrl}/settings`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get configuration');
    }

    return response.json();
  }

  async updateConfig(config: Config): Promise<void> {
    const baseUrl = await this.getBaseUrlCached();
    const response = await fetch(`${baseUrl}/settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update configuration');
    }
  }
}

export const api = new ApiService(); 