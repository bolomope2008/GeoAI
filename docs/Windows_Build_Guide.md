# GeoAI Desktop - Windows Build Documentation

## Overview

This documentation provides complete instructions for building and distributing GeoAI Desktop as a self-contained Windows application using Electron. The resulting installer (.exe) includes all Python dependencies and requires no additional software installation except Ollama for AI features.

## Architecture

### Application Structure
```
GeoAI_V2/
├── backend/                 # FastAPI Python backend
├── frontend/my-app/         # Next.js frontend
├── electron/               # Electron wrapper
├── assets/                # Application icons (includes icon.ico)
├── docs/                  # Documentation
├── build_windows_app.bat  # Batch build script
└── build_windows_app.ps1  # PowerShell build script
```

### Technology Stack
- **Frontend**: Next.js (static export)
- **Backend**: FastAPI with ChromaDB
- **Desktop Wrapper**: Electron
- **Packaging**: electron-builder with NSIS installer
- **Python Bundling**: Virtual environment + requirements.txt

## Prerequisites

### System Requirements
- Windows 10/11 (for building)
- Node.js 18+ and npm
- Python 3.8+
- Git (recommended)

### Install Dependencies
```powershell
# Install Node.js dependencies
cd frontend/my-app
npm install

cd ../../electron
npm install

# Install Python dependencies
cd ../backend
pip install -r requirements.txt
```

## Build Process

### Automated Build (Recommended)

Choose one of two build scripts:

#### Option 1: Batch Script (Simple)
```batch
build_windows_app.bat
```

#### Option 2: PowerShell Script (Advanced)
```powershell
# Basic build
.\build_windows_app.ps1

# Advanced options
.\build_windows_app.ps1 -SkipFrontend  # Skip frontend build
.\build_windows_app.ps1 -SkipPython    # Skip Python bundle
.\build_windows_app.ps1 -Verbose       # Detailed logging
```

Both scripts will:
1. Build the Next.js frontend
2. Create a Python bundle with all dependencies
3. Configure Electron packaging
4. Generate Windows installer (.exe)

### Manual Build Steps

If you need to build manually:

#### 1. Build Frontend
```batch
cd frontend\my-app
npm install
npm run build
```

#### 2. Create Python Bundle
```batch
cd backend
python create_bundle.py
```

#### 3. Build Electron App
```batch
cd electron
npm install
npm run dist:win
```

## Key Configuration Files

### electron/package.json
Windows-specific Electron Builder configuration:

**Windows Target Configuration**:
```json
"win": {
  "icon": "../assets/icon.ico",
  "target": [
    {
      "target": "nsis",
      "arch": ["x64"]
    }
  ],
  "requestedExecutionLevel": "asInvoker",
  "artifactName": "${productName}-${version}-${arch}.${ext}"
}
```

**NSIS Installer Configuration**:
```json
"nsis": {
  "oneClick": false,
  "allowToChangeInstallationDirectory": true,
  "createDesktopShortcut": true,
  "createStartMenuShortcut": true,
  "shortcutName": "GeoAI Desktop",
  "displayLanguageSelector": false,
  "installerIcon": "../assets/icon.ico",
  "uninstallerIcon": "../assets/icon.ico",
  "installerHeaderIcon": "../assets/icon.ico",
  "deleteAppDataOnUninstall": false
}
```

### electron/main.js
Windows-specific path handling (already implemented):

**Python Environment Selection**:
```javascript
if (isDev) {
  // Development: use system Python
  backendCommand = 'python';
} else {
  // Production: use bundled Python environment
  const bundledPythonPath = process.platform === 'win32' 
    ? path.join(process.resourcesPath, 'backend', 'venv', 'Scripts', 'python.exe')
    : path.join(process.resourcesPath, 'backend', 'venv', 'bin', 'python');
}
```

### backend/create_bundle.py
Windows compatibility (already implemented):

```python
# Determine pip path based on platform
if sys.platform == "darwin" or sys.platform == "linux":
    pip_path = bundle_dir / "venv" / "bin" / "pip"
    python_path = bundle_dir / "venv" / "bin" / "python"
else:  # Windows
    pip_path = bundle_dir / "venv" / "Scripts" / "pip.exe"
    python_path = bundle_dir / "venv" / "Scripts" / "python.exe"
```

## Storage and Data Management

### User Data Locations
- **Windows**: `%APPDATA%\geoai-desktop\`
- **Structure**:
  - `knowledge_base\` - User uploaded documents
  - `chroma_db\` - Vector database storage
  - `config\` - Application settings

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
electron\dist\
├── GeoAI Desktop Setup 1.0.0.exe     # NSIS Installer (~280MB)
├── win-unpacked\                      # Unpacked application
│   ├── GeoAI Desktop.exe             # Main executable
│   ├── resources\                    # App resources
│   │   ├── app.asar                  # Frontend code
│   │   └── backend\                  # Python bundle
│   └── ...                          # Electron runtime
└── builder-debug.yml                 # Build metadata
```

### Installation Package Contents
The installer includes:
- Complete Windows application
- All Python dependencies bundled
- Frontend static files
- Application icons and metadata
- Desktop and Start Menu shortcuts
- Uninstaller

## Windows-Specific Features

### NSIS Installer
- **Custom Installation Path**: Users can choose install directory
- **Desktop Shortcut**: Optional desktop shortcut creation
- **Start Menu Integration**: Automatically adds to Start Menu
- **Uninstaller**: Clean removal with registry cleanup
- **Admin Rights**: Runs as normal user (asInvoker)

### File Associations
Currently not configured, but can be added:
```json
"fileAssociations": [
  {
    "ext": "pdf",
    "name": "PDF Document",
    "description": "Open with GeoAI Desktop"
  }
]
```

## Troubleshooting

### Common Build Issues

**Python Bundle Creation Fails**:
```batch
# Ensure Python dependencies are installed
pip install -r backend\requirements.txt

# Check Python version compatibility
python --version  # Should be 3.8+

# Check if virtual environment module is available
python -m venv --help
```

**Frontend Build Errors**:
```batch
# Clear Next.js cache
cd frontend\my-app
rmdir /s .next out
npm run build
```

**Electron Packaging Fails**:
```batch
# Clear Electron cache
cd electron
rmdir /s node_modules dist
npm install
npm run dist:win
```

**Icon Issues**:
```batch
# Verify icon file exists
dir assets\icon.ico

# Icon should be proper Windows .ico format
# Use online converters if needed: png2ico.com
```

### Runtime Issues

**Backend Won't Start**:
- Check Python bundle integrity in `electron\dist\win-unpacked\resources\backend\`
- Verify all .py files copied correctly
- Check Windows Event Viewer for detailed error logs
- Run from Command Prompt to see error messages

**Port Conflicts**:
- App automatically finds available ports starting from 8000
- Check Task Manager for conflicting processes
- Windows Firewall may prompt for network access

**Storage Issues**:
- Verify app has permission to write to `%APPDATA%\geoai-desktop\`
- Check Windows User Account Control (UAC) settings
- Ensure sufficient disk space (600MB+ required)

**Antivirus Interference**:
- Some antivirus software may flag the bundled Python executable
- Add exception for GeoAI Desktop installation directory
- Consider code signing for production releases

## Development vs Production

### Development Mode
- Uses system Python installation
- Loads frontend from `frontend\my-app\out\`
- Easier debugging with Windows terminal

### Production Mode  
- Uses bundled Python environment from `resources\backend\`
- Frontend loaded from app.asar bundle
- Self-contained, no external dependencies

Mode is determined by:
```javascript
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
```

## Security Considerations

### Code Signing (Recommended for Distribution)
```json
"win": {
  "certificateFile": "path/to/certificate.p12",
  "certificatePassword": "certificate_password",
  "signAndEditExecutable": true,
  "signingHashAlgorithms": ["sha256"],
  "rfc3161TimeStampServer": "http://timestamp.digicert.com"
}
```

### Windows Defender SmartScreen
- Unsigned executables may trigger SmartScreen warnings
- Code signing certificate resolves this issue
- Users can bypass warnings by clicking "More info" → "Run anyway"

### Sandboxing
Current build uses:
- `nodeIntegration: false`
- `contextIsolation: true` 
- `webSecurity: true`

## Distribution

### End User Installation
1. Download the installer: `GeoAI Desktop Setup 1.0.0.exe`
2. Run the installer (may show SmartScreen warning if unsigned)
3. Choose installation directory (default: `C:\Users\{username}\AppData\Local\Programs\geoai-desktop`)
4. Complete installation wizard
5. Launch from Desktop shortcut or Start Menu
6. Install Ollama separately for AI features

### File Sizes
- **Installer**: ~280MB
- **Installed Size**: ~650MB (includes Python environment)
- **Runtime Memory**: 200-400MB

## Performance Characteristics

### Startup Time
- Cold start: ~4-6 seconds (Windows may be slower than macOS)
- Backend initialization: ~3-4 seconds
- Frontend load: ~1-2 seconds

### Resource Usage
- RAM: ~250-450MB (slightly higher than macOS due to Windows overhead)
- Disk: ~650MB installed
- CPU: Minimal when idle, high during document processing

### Windows-Specific Optimizations
- Process priority can be adjusted in Task Manager
- Windows power settings affect performance
- SSD recommended for better ChromaDB performance

## Maintenance

### Updating Dependencies
1. Update `backend\requirements.txt`
2. Update `frontend\my-app\package.json`
3. Update `electron\package.json`
4. Rebuild with build script

### Version Management
Update version in:
- `electron\package.json` (main version)
- `frontend\my-app\package.json`
- Build script references

### Windows Updates Compatibility
- Test on Windows 10 and 11
- Verify compatibility with Windows Updates
- Consider Windows Store distribution for automatic updates

---

*This documentation reflects the Windows build system configuration. For cross-platform builds, see the main build documentation.*