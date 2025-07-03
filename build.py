#!/usr/bin/env python3
"""
GeoAI Desktop Build Launcher
Simple launcher script that delegates to the main build system in build/
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the main build script"""
    # Get the directory containing this script (project root)
    project_root = Path(__file__).parent
    
    # Path to the main build script
    main_build_script = project_root / "build" / "build_app.py"
    
    if not main_build_script.exists():
        print("Error: Main build script not found at build/build_app.py")
        return 1
    
    print("GeoAI Desktop Build Launcher")
    print("Delegating to main build system...")
    print()
    
    # Run the main build script with all arguments
    try:
        result = subprocess.run([sys.executable, str(main_build_script)] + sys.argv[1:])
        return result.returncode
    except KeyboardInterrupt:
        print("\nBuild cancelled by user")
        return 1
    except Exception as e:
        print(f"Error launching build script: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())