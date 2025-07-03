# GeoAI Desktop Windows Build Script (PowerShell)
# This script builds the complete Windows application with bundled dependencies

param(
    [switch]$SkipFrontend = $false,
    [switch]$SkipPython = $false,
    [switch]$Verbose = $false
)

# Function to log messages
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $(
        switch ($Level) {
            "ERROR" { "Red" }
            "WARN" { "Yellow" }
            "SUCCESS" { "Green" }
            default { "White" }
        }
    )
}

# Start build process
Write-Log "Starting GeoAI Desktop Windows Build Process" "SUCCESS"
Write-Log "=============================================" "SUCCESS"

# Get project root directory (parent of build directory)
$PROJECT_ROOT = Split-Path $PSScriptRoot -Parent
Set-Location $PROJECT_ROOT

# Check prerequisites
Write-Log "Checking prerequisites..."

# Check Python version
$pythonVersion = python --version 2>&1
Write-Log "Found Python: $pythonVersion"

# Step 1: Build frontend
if (-not $SkipFrontend) {
    Write-Log "Step 1: Building frontend..." "SUCCESS"
    
    Set-Location "$PROJECT_ROOT\frontend\my-app"
    
    Write-Log "Installing frontend dependencies..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Frontend npm install failed" "ERROR"
        exit 1
    }
    
    Write-Log "Building frontend..."
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Frontend build failed" "ERROR"
        exit 1
    }
    
    Set-Location $PROJECT_ROOT
    Write-Log "Frontend build completed successfully" "SUCCESS"
} else {
    Write-Log "Skipping frontend build (--SkipFrontend specified)" "WARN"
}

# Step 2: Create Python bundle
if (-not $SkipPython) {
    Write-Log "Step 2: Creating Python bundle with all dependencies..." "SUCCESS"
    Write-Log "This will take several minutes as it downloads and packages all Python libraries..."
    
    Set-Location "$PROJECT_ROOT\backend"
    
    & python create_bundle.py
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Python bundle creation failed" "ERROR"
        exit 1
    }
    
    Set-Location $PROJECT_ROOT
    Write-Log "Python bundle created successfully" "SUCCESS"
} else {
    Write-Log "Skipping Python bundle creation (--SkipPython specified)" "WARN"
}

# Step 3: Check for icon file
Write-Log "Step 3: Checking assets..." "SUCCESS"

if (-not (Test-Path "assets\icon.ico")) {
    Write-Log "Warning: assets\icon.ico not found" "WARN"
    Write-Log "The build will continue but the app may not have a proper icon"
    
    # Create assets directory if it doesn't exist
    if (-not (Test-Path "assets")) {
        New-Item -ItemType Directory -Path "assets" | Out-Null
    }
}

# Step 4: Install Electron dependencies
Write-Log "Step 4: Installing Electron dependencies..." "SUCCESS"

Set-Location "$PROJECT_ROOT\electron"

npm install
if ($LASTEXITCODE -ne 0) {
    Write-Log "Electron npm install failed" "ERROR"
    exit 1
}

# Step 5: Build Electron app for Windows
Write-Log "Step 5: Building Electron app for Windows..." "SUCCESS"

npm run dist:win
if ($LASTEXITCODE -ne 0) {
    Write-Log "Electron build failed" "ERROR"
    exit 1
}

Set-Location $PROJECT_ROOT

# Build completed successfully
Write-Log ""
Write-Log "=============================================" "SUCCESS"
Write-Log "Windows Build Complete!" "SUCCESS"
Write-Log "=============================================" "SUCCESS"
Write-Log ""

# Check build output
$distPath = "$PROJECT_ROOT\electron\dist"
if (Test-Path $distPath) {
    $installers = Get-ChildItem $distPath -Filter "*.exe" | Sort-Object Name
    
    if ($installers.Count -gt 0) {
        Write-Log "Installers created in: electron\dist\" "SUCCESS"
        foreach ($installer in $installers) {
            $sizeInMB = [math]::Round($installer.Length / 1MB, 1)
            Write-Log "  - $($installer.Name) ($sizeInMB MB)" "SUCCESS"
        }
    } else {
        Write-Log "No installer files found in dist directory" "WARN"
    }
} else {
    Write-Log "Dist directory not found" "ERROR"
}

Write-Log ""
Write-Log "The app now includes:" "SUCCESS"
Write-Log "- Complete Python environment"
Write-Log "- All Python dependencies"
Write-Log "- No external requirements needed!"
Write-Log ""
Write-Log "Users can:" "SUCCESS"
Write-Log "1. Run the installer (.exe)"
Write-Log "2. Follow installation wizard"
Write-Log "3. Launch GeoAI Desktop from Start Menu or Desktop"
Write-Log ""
Write-Log "Note: Users still need to install Ollama separately for AI features." "WARN"
Write-Log "Ollama can be downloaded from: https://ollama.ai"

Write-Log ""
Write-Log "Build process completed successfully!" "SUCCESS"