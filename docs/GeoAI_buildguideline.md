# GeoAI Electron Build Guidelines

## Overview

This document provides comprehensive guidelines for building self-contained GeoAI desktop applications for macOS and Windows using Electron. The final executables will include everything except Ollama, which users must install separately.

## Architecture Overview

The GeoAI application consists of three main components:
1. **Backend**: FastAPI server (Python)
2. **Frontend**: Next.js application 
3. **Electron Wrapper**: Desktop application shell

The build process will bundle the Python backend with a portable Python interpreter and the built Next.js frontend into a single executable.

## Prerequisites

### Development Environment Setup

1. **Node.js and npm** (v18 or higher)
2. **Python 3.9+** for development
3. **Git** for version control
4. **Code signing certificates** (for production builds)
   - Apple Developer ID certificate for macOS
   - Windows code signing certificate

### Required Build Tools

#### macOS Development Machine
- Xcode Command Line Tools
- Python 3.9+ with pip
- Node.js 18+

#### Windows Development Machine
- Visual Studio Build Tools
- Python 3.9+ with pip
- Node.js 18+

## Project Structure

```
GeoAI_V2/
├── backend/
│   ├── api.py
│   ├── configuration.py
│   ├── update_database.py
│   ├── requirements.txt
│   └── knowledge_base/ (excluded from build)
├── frontend/
│   └── my-app/
│       ├── package.json
│       ├── next.config.js
│       └── app/
├── electron/
│   ├── main.js
│   ├── package.json
│   ├── preload.js
│   ├── assets/
│   │   ├── icon.svg (Source SVG icon)
│   │   ├── convert_icons.sh (Script to convert SVG to platform-specific icons)
│   │   ├── icon.ico (Generated Windows icon)
│   │   ├── icon.icns (Generated macOS icon)
│   │   └── icon.png (Generated Linux icon)
│   └── build/
│       └── entitlements.mac.plist
```

### Icon Assets and Conversion

The application uses a single SVG file (`icon.svg`) as the source for all platform-specific application icons. A conversion script (`convert_icons.sh`) is provided to generate the necessary `.ico`, `.icns`, and `.png` files from this SVG.

#### Conversion Process

1.  **Prerequisites**: Ensure you have `imagemagick` and `librsvg` (for `rsvg-convert`) installed on your system.
    *   **macOS (using Homebrew)**:
        ```bash
        brew install imagemagick librsvg
        ```
    *   **Linux (Debian/Ubuntu)**:
        ```bash
        sudo apt-get update
        sudo apt-get install imagemagick librsvg2-bin
        ```
    *   **Windows**: You might need to install these tools via WSL or find Windows-native binaries.

2.  **Run the Conversion Script**:
    Navigate to the `electron/assets/` directory and execute the script:
    ```bash
    cd electron/assets/
    ./convert_icons.sh
    ```
    This script will generate `icon.ico`, `icon.icns`, and `icon.png` in the same directory, which will then be used by Electron Builder for packaging.

    **Note**: The `convert_icons.sh` script should contain logic to:
    *   Convert `icon.svg` to various PNG sizes (e.g., 16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024).
    *   Combine these PNGs into a multi-resolution `.ico` file for Windows.
    *   Combine these PNGs into a multi-resolution `.icns` file for macOS.
    *   Select an appropriate PNG (e.g., 512x512) for the generic Linux icon.

    Example `convert_icons.sh` (conceptual):
    ```bash
    #!/bin/bash

    SOURCE_SVG="icon.svg"
    OUTPUT_DIR="."

    # Generate PNGs of various sizes
    rsvg-convert -w 16 -h 16 "$SOURCE_SVG" > "$OUTPUT_DIR/icon-16x16.png"
    rsvg-convert -w 32 -h 32 "$SOURCE_SVG" > "$OUTPUT_DIR/icon-32x32.png"
    rsvg-convert -w 64 -h 64 "$SOURCE_SVG" > "$OUTPUT_DIR/icon-64x64.png"
    rsvg-convert -w 128 -h 128 "$SOURCE_SVG" > "$OUTPUT_DIR/icon-128x128.png"
    rsvg-convert -w 256 -h 256 "$SOURCE_SVG" > "$OUTPUT_DIR/icon-256x256.png"
    rsvg-convert -w 512 -h 512 "$SOURCE_SVG" > "$OUTPUT_DIR/icon-512x512.png"
    rsvg-convert -w 1024 -h 1024 "$SOURCE_SVG" > "$OUTPUT_DIR/icon-1024x1024.png"

    # Create .ico for Windows
    convert "$OUTPUT_DIR/icon-16x16.png" "$OUTPUT_DIR/icon-32x32.png" "$OUTPUT_DIR/icon-64x64.png" "$OUTPUT_DIR/icon-128x128.png" "$OUTPUT_DIR/icon-256x256.png" "$OUTPUT_DIR/icon.ico"

    # Create .icns for macOS
    iconutil -c icns -o "$OUTPUT_DIR/icon.icns" "$OUTPUT_DIR/icon-1024x1024.png" # Requires macOS and iconutil

    # Use a high-res PNG for Linux
    cp "$OUTPUT_DIR/icon-512x512.png" "$OUTPUT_DIR/icon.png"

    # Clean up intermediate PNGs
    rm "$OUTPUT_DIR"/icon-*.png
    ```

    Ensure the `electron-builder` configuration in `electron/package.json` points to these generated icon files.


## Build Process Steps

### 1. Backend Preparation

#### 1.1 Create Portable Python Environment

**For Windows:**
```bash
# Download Python embeddable package from python.org
# Example: python-3.9.13-embed-amd64.zip
# Extract to electron/python-builds/win-x64/

# Install pip in the embedded Python
cd electron/python-builds/win-x64
./python.exe -m ensurepip
./python.exe -m pip install --upgrade pip

# Install all backend dependencies
./python.exe -m pip install -r ../../../backend/requirements.txt --target .
```

**For macOS:**
```bash
# Use pyinstaller or py2app alternative approach
# Or build Python from source with --enable-framework
cd electron/python-builds/mac-x64
python3 -m venv python-mac
source python-mac/bin/activate
pip install -r ../../../backend/requirements.txt
deactivate
```

#### 1.2 Backend Configuration Updates

Create a modified `configuration.py` that uses environment variables for paths:
```python
import os

# Use environment variables set by Electron
KNOWLEDGE_BASE_DIR = os.environ.get('KNOWLEDGE_BASE_DIR', './knowledge_base')
CHROMA_DB_DIR = os.environ.get('CHROMA_DB_DIR', './chroma_db')
```

### 2. Frontend Build Process

#### 2.1 Update Frontend API Configuration

Modify `frontend/my-app/lib/api.ts` to handle Electron environment:
```typescript
const getBaseUrl = () => {
  if (typeof window !== 'undefined' && window.electronAPI) {
    return window.electronAPI.getBackendUrl();
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};
```

#### 2.2 Build Frontend for Production

```bash
cd frontend/my-app

# Install dependencies
npm install

# Build for production with static export
npm run build

# Export static files
npx next export -o out
```

The `out` directory will contain the static HTML/CSS/JS files.

### 3. Electron Setup

#### 3.1 Initialize Electron Project

```bash
mkdir electron
cd electron
npm init -y
npm install --save-dev electron electron-builder
npm install @electron/remote
```

#### 3.2 Critical Electron Configuration Files

**main.js** - Key considerations:
- Handle Python process spawning for both development and production
- Manage proper paths for bundled resources
- Implement graceful shutdown for backend process
- Check for Ollama installation on startup

**preload.js** - Security bridge:
```javascript
const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getBackendUrl: () => 'http://localhost:8000'
});
```

**package.json** - Electron Builder configuration (see artifact for detailed example)

### 4. Platform-Specific Considerations

#### 4.1 macOS Build

**Code Signing Requirements:**
- Create `entitlements.mac.plist` for hardened runtime
- Required entitlements:
  - `com.apple.security.cs.allow-unsigned-executable-memory`
  - `com.apple.security.cs.allow-jit`
  - `com.apple.security.network.client`
  - `com.apple.security.network.server`

**Notarization Process:**
1. Build the app with code signing
2. Create a DMG
3. Submit to Apple for notarization
4. Staple the notarization ticket

#### 4.2 Windows Build

**Considerations:**
- Windows Defender may flag Python executables
- Include Windows runtime redistributables
- Sign the executable to avoid SmartScreen warnings

### 5. Build Commands

#### Development Build Testing
```bash
# Test Electron app in development
cd electron
npm run dev
```

#### Production Builds

```bash
# Build for current platform
npm run dist

# Build for macOS (requires macOS)
npm run dist-mac

# Build for Windows (can be done on any platform with Wine)
npm run dist-win

# Build for all platforms
npm run dist-all
```

### 6. User Data Management

The application should store user data in platform-specific locations:

- **macOS**: `~/Library/Application Support/GeoAI/`
- **Windows**: `%APPDATA%/GeoAI/`
- **Linux**: `~/.config/GeoAI/`

Store in these directories:
- `knowledge_base/` - User's uploaded documents
- `chroma_db/` - Vector database files
- `config.json` - User preferences

### 7. Ollama Integration

#### Non-Blocking Startup Check
1. Check if Ollama is running at `http://localhost:11434` in the background
2. If not found, show a non-intrusive notification or status indicator
3. Allow the app to start normally - users can configure Ollama settings later
4. Display connection status in the UI (e.g., "Ollama: Connected" or "Ollama: Not Connected")

#### Graceful Degradation
- App should start and function normally without Ollama
- Show informative messages when users try to chat without Ollama connected
- Provide easy access to settings where users can:
  - Change Ollama URL
  - Select different models
  - Test connection
- Include "Install Ollama" helper link in settings or help menu

#### Model Management
- Don't block on missing models
- Let users configure model names in settings
- Show clear error messages if selected models aren't available
- Allow users to proceed with different models

### 8. Testing Checklist

Before distribution, test:

- [ ] Fresh installation on clean system
- [ ] File upload functionality
- [ ] Database refresh operation
- [ ] Settings persistence across restarts
- [ ] Proper cleanup on uninstall
- [ ] Memory usage over extended periods
- [ ] Ollama connection handling
- [ ] Error states and recovery

### 9. Distribution

#### macOS
- Distribute as DMG with drag-to-Applications installer

#### Windows
- NSIS installer for traditional installation

### 10. Important Considerations

#### User Experience First
- App should always start successfully, regardless of Ollama status
- All file management features should work without Ollama
- Configuration interface should be easily accessible
- Show clear, actionable messages when Ollama connection fails
- Never show blocking error dialogs on startup

#### Performance
- Backend startup time (Python initialization)
- Consider using `--no-site-packages` for faster Python startup
- Implement loading screens during initialization
- Don't wait for Ollama connection during startup

#### Security
- Never expose backend directly to network
- Use IPC for Electron-backend communication in future versions
- Sanitize all file paths and user inputs

#### Updates
- Implement auto-updater using electron-updater
- Separate app updates from model updates
- Allow users to maintain their knowledge base across updates

#### Error Handling
- Comprehensive logging to user data directory
- User-friendly error messages that suggest solutions
- Diagnostic information collection for support
- Graceful fallbacks for all external dependencies

## Troubleshooting Guide

### Common Issues

1. **Python Module Import Errors**
   - Ensure all dependencies are installed in portable Python
   - Check PYTHONPATH environment variable
   - Verify no hardcoded paths in Python code

2. **Frontend Not Loading**
   - Verify Next.js static export completed successfully
   - Check file paths in production build
   - Ensure correct content security policy

3. **Ollama Connection Issues**
   - Verify Ollama service is running
   - Check firewall settings
   - Ensure correct base URL configuration

4. **File Permission Errors**
   - Ensure app has write permissions to user data directory
   - Handle Windows UAC properly
   - Request appropriate permissions on macOS

## Build Automation

Consider setting up CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Build Electron App
on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        os: [macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - uses: actions/setup-python@v2
      - run: npm install
      - run: npm run dist
      - uses: actions/upload-artifact@v2
```

## Final Notes

- Always test on clean VMs before release
- Maintain separate development and production configurations
- Document minimum system requirements clearly
- Provide comprehensive installation guides for end users
- Consider creating video tutorials for setup process
- Ensure the app has a smooth first-run experience even without Ollama

Remember: The goal is a seamless experience where users can:
1. Download and run your GeoAI application immediately
2. Use all file management features right away
3. Configure Ollama connection when they're ready
4. Start chatting with their documents once Ollama is set up

The application should never feel broken or incomplete, even without Ollama installed.