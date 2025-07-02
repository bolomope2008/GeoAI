# GeoAI Desktop - Technical Architecture

## System Overview

GeoAI Desktop is a hybrid desktop application that combines a React/Next.js frontend, Python FastAPI backend, and Electron wrapper to create a self-contained RAG (Retrieval-Augmented Generation) chatbot for geological research.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Electron Main Process                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Port Manager  │  │  Process Mgmt   │  │  User Data Mgmt │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│   Frontend      │  │   Backend       │  │   Storage Layer     │
│   (Next.js)     │  │   (FastAPI)     │  │                     │
│                 │  │                 │  │  ┌───────────────┐  │
│  ┌───────────┐  │  │  ┌───────────┐  │  │  │ Knowledge     │  │
│  │ Chat UI   │  │  │  │ RAG API   │  │  │  │ Base          │  │
│  └───────────┘  │  │  └───────────┘  │  │  └───────────────┘  │
│  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────────┐  │
│  │ File Mgmt │  │  │  │ ChromaDB  │  │  │  │ Vector DB     │  │
│  └───────────┘  │  │  └───────────┘  │  │  │ (ChromaDB)    │  │
│  ┌───────────┐  │  │  ┌───────────┐  │  │  └───────────────┘  │
│  │ Settings  │  │  │  │ Ollama    │  │  │  ┌───────────────┐  │
│  └───────────┘  │  │  │ Client    │  │  │  │ Config Files  │  │
└─────────────────┘  │  └───────────┘  │  │  └───────────────┘  │
                     └─────────────────┘  └─────────────────────┘
```

## Component Details

### 1. Electron Main Process (`electron/main.js`)

**Responsibilities:**
- Application lifecycle management
- Backend process spawning and monitoring
- Dynamic port allocation
- User data directory management
- IPC (Inter-Process Communication) handling

**Key Functions:**

```javascript
// Dynamic port allocation to prevent conflicts
async function findAvailablePort(startPort = 8000)

// User data path management  
function getUserDataPath() {
  // Returns: ~/Library/Application Support/geoai-desktop/
}

// Backend process management
async function startBackend()
function stopBackend()
```

**Process Flow:**
1. App starts → Find available port → Start backend → Create window
2. Backend crash → Auto-restart after 5 seconds
3. App quit → Gracefully stop backend → Exit

### 2. Frontend Layer (`frontend/my-app/`)

**Technology Stack:**
- **Framework**: Next.js 14 with App Router
- **UI**: React with TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **Build**: Static export (`next export`)

**Key Components:**

```typescript
// API Communication
lib/api.ts:
- getBaseUrl(): Gets dynamic backend URL from Electron
- All API calls use dynamic base URL

// Main Interface
app/page.tsx:
- ChatInterface: Main chat UI
- FileUpload: Document management
- Settings: Configuration panel
```

**Communication Flow:**
```
React Component → api.ts → Electron IPC → Backend API → Response
```

### 3. Backend Layer (`backend/`)

**Technology Stack:**
- **Framework**: FastAPI
- **Vector DB**: ChromaDB
- **LLM Integration**: Ollama client
- **Document Processing**: LangChain

**Core Services:**

```python
# Main application
start.py:
- FastAPI app initialization
- Dynamic port binding
- Settings management

# RAG Pipeline
rag_service.py:
- Document ingestion
- Vector similarity search
- LLM query processing

# Storage Management
settings_manager.py:
- JSON-based configuration
- Dynamic path resolution
```

**API Endpoints:**
- `GET /health` - Health check
- `POST /upload` - Document upload
- `POST /chat` - Chat processing
- `GET /documents` - List documents
- `DELETE /documents/{id}` - Delete document

### 4. Python Bundling System (`backend/create_bundle.py`)

**Purpose:** Create self-contained Python environment

**Process:**
1. Create virtual environment in `python_bundle/venv/`
2. Install all requirements.txt dependencies
3. Copy Python source files
4. Create launcher script
5. Package everything for distribution

**Output Structure:**
```
python_bundle/
├── venv/                    # Complete Python environment
│   ├── bin/python          # Python interpreter
│   └── lib/python3.x/      # All installed packages
├── *.py                    # Backend source files
├── run_backend.py          # Launcher script  
└── INFO.txt               # Bundle information
```

### 5. Storage Architecture

**Data Persistence:**
- **Location**: `~/Library/Application Support/geoai-desktop/`
- **Structure**:
  ```
  geoai-desktop/
  ├── knowledge_base/        # User documents
  │   ├── document1.pdf
  │   └── document2.txt
  ├── chroma_db/            # Vector database
  │   ├── chroma.sqlite3
  │   └── collections/
  └── settings.json         # App configuration
  ```

**Environment Variables:**
```bash
KNOWLEDGE_BASE_DIR=/path/to/knowledge_base
CHROMA_DB_DIR=/path/to/chroma_db  
CONFIG_DIR=/path/to/config
BACKEND_PORT=8001
```

## Inter-Process Communication

### Electron IPC Bridge (`electron/preload.js`)

```javascript
// Secure API exposure to frontend
window.electronAPI = {
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  checkOllama: () => ipcRenderer.invoke('check-ollama')
}
```

### Frontend Integration (`frontend/my-app/lib/api.ts`)

```typescript
// Dynamic URL resolution
export const getBaseUrl = async () => {
  if (window.electronAPI) {
    return await window.electronAPI.getBackendUrl();
  }
  return 'http://localhost:8000'; // fallback
}
```

## Build System

### Automated Build Pipeline (`build_complete_app.sh`)

```bash
# 1. Frontend Build
cd frontend/my-app && npm run build

# 2. Python Bundle Creation  
cd backend && python3 create_bundle.py

# 3. Electron Packaging
cd electron && npm run dist:mac
```

### Electron Builder Configuration

```json
{
  "files": [
    "main.js", "preload.js", "package.json",
    {"from": "../frontend/my-app/out", "to": "frontend/my-app/out"}
  ],
  "extraResources": [
    {"from": "../backend/python_bundle", "to": "backend"}
  ]
}
```

## Security Model

### Sandboxing
- **nodeIntegration**: `false`
- **contextIsolation**: `true`
- **webSecurity**: `true`

### Data Isolation
- App data stored in OS-specific user directories
- No access to system-wide Python installations
- Bundled dependencies prevent version conflicts

### IPC Security
- Preload script provides controlled API access
- No direct Node.js access from renderer process
- All backend communication through secure channels

## Performance Characteristics

### Memory Usage
- **Base**: ~100MB (Electron + frontend)
- **Backend**: ~100-200MB (Python + ChromaDB)
- **Variable**: Document processing can spike to 500MB+

### Startup Sequence
1. **Electron launch**: 1-2 seconds
2. **Backend startup**: 2-3 seconds (Python env + imports)
3. **Frontend load**: 1 second (static files)
4. **Total cold start**: 4-6 seconds

### Scaling Limits
- **Documents**: 1000s supported (limited by ChromaDB performance)
- **Chat history**: Stored in memory, cleared on restart
- **Concurrent users**: Single-user desktop application

## Error Handling & Recovery

### Backend Monitoring
```javascript
// Auto-restart on crash
backendProcess.on('exit', (code, signal) => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    setTimeout(() => startBackend(), 5000);
  }
});
```

### Frontend Resilience
- API failures fall back to cached data
- Graceful degradation when backend unavailable
- User-friendly error messages

### Data Recovery
- ChromaDB auto-recovery from corruption
- Settings fallback to defaults if corrupted
- Document re-indexing on vector DB issues

---

*This architecture supports the current self-contained desktop application model and can be extended for multi-user or cloud deployment scenarios.*