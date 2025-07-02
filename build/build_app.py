#!/usr/bin/env python3
"""
Cross-platform build script for GeoAI Desktop
Automatically detects the operating system and runs the appropriate build process
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def get_platform():
    """Detect the current platform"""
    system = platform.system().lower()
    if system == "darwin":
        return "macOS"
    elif system == "windows":
        return "Windows"
    elif system == "linux":
        return "Linux"
    else:
        return "Unknown"

def check_prerequisites():
    """Check if required tools are installed"""
    required_tools = []
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Node.js: {result.stdout.strip()}")
        else:
            required_tools.append("Node.js")
    except FileNotFoundError:
        required_tools.append("Node.js")
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ npm: {result.stdout.strip()}")
        else:
            required_tools.append("npm")
    except FileNotFoundError:
        required_tools.append("npm")
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Python: {result.stdout.strip()}")
        else:
            required_tools.append("Python")
    except FileNotFoundError:
        required_tools.append("Python")
    
    return required_tools

def build_macos():
    """Build for macOS"""
    print("🍎 Building for macOS...")
    # Get the directory containing this script (build/)
    script_dir = Path(__file__).parent
    script_path = script_dir / "build_complete_app.sh"
    
    if not script_path.exists():
        print("❌ Error: build_complete_app.sh not found")
        return False
    
    # Make script executable
    os.chmod(script_path, 0o755)
    
    # Run the build script
    result = subprocess.run([str(script_path)], shell=True)
    return result.returncode == 0

def build_windows():
    """Build for Windows"""
    print("🪟 Building for Windows...")
    
    # Get the directory containing this script (build/)
    script_dir = Path(__file__).parent
    ps_script = script_dir / "build_windows_app.ps1"
    bat_script = script_dir / "build_windows_app.bat"
    
    # Try PowerShell script first, then batch script
    if ps_script.exists():
        print("Using PowerShell script...")
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)])
        return result.returncode == 0
    elif bat_script.exists():
        print("Using batch script...")
        result = subprocess.run([str(bat_script)], shell=True)
        return result.returncode == 0
    else:
        print("❌ Error: No Windows build script found")
        return False

def build_linux():
    """Build for Linux (future implementation)"""
    print("🐧 Linux builds not yet implemented")
    print("You can manually adapt the macOS build script for Linux")
    return False

def main():
    """Main build function"""
    print("🚀 GeoAI Desktop Cross-Platform Builder")
    print("=" * 50)
    
    # Detect platform
    current_platform = get_platform()
    print(f"Platform detected: {current_platform}")
    print()
    
    # Check prerequisites
    print("Checking prerequisites...")
    missing_tools = check_prerequisites()
    
    if missing_tools:
        print("❌ Missing required tools:")
        for tool in missing_tools:
            print(f"   - {tool}")
        print()
        if current_platform == "macOS":
            print("Install missing tools:")
            print("  Node.js: https://nodejs.org or `brew install node`")
            print("  Python: https://python.org or `brew install python`")
        elif current_platform == "Windows":
            print("Install missing tools:")
            print("  Node.js: https://nodejs.org")
            print("  Python: https://python.org")
        return 1
    
    print()
    
    # Run platform-specific build
    success = False
    if current_platform == "macOS":
        success = build_macos()
    elif current_platform == "Windows":
        success = build_windows()
    elif current_platform == "Linux":
        success = build_linux()
    else:
        print(f"❌ Unsupported platform: {current_platform}")
        return 1
    
    # Report results
    print()
    print("=" * 50)
    if success:
        print("✅ Build completed successfully!")
        print()
        if current_platform == "macOS":
            print("Output: electron/dist/*.dmg")
        elif current_platform == "Windows":
            print("Output: electron/dist/*.exe")
        print()
        print("Next steps:")
        print("1. Test the built application")
        print("2. Install Ollama for AI features")
        print("3. Distribute to end users")
    else:
        print("❌ Build failed!")
        print("Check the error messages above for details")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())