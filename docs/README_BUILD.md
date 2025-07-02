# GeoAI Desktop Build Instructions

## Overview

GeoAI Desktop is an Electron application with a Python backend. This guide explains how to build the application for macOS.

## Current Architecture

The application consists of:
1. **Frontend**: Next.js static export bundled with Electron
2. **Backend**: Python FastAPI server that runs as a subprocess
3. **Electron Shell**: Manages the application lifecycle and backend process

## Build Process

### Prerequisites

Users must have Python 3.9+ and the required dependencies installed:

```bash
# Install Python dependencies
pip install -r backend/requirements.txt
```

### Building the Application

1. **Build the Frontend**:
```bash
cd frontend/my-app
npm install
npm run build
```

2. **Build the Electron App**:
```bash
cd electron
npm install
npm run dist:mac
```

This creates DMG files in `electron/dist/`:
- `GeoAI Desktop-1.0.0-arm64.dmg` - For Apple Silicon Macs
- `GeoAI Desktop-1.0.0.dmg` - For Intel Macs

## How It Works

1. **Frontend Loading**: The frontend is bundled as static files within the Electron app
2. **Backend Management**: 
   - Electron spawns a Python subprocess running the FastAPI backend
   - Dynamic port allocation prevents conflicts
   - Backend uses user data directories for storage
3. **IPC Communication**: Frontend communicates with backend via HTTP, getting the URL through Electron IPC

## Current Limitations

The current build requires users to have Python and dependencies installed. This is a temporary solution while we work on fully self-contained packaging.

## Future Improvements

We're working on creating a fully self-contained application that includes:
- Bundled Python runtime
- All dependencies pre-installed
- No external requirements

## User Data Locations

The application stores user data in platform-specific directories:
- **macOS**: `~/Library/Application Support/geoai-desktop/`
  - `knowledge_base/` - Uploaded documents
  - `chroma_db/` - Vector database
  - `settings.json` - Configuration