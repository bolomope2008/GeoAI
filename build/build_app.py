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

def find_npm_on_windows():
    """
    Searches for npm.cmd in common Node.js installation paths on Windows
    and adds its directory to PATH if found.
    """
    if platform.system().lower() != "windows":
        return

    common_paths = [
        Path(os.environ.get('ProgramFiles', '')) / "nodejs",
        Path(os.environ.get('ProgramFiles(x86)', '')) / "nodejs",
        Path(os.environ.get('LOCALAPPDATA', '')) / "Programs" / "nodejs",
        Path(os.environ.get('APPDATA', '')) / "npm"
    ]

    for p in common_paths:
        npm_path = p / "npm.cmd"
        if npm_path.exists():
            print(f"Found npm.cmd at: {npm_path}")
            # Add to PATH if not already there
            if str(p) not in os.environ['PATH']:
                os.environ['PATH'] = f"{p};{os.environ['PATH']}"
                print(f"Added {p} to PATH.")
            return

    print("npm.cmd not found in common Node.js installation paths.")


def check_prerequisites():
    """Check if required tools are installed"""
    required_tools = []
    
    # Ensure npm is discoverable on Windows
    find_npm_on_windows()

    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"OK: Node.js: {result.stdout.strip()}")
        else:
            required_tools.append("Node.js")
    except FileNotFoundError:
        required_tools.append("Node.js")
    
    # Check npm directly from PATH
    npm_found = False
    for path_dir in os.environ['PATH'].split(os.pathsep):
        npm_cmd_path = Path(path_dir) / "npm.cmd"
        if npm_cmd_path.exists():
            print(f"OK: npm: {npm_cmd_path}")
            npm_found = True
            break
    if not npm_found:
        required_tools.append("npm")
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"OK: Python: {result.stdout.strip()}")
        else:
            required_tools.append("Python")
    except FileNotFoundError:
        required_tools.append("Python")
    
    return required_tools

def build_macos():
    """Build for macOS"""
    print("Building for macOS...")
    # Get the directory containing this script (build/)
    script_dir = Path(__file__).parent
    script_path = script_dir / "build_complete_app.sh"
    
    if not script_path.exists():
        print("Error: build_complete_app.sh not found")
        return False
    
    # Make script executable
    os.chmod(script_path, 0o755)
    
    # Run the build script
    result = subprocess.run([str(script_path)], shell=True)
    return result.returncode == 0

def build_windows():
    """Build for Windows"""
    print("Building for Windows...")
    
    # Get the directory containing this script (build/)
    script_dir = Path(__file__).parent
    ps_script = script_dir / "build_windows_app.ps1"
    bat_script = script_dir / "build_windows_app.bat"
    
    # Try PowerShell script first, then batch script
    if ps_script.exists():
        print("Using PowerShell script...")
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)], env=os.environ)
        return result.returncode == 0
    elif bat_script.exists():
        print("Using batch script...")
        result = subprocess.run([str(bat_script)], shell=True, env=os.environ)
        return result.returncode == 0
    else:
        print("Error: No Windows build script found")
        return False

def build_linux():
    """Build for Linux (future implementation)"""
    print("Linux builds not yet implemented")
    print("You can manually adapt the macOS build script for Linux")
    return False

def main():
    """Main build function"""
    print("GeoAI Desktop Cross-Platform Builder")
    print("=" * 50)
    
    # Detect platform
    current_platform = get_platform()
    print(f"Platform detected: {current_platform}")
    print()
    
    # Check prerequisites
    print("Checking prerequisites...")
    missing_tools = check_prerequisites()
    
    if missing_tools:
        print("Error: Missing required tools:")
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
        print(f"Error: Unsupported platform: {current_platform}")
        return 1
    
    # Report results
    print()
    print("=" * 50)
    if success:
        print("OK: Build completed successfully!")
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
        print("Error: Build failed!")
        print("Check the error messages above for details")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())