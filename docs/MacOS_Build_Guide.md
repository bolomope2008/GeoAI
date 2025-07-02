# GeoAI Desktop - macOS Build Documentation

## Overview

This documentation provides complete instructions for building and distributing GeoAI Desktop as a self-contained macOS application using Electron. The resulting DMG includes all Python dependencies and requires no additional software installation except Ollama for AI features.

## Architecture

### Application Structure
```
GeoAI_V2/
├── backend/                 # FastAPI Python backend
├── frontend/my-app/         # Next.js frontend
├── electron/               # Electron wrapper
├── assets/                # Application icons
├── docs/                  # Documentation
└── build_complete_app.sh  # Main build script
```

### Technology Stack
- **Frontend**: Next.js (static export)
- **Backend**: FastAPI with ChromaDB
- **Desktop Wrapper**: Electron
- **Packaging**: electron-builder
- **Python Bundling**: Virtual environment + requirements.txt

## Prerequisites

### System Requirements
- macOS 10.15+ (for building)
- Node.js 18+ and npm
- Python 3.8+
- Xcode Command Line Tools

### Install Dependencies
```bash
# Install Node.js dependencies
cd frontend/my-app
npm install

cd ../../electron
npm install

# Install Python dependencies
cd ../backend
pip3 install -r requirements.txt
```

## Build Process

### Automated Build (Recommended)

The complete build process is automated via a single script:

```bash
chmod +x build_complete_app.sh
./build_complete_app.sh
```

This script:
1. Builds the Next.js frontend
2. Creates a Python bundle with all dependencies
3. Configures Electron packaging
4. Generates DMG files for both ARM64 and Intel architectures

### Manual Build Steps

If you need to build manually or understand the process:

#### 1. Build Frontend
```bash
cd frontend/my-app
npm install
npm run build
```

#### 2. Create Python Bundle
```bash
cd backend
python3 create_bundle.py
```

#### 3. Build Electron App
```bash
cd electron
npm install
npm run dist:mac
```

## Key Configuration Files

### electron/main.js
Main Electron process file with critical features:

**Dynamic Port Allocation** (lines 37-54):
```javascript
async function findAvailablePort(startPort = 8000) {
  // Finds available port to prevent conflicts
}
```

**User Data Management** (lines 17-35):
```javascript
function getUserDataPath() {
  const userDataPath = app.getPath('userData');
  // Creates: ~/Library/Application Support/geoai-desktop/
}
```

**Python Environment Selection** (lines 80-95):
```javascript
if (isDev) {
  // Development: use system Python
} else {
  // Production: use bundled Python environment
}
```

### electron/package.json
Electron Builder configuration:

**File Inclusion**:
```json
"files": [
  "main.js",
  "preload.js", 
  "package.json",
  {
    "from": "../frontend/my-app/out",
    "to": "frontend/my-app/out"
  }
]
```

**Python Bundle Packaging**:
```json
"extraResources": [
  {
    "from": "../backend/python_bundle",
    "to": "backend",
    "filter": ["**/*"]
  }
]
```

### backend/create_bundle.py
Creates self-contained Python environment:

1. Creates virtual environment in `backend/python_bundle/venv/`  
2. Installs all requirements.txt dependencies
3. Copies Python source files
4. Creates launcher script
5. Results in ~200MB bundle with all dependencies

### frontend/my-app/lib/api.ts
Handles API communication with Electron IPC:

```typescript
export const getBaseUrl = async () => {
  if (typeof window !== 'undefined') {
    if (window.electronAPI) {
      return await window.electronAPI.getBackendUrl();
    }
  }
  return 'http://localhost:8000'; // fallback
}
```

## Storage and Data Management

### User Data Locations
- **macOS**: `~/Library/Application Support/geoai-desktop/`
- **Structure**:
  - `knowledge_base/` - User uploaded documents
  - `chroma_db/` - Vector database storage
  - `config/` - Application settings

### Environment Variables
The backend receives these environment variables:
- `KNOWLEDGE_BASE_DIR` - Path to document storage
- `CHROMA_DB_DIR` - Path to vector database
- `CONFIG_DIR` - Path to configuration files
- `BACKEND_PORT` - Dynamic port number

## Build Output

### Generated Files
After successful build:
```
electron/dist/
├── GeoAI Desktop-1.0.0-arm64.dmg    # Apple Silicon (275MB)
├── GeoAI Desktop-1.0.0.dmg          # Intel x64 (281MB)
├── mac-arm64/                        # Unpacked ARM64 app
└── mac/                              # Unpacked Intel app
```

### Installation Package Contents
Each DMG contains:
- GeoAI Desktop.app (complete application)
- Drag-to-Applications installation interface
- All Python dependencies bundled
- Frontend static files
- Application icons and metadata

## Troubleshooting

### Common Build Issues

**Python Bundle Creation Fails**:
```bash
# Ensure Python dependencies are installed
pip3 install -r backend/requirements.txt

# Check Python version compatibility
python3 --version  # Should be 3.8+
```

**Frontend Build Errors**:
```bash
# Clear Next.js cache
cd frontend/my-app
rm -rf .next out
npm run build
```

**Electron Packaging Fails**:
```bash
# Clear Electron cache
cd electron
rm -rf node_modules dist
npm install
npm run dist:mac
```

### Runtime Issues

**Backend Won't Start**:
- Check Python bundle integrity in `backend/python_bundle/`
- Verify all .py files copied correctly
- Check Console.app for detailed error logs

**Port Conflicts**:
- App automatically finds available ports starting from 8000
- Check Activity Monitor for conflicting processes

**Storage Issues**:
- Verify app has permission to write to user data directory
- Check `~/Library/Application Support/geoai-desktop/` exists

## Development vs Production

### Development Mode
- Uses system Python installation
- Loads frontend from `frontend/my-app/out/`
- Easier debugging and testing

### Production Mode  
- Uses bundled Python environment
- Frontend loaded from app bundle
- Self-contained, no external dependencies

Mode is determined by:
```javascript
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
```

## Security Considerations

### Code Signing (Future)
For App Store distribution or to avoid Gatekeeper warnings:
```json
"mac": {
  "identity": "Developer ID Application: Your Name",
  "hardenedRuntime": true,
  "gatekeeperAssess": false
}
```

### Sandboxing
Current build uses:
- `nodeIntegration: false`
- `contextIsolation: true` 
- `webSecurity: true`

## Distribution

### End User Installation
1. Download appropriate DMG (ARM64 or Intel)
2. Mount DMG file
3. Drag GeoAI Desktop to Applications folder
4. Launch application
5. Install Ollama separately for AI features

### File Sizes
- **ARM64 DMG**: ~275MB
- **Intel DMG**: ~281MB
- **Installed Size**: ~600MB (includes Python environment)

## Maintenance

### Updating Dependencies
1. Update `backend/requirements.txt`
2. Update `frontend/my-app/package.json`
3. Update `electron/package.json`
4. Rebuild with `build_complete_app.sh`

### Version Management
Update version in:
- `electron/package.json` (main version)
- `frontend/my-app/package.json`
- Build script references

## Performance Characteristics

### Startup Time
- Cold start: ~3-5 seconds
- Backend initialization: ~2-3 seconds
- Frontend load: ~1-2 seconds

### Resource Usage
- RAM: ~200-400MB (depending on document processing)
- Disk: ~600MB installed
- CPU: Minimal when idle, high during document processing

---

*This documentation reflects the current build system as of the successful DMG creation. For updates or issues, refer to the project repository.*