# GeoAI Desktop - Windows Deployment Guide

## Quick Start

### For Developers
```batch
# Simple one-command build
build_windows_app.bat

# OR PowerShell with options
.\build_windows_app.ps1 -Verbose
```

### For End Users
1. Download `GeoAI Desktop Setup 1.0.0.exe`
2. Run installer and follow wizard
3. Install [Ollama](https://ollama.ai/download/windows) for AI features
4. Launch from Desktop or Start Menu

## Build Scripts Comparison

### Batch Script (`build_windows_app.bat`)
- **Best for**: Simple, automated builds
- **Advantages**: Works on all Windows systems, no execution policy issues
- **Usage**: Double-click or run from Command Prompt

### PowerShell Script (`build_windows_app.ps1`)
- **Best for**: Advanced users, CI/CD pipelines
- **Advantages**: Better error handling, flexible options, colored output
- **Usage**: 
  ```powershell
  # Basic build
  .\build_windows_app.ps1
  
  # Skip steps for faster iteration
  .\build_windows_app.ps1 -SkipFrontend -SkipPython
  
  # Verbose logging
  .\build_windows_app.ps1 -Verbose
  ```

## Prerequisites Checklist

### Development Environment
- [ ] Windows 10 or 11
- [ ] Node.js 18+ ([download](https://nodejs.org))
- [ ] Python 3.8+ ([download](https://python.org))
- [ ] Git (optional but recommended)
- [ ] Code editor (VS Code recommended)

### Verification Commands
```batch
# Check Node.js
node --version
npm --version

# Check Python
python --version
pip --version

# Check Git (optional)
git --version
```

## Build Process Details

### What Gets Built
1. **Frontend**: Next.js app compiled to static files
2. **Python Bundle**: Complete virtual environment (~200MB)
3. **Electron App**: Desktop wrapper with all dependencies
4. **NSIS Installer**: Professional Windows installer

### Build Output Structure
```
electron\dist\
├── GeoAI Desktop Setup 1.0.0.exe    # Main installer
├── win-unpacked\                     # Development version
│   ├── GeoAI Desktop.exe            # Main executable
│   ├── resources\
│   │   ├── app.asar                 # Frontend code
│   │   └── backend\                 # Python environment
│   └── ...                         # Electron files
└── builder-debug.yml                # Build metadata
```

## Installation Experience

### Installer Features
- **Welcome Screen**: Professional installer interface
- **License Agreement**: MIT license display
- **Installation Path**: Customizable install location
- **Components**: Optional desktop/start menu shortcuts
- **Progress**: Real-time installation progress
- **Completion**: Launch option after install

### Default Installation Paths
- **Program Files**: `C:\Users\{user}\AppData\Local\Programs\geoai-desktop\`
- **User Data**: `C:\Users\{user}\AppData\Roaming\geoai-desktop\`
- **Desktop Shortcut**: Optional
- **Start Menu**: `GeoAI Desktop`

## Windows-Specific Features

### System Integration
- **Start Menu**: Automatic entry creation
- **Add/Remove Programs**: Proper uninstall support
- **File Associations**: Can be configured for document types
- **Context Menu**: Potential for "Open with GeoAI" option

### Security Considerations
- **SmartScreen**: May show warning for unsigned executables
- **Antivirus**: Some AV software may scan the Python bundle
- **UAC**: Runs as normal user, no admin rights needed
- **Firewall**: May prompt for network access (Ollama communication)

## Troubleshooting

### Build Issues

**"Python not found"**:
```batch
# Add Python to PATH
set PATH=%PATH%;C:\Python39;C:\Python39\Scripts
# OR reinstall Python with "Add to PATH" checked
```

**"npm not found"**:
```batch
# Restart Command Prompt after Node.js installation
# OR add to PATH manually
set PATH=%PATH%;C:\Program Files\nodejs
```

**"Access denied" errors**:
```powershell
# Run as Administrator (if needed)
# OR check folder permissions
icacls . /grant %USERNAME%:F
```

### Runtime Issues

**App won't start**:
1. Check Windows Event Viewer (Windows Logs > Application)
2. Run from Command Prompt to see error messages:
   ```batch
   cd "C:\Users\%USERNAME%\AppData\Local\Programs\geoai-desktop"
   "GeoAI Desktop.exe"
   ```
3. Check antivirus exclusions

**Backend connection issues**:
1. Windows Firewall may block connections
2. Check Task Manager for conflicting Python processes
3. Try different port range (app auto-finds available ports)

**Ollama integration issues**:
```batch
# Install Ollama for Windows
winget install Ollama.Ollama

# OR download from https://ollama.ai/download/windows

# Start Ollama service
ollama serve

# Test Ollama connection
curl http://localhost:11434/api/tags
```

### Performance Optimization

**Slow startup**:
- Install on SSD if possible
- Exclude from antivirus real-time scanning
- Close unnecessary background applications

**High memory usage**:
- Limit concurrent document processing
- Restart app periodically for memory cleanup
- Consider increasing virtual memory

## Distribution Strategies

### Direct Distribution
- Upload installer to GitHub releases
- Host on company website
- Share via email/network drives

### Microsoft Store (Future)
- Requires MSIX packaging
- Automatic updates
- Better security reputation
- Store approval process

### Enterprise Deployment
- Group Policy deployment
- System Center Configuration Manager
- PowerShell DSC scripts
- Silent installation options

### Silent Installation
```batch
# Install silently
"GeoAI Desktop Setup 1.0.0.exe" /S

# Install to specific directory
"GeoAI Desktop Setup 1.0.0.exe" /S /D=C:\MyApps\GeoAI

# Uninstall silently
"C:\Users\%USERNAME%\AppData\Local\Programs\geoai-desktop\Uninstall GeoAI Desktop.exe" /S
```

## Code Signing (Production)

### Why Sign Code
- Eliminates SmartScreen warnings
- Builds user trust
- Required for some enterprise environments
- Enables automatic updates

### Signing Process
1. **Obtain Certificate**: Purchase from DigiCert, Sectigo, etc.
2. **Configure electron-builder**:
   ```json
   "win": {
     "certificateFile": "certificate.p12",
     "certificatePassword": "password",
     "signingHashAlgorithms": ["sha256"]
   }
   ```
3. **Build with signing**: Normal build process will sign automatically

### Testing Signed Builds
```batch
# Verify signature
signtool verify /pa "GeoAI Desktop Setup 1.0.0.exe"

# Check certificate details
certlm.msc
```

## Monitoring and Analytics

### Crash Reporting
Consider integrating:
- **Sentry**: Error tracking and performance monitoring
- **Electron Crash Reporter**: Built-in crash reporting
- **Custom logging**: Application-specific logging

### Usage Analytics
- **Mixpanel**: User behavior tracking
- **Google Analytics**: Website-style analytics
- **Custom telemetry**: Privacy-focused internal analytics

## Maintenance and Updates

### Update Strategies
1. **Manual Updates**: Users download new installer
2. **Electron Updater**: Automatic update system
3. **Microsoft Store**: Automatic store updates
4. **Custom Updater**: Application-specific update mechanism

### Version Management
```json
{
  "version": "1.0.0",
  "buildVersion": "1.0.0.20231201",
  "releaseNotes": "Initial Windows release"
}
```

### Backward Compatibility
- Maintain user data format compatibility
- Graceful handling of old configuration files
- Database migration scripts when needed

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Windows Build
on: [push, pull_request]
jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Build Windows App
        run: .\build_windows_app.ps1
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: electron/dist/*.exe
```

### Azure DevOps Pipeline
```yaml
trigger:
- main

pool:
  vmImage: 'windows-latest'

steps:
- task: NodeTool@0
  inputs:
    versionSpec: '18.x'
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.9'
- script: .\build_windows_app.ps1
  displayName: 'Build Windows App'
- task: PublishBuildArtifacts@1
  inputs:
    pathtoPublish: 'electron/dist'
    artifactName: 'windows-build'
```

## Support and Documentation

### User Support
- Include help documentation in installer
- Create video tutorials for installation
- Provide troubleshooting FAQ
- Consider in-app help system

### Developer Support
- Maintain build documentation
- Create development environment setup guide
- Document common issues and solutions
- Provide debugging tips

---

*This guide covers the complete Windows deployment process from development to end-user installation.*