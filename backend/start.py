#!/usr/bin/env python3
"""
Startup script for GeoAI Backend

This script handles dynamic port allocation and environment variable setup
for both development and production (Electron) environments.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    # Get port from environment variable (set by Electron) or default to 8000
    port = int(os.environ.get('BACKEND_PORT', 8000))
    host = os.environ.get('BACKEND_HOST', '127.0.0.1')
    
    # Set up user data directories if provided by Electron
    if 'KNOWLEDGE_BASE_DIR' in os.environ:
        print(f"Using knowledge base directory: {os.environ['KNOWLEDGE_BASE_DIR']}")
    if 'CHROMA_DB_DIR' in os.environ:
        print(f"Using ChromaDB directory: {os.environ['CHROMA_DB_DIR']}")
    if 'CONFIG_DIR' in os.environ:
        print(f"Using config directory: {os.environ['CONFIG_DIR']}")
    
    # Log startup information
    print(f"Starting GeoAI Backend on {host}:{port}")
    print(f"Python path: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    # Import here to ensure path is set
    from api import app
    
    # Start the server
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,  # Disable reload in production
            log_level="info"
        )
    except Exception as e:
        print(f"Failed to start backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()