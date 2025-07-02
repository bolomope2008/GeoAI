@echo off
setlocal enabledelayedexpansion

echo =====================================
echo GeoAI Desktop Windows Build Process
echo =====================================
echo.

REM Navigate to project root (parent of build directory)
cd /d "%~dp0\.."
set PROJECT_ROOT=%CD%

REM Step 1: Build frontend
echo Step 1: Building frontend...
cd frontend\my-app
call npm install
if errorlevel 1 (
    echo Error: Frontend npm install failed
    exit /b 1
)
call npm run build
if errorlevel 1 (
    echo Error: Frontend build failed
    exit /b 1
)
cd "%PROJECT_ROOT%"

REM Step 2: Create Python bundle with all dependencies
echo.
echo Step 2: Creating Python bundle with all dependencies...
echo This will take several minutes as it downloads and packages all Python libraries...
cd backend
python create_bundle.py
if errorlevel 1 (
    echo Error: Python bundle creation failed
    exit /b 1
)
cd "%PROJECT_ROOT%"

REM Step 3: Update Electron configuration
echo.
echo Step 3: Updating Electron configuration...

REM Check if icon file exists
if not exist "assets\icon.ico" (
    echo Warning: assets\icon.ico not found. Creating placeholder...
    if not exist "assets" mkdir assets
    echo. > assets\icon.ico
)

cd electron

REM Step 4: Install Electron dependencies
echo.
echo Step 4: Installing Electron dependencies...
call npm install
if errorlevel 1 (
    echo Error: Electron npm install failed
    exit /b 1
)

REM Step 5: Build Electron app for Windows
echo.
echo Step 5: Building Electron app for Windows...
call npm run dist:win
if errorlevel 1 (
    echo Error: Electron build failed
    exit /b 1
)

cd "%PROJECT_ROOT%"

echo.
echo =====================================
echo ✅ Windows Build Complete!
echo =====================================
echo.
echo Installer created in: electron\dist\
echo.
echo The app now includes:
echo - Complete Python environment
echo - All Python dependencies  
echo - No external requirements needed!
echo.
echo Users can:
echo 1. Run the installer (.exe)
echo 2. Follow installation wizard
echo 3. Launch GeoAI Desktop from Start Menu
echo.
echo Note: Users still need to install Ollama separately for AI features.
echo.
pause