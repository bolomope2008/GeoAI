# GeoAI Desktop Build System

This directory contains all the build scripts and configuration files needed to create distributable versions of GeoAI Desktop for different platforms.

## 📁 Directory Structure

```
build/
├── README.md                    # This file
├── build_config.json           # Build configuration and metadata
├── build_app.py                # Cross-platform build script (recommended)
├── build_complete_app.sh        # macOS build script
├── build_windows_app.bat        # Windows build script (simple)
├── build_windows_app.ps1        # Windows build script (advanced)
└── (future: build_linux_app.sh) # Linux build script
```

## 🚀 Quick Start

### One-Command Build (Recommended)
```bash
# From project root
python3 build/build_app.py

# OR from build directory
cd build
python3 build_app.py
```

This script automatically:
- Detects your operating system
- Checks prerequisites
- Runs the appropriate platform-specific build
- Reports build status and output locations

### Platform-Specific Builds

#### macOS
```bash
# From project root
build/build_complete_app.sh

# OR from build directory
cd build
./build_complete_app.sh
```

#### Windows
```batch
# Simple batch script
build\build_windows_app.bat

# Advanced PowerShell script
build\build_windows_app.ps1

# With options (PowerShell only)
build\build_windows_app.ps1 -SkipFrontend -Verbose
```

## 📋 Prerequisites

### All Platforms
- **Node.js 18+** - [Download](https://nodejs.org)
- **Python 3.8+** - [Download](https://python.org)

### macOS Specific
- **Xcode Command Line Tools** - `xcode-select --install`

### Windows Specific
- **PowerShell 5.0+** (for advanced script)

## 🔧 Build Process

Each build follows these steps:

1. **Frontend Build** (~30 seconds)
   - Installs npm dependencies
   - Builds Next.js to static files
   - Output: `frontend/my-app/out/`

2. **Python Bundle Creation** (~3 minutes)
   - Creates virtual environment
   - Installs all Python dependencies
   - Bundles into self-contained package
   - Output: `backend/python_bundle/`

3. **Electron Packaging** (~1 minute)
   - Installs Electron dependencies
   - Packages application with electron-builder
   - Creates platform-specific installers
   - Output: `electron/dist/`

## 📦 Build Outputs

### macOS
- `electron/dist/GeoAI Desktop-1.0.0-arm64.dmg` (275MB) - Apple Silicon
- `electron/dist/GeoAI Desktop-1.0.0.dmg` (281MB) - Intel

### Windows
- `electron/dist/GeoAI Desktop Setup 1.0.0.exe` (280MB) - NSIS installer

### Development Builds
- `electron/dist/mac/` - Unpacked macOS app
- `electron/dist/win-unpacked/` - Unpacked Windows app

## ⚙️ Configuration

### Build Configuration (`build_config.json`)
Contains:
- Platform-specific settings
- Build step definitions
- Dependency requirements
- Output specifications
- Troubleshooting guide

### Environment Variables
The build process uses these environment variables:
- `NODE_ENV=production`
- `ELECTRON_BUILDER_CACHE=electron/dist/.cache`
- `PYTHONUNBUFFERED=1`

## 🐛 Troubleshooting

### Common Issues

**"Command not found" errors:**
```bash
# Check if tools are installed
node --version
python --version
npm --version
```

**Build fails with permission errors:**
```bash
# Make scripts executable (macOS/Linux)
chmod +x build/*.sh

# Run as administrator if needed (Windows)
```

**Electron build cache issues:**
```bash
# Clear electron builder cache
rm -rf electron/dist/.cache
# OR on Windows
rmdir /s electron\dist\.cache
```

**Python bundle creation fails:**
```bash
# Check internet connection
# Verify Python packages can be installed
pip install -r backend/requirements.txt
```

### Platform-Specific Issues

#### macOS
- **Code signing**: Apps may show security warnings without signing
- **Gatekeeper**: Users need to allow app in Security preferences
- **Disk space**: Ensure 2GB+ free space for build process

#### Windows
- **SmartScreen**: Unsigned apps trigger warnings
- **Antivirus**: May scan/block Python bundle during creation
- **Execution Policy**: PowerShell scripts may need policy bypass

## 🔄 Development Workflow

### Iterative Development
```bash
# Skip time-consuming steps during development
build/build_windows_app.ps1 -SkipPython  # Skip Python bundle
build/build_windows_app.ps1 -SkipFrontend  # Skip frontend build
```

### Testing Builds
1. Run build script
2. Check `electron/dist/` for output files
3. Test installer on clean system
4. Verify app functionality

### Release Process
1. Update version in `package.json` files
2. Update `build_config.json` version
3. Run full clean build
4. Test on target platforms
5. Distribute installers

## 📊 Build Metrics

| Platform | Build Time | Installer Size | Installed Size |
|----------|------------|----------------|----------------|
| macOS ARM64 | ~4 min | 275 MB | ~600 MB |
| macOS Intel | ~4 min | 281 MB | ~600 MB |
| Windows x64 | ~4 min | 280 MB | ~650 MB |

## 🛠️ Customization

### Adding New Platforms
1. Create platform-specific build script
2. Update `build_config.json` with platform details
3. Add platform detection to `build_app.py`
4. Update documentation

### Modifying Build Steps
1. Edit platform-specific scripts
2. Update `build_config.json` step definitions
3. Test on target platforms

### Changing Output Locations
1. Modify electron-builder configuration in `electron/package.json`
2. Update output paths in build scripts
3. Update `build_config.json` output specifications

## 📚 Related Documentation

- [macOS Build Guide](../docs/MacOS_Build_Guide.md) - Detailed macOS instructions
- [Windows Build Guide](../docs/Windows_Build_Guide.md) - Detailed Windows instructions
- [Windows Deployment Guide](../docs/Windows_Deployment_Guide.md) - Windows deployment strategies
- [Technical Architecture](../docs/Technical_Architecture.md) - System architecture overview

---

*All build scripts are designed to be run from any location and will automatically navigate to the correct project structure.*