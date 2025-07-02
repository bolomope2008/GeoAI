#!/usr/bin/env python3
"""
Create a standalone Python bundle for GeoAI backend
This creates a portable Python environment with all dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_standalone_bundle():
    print("Creating standalone Python bundle for GeoAI backend...")
    
    # Get the directory of this script
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent
    
    # Create bundle directory
    bundle_dir = backend_dir / "python_bundle"
    if bundle_dir.exists():
        print(f"Removing existing bundle directory...")
        shutil.rmtree(bundle_dir)
    
    bundle_dir.mkdir()
    
    # Create a virtual environment
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", str(bundle_dir / "venv")], check=True)
    
    # Determine pip path
    if sys.platform == "darwin" or sys.platform == "linux":
        pip_path = bundle_dir / "venv" / "bin" / "pip"
        python_path = bundle_dir / "venv" / "bin" / "python"
    else:
        pip_path = bundle_dir / "venv" / "Scripts" / "pip.exe"
        python_path = bundle_dir / "venv" / "Scripts" / "python.exe"
    
    # Upgrade pip
    print("Upgrading pip...")
    subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # Install requirements
    print("Installing requirements (this may take a few minutes)...")
    requirements_file = backend_dir / "requirements.txt"
    subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
    
    # Copy Python files
    print("Copying Python source files...")
    for py_file in backend_dir.glob("*.py"):
        shutil.copy2(py_file, bundle_dir)
    
    # Create a launcher script
    print("Creating launcher script...")
    launcher_content = '''#!/usr/bin/env python3
import os
import sys
import subprocess

# Add the bundle directory to Python path
bundle_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, bundle_dir)

# Set up environment
if sys.platform == "darwin" or sys.platform == "linux":
    python_exe = os.path.join(bundle_dir, "venv", "bin", "python")
else:
    python_exe = os.path.join(bundle_dir, "venv", "Scripts", "python.exe")

# Run the backend
subprocess.run([python_exe, os.path.join(bundle_dir, "start.py")] + sys.argv[1:])
'''
    
    launcher_path = bundle_dir / "run_backend.py"
    launcher_path.write_text(launcher_content)
    launcher_path.chmod(0o755)
    
    # Create info file
    info_content = f"""GeoAI Backend Bundle
Created: {subprocess.check_output(['date']).decode().strip()}
Python Version: {sys.version}
Platform: {sys.platform}

This is a self-contained Python environment with all dependencies for GeoAI.
"""
    (bundle_dir / "INFO.txt").write_text(info_content)
    
    print(f"\n✅ Bundle created successfully at: {bundle_dir}")
    print(f"   Total size: {sum(f.stat().st_size for f in bundle_dir.rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB")
    
    return bundle_dir

if __name__ == "__main__":
    create_standalone_bundle()