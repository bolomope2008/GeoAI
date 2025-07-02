# GeoAI Desktop - Quick Start Guide

## For Developers: Building the App

### One-Command Build
```bash
chmod +x build_complete_app.sh
./build_complete_app.sh
```

### Prerequisites
- macOS 10.15+
- Node.js 18+
- Python 3.8+
- Xcode Command Line Tools

### What Gets Built
- **ARM64 DMG**: For Apple Silicon Macs (M1, M2, M3)
- **Intel DMG**: For Intel-based Macs
- **Size**: ~275-281MB each
- **Self-contained**: No additional software needed (except Ollama)

## For End Users: Installing the App

### Installation Steps
1. Download the appropriate DMG file:
   - `GeoAI Desktop-1.0.0-arm64.dmg` for Apple Silicon
   - `GeoAI Desktop-1.0.0.dmg` for Intel Macs
2. Double-click the DMG to mount it
3. Drag "GeoAI Desktop" to the Applications folder
4. Launch from Applications or Spotlight

### First Run
1. **Install Ollama** (required for AI features):
   ```bash
   brew install ollama
   # OR download from https://ollama.ai
   ```

2. **Start Ollama** and pull a model:
   ```bash
   ollama serve
   ollama pull llama2  # or your preferred model
   ```

3. **Launch GeoAI Desktop** from Applications

### Storage Location
Your documents and data are stored in:
```
~/Library/Application Support/geoai-desktop/
├── knowledge_base/    # Your uploaded documents
├── chroma_db/        # Vector database
└── config/           # App settings
```

## Architecture Overview

### How It Works
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js       │    │    Electron      │    │   FastAPI       │
│   Frontend      │◄──►│    Wrapper       │◄──►│   Backend       │
│   (React)       │    │  (main.js)       │    │   (Python)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Bundled Python │
                       │   Environment    │
                       │   (venv + deps)  │
                       └──────────────────┘
```

### Key Features
- **Self-contained**: All Python dependencies bundled
- **Dynamic ports**: Automatically finds available ports
- **Secure**: Isolated user data storage
- **Cross-platform**: Works on both Intel and Apple Silicon

## Troubleshooting

### App Won't Start
1. Check Console.app for error messages
2. Ensure you have sufficient disk space (600MB)
3. Try restarting your Mac

### Backend Connection Issues
1. Check if port 8000-8010 range is available
2. Quit and restart the application
3. Check Activity Monitor for conflicting processes

### AI Features Not Working
1. Ensure Ollama is installed and running
2. Check that you've pulled at least one model
3. Verify Ollama is accessible at `http://localhost:11434`

### Document Upload Issues
1. Check permissions for the app to access files
2. Ensure document format is supported (PDF, TXT, etc.)
3. Check available disk space

## File Structure Reference

### Source Code
```
GeoAI_V2/
├── backend/                 # Python FastAPI backend
│   ├── start.py            # Main backend entry point
│   ├── requirements.txt    # Python dependencies
│   └── create_bundle.py    # Bundle creation script
├── frontend/my-app/        # Next.js frontend
│   ├── lib/api.ts         # API communication
│   └── out/               # Built static files
├── electron/              # Electron wrapper
│   ├── main.js           # Main Electron process
│   ├── preload.js        # Secure API bridge
│   └── package.json      # Electron configuration
└── build_complete_app.sh  # Build automation script
```

### Built Application
```
GeoAI Desktop.app/
├── Contents/
│   ├── MacOS/
│   │   └── GeoAI Desktop           # Electron executable
│   ├── Resources/
│   │   ├── app.asar                # Frontend + Electron code
│   │   └── backend/                # Python bundle
│   │       ├── venv/               # Python virtual environment
│   │       └── *.py                # Backend Python files
│   └── Info.plist                  # App metadata
```

## Performance Notes

### Startup Time
- **First launch**: 5-8 seconds (Python environment initialization)
- **Subsequent launches**: 3-5 seconds
- **Backend ready**: 2-3 seconds after window appears

### Resource Usage
- **Memory**: 200-400MB (varies with document processing)
- **Disk**: 600MB installed size
- **CPU**: Low when idle, high during document processing

### Optimization Tips
- Close unused chat sessions to free memory
- Regularly clear old documents from knowledge base
- Keep Ollama models updated for better performance

---

*Need help? Check the full documentation in `docs/MacOS_Build_Guide.md`*