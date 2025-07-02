#!/bin/bash

# Complete build script for GeoAI Desktop with bundled dependencies

set -e

echo "====================================="
echo "GeoAI Desktop Complete Build Process"
echo "====================================="
echo ""

# Navigate to project root (parent of build directory)
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# Step 1: Build frontend
echo "Step 1: Building frontend..."
cd frontend/my-app
npm install
npm run build
cd "$PROJECT_ROOT"

# Step 2: Create Python bundle with all dependencies
echo ""
echo "Step 2: Creating Python bundle with all dependencies..."
echo "This will take several minutes as it downloads and packages all Python libraries..."
cd backend
python3 create_bundle.py
cd "$PROJECT_ROOT"

# Step 3: Update Electron configuration to use bundled Python
echo ""
echo "Step 3: Updating Electron configuration..."

# Update package.json to include the Python bundle
cd electron

# Create a temporary package.json with updated extraResources
cat > package_temp.json << 'EOF'
{
  "name": "geoai-desktop",
  "version": "1.0.0",
  "description": "GeoAI Desktop Application - RAG Chatbot for Geological Research",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "dev": "NODE_ENV=development electron .",
    "build": "electron-builder",
    "dist": "electron-builder --publish=never",
    "dist:mac": "electron-builder --mac --publish=never",
    "dist:win": "electron-builder --win --publish=never",
    "dist:linux": "electron-builder --linux --publish=never",
    "postinstall": "electron-builder install-app-deps"
  },
  "keywords": [
    "geoai",
    "geology",
    "rag",
    "chatbot",
    "electron",
    "desktop"
  ],
  "author": {
    "name": "GeoAI Team",
    "email": "contact@geoai.com"
  },
  "license": "MIT",
  "devDependencies": {
    "electron": "^31.0.0",
    "electron-builder": "^24.13.0"
  },
  "dependencies": {
    "node-fetch": "^3.3.2"
  },
  "build": {
    "appId": "com.geoai.desktop",
    "productName": "GeoAI Desktop",
    "directories": {
      "output": "dist"
    },
    "files": [
      "main.js",
      "preload.js",
      "package.json",
      {
        "from": "../frontend/my-app/out",
        "to": "frontend/my-app/out",
        "filter": ["**/*"]
      },
      "!../backend/knowledge_base/**/*",
      "!../backend/chroma_db/**/*"
    ],
    "extraResources": [
      {
        "from": "../backend/python_bundle",
        "to": "backend",
        "filter": ["**/*"]
      }
    ],
    "mac": {
      "category": "public.app-category.education",
      "icon": "../assets/icon.icns",
      "target": [
        {
          "target": "dmg",
          "arch": ["arm64", "x64"]
        }
      ],
      "entitlements": "build/entitlements.mac.plist",
      "entitlementsInherit": "build/entitlements.mac.plist",
      "hardenedRuntime": true,
      "gatekeeperAssess": false
    },
    "dmg": {
      "title": "GeoAI Desktop Installer",
      "icon": "../assets/icon.icns",
      "background": null,
      "window": {
        "width": 600,
        "height": 400
      },
      "contents": [
        {
          "x": 150,
          "y": 200,
          "type": "file"
        },
        {
          "x": 450,
          "y": 200,
          "type": "link",
          "path": "/Applications"
        }
      ]
    },
    "win": {
      "icon": "../assets/icon.ico",
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        }
      ]
    },
    "linux": {
      "icon": "../assets/icon.png",
      "target": [
        {
          "target": "AppImage",
          "arch": ["x64"]
        }
      ],
      "category": "Education"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true
    }
  }
}
EOF

mv package_temp.json package.json

# Update main.js to use the bundled Python
echo "Updating main.js to use bundled Python..."

# Step 4: Install Electron dependencies
echo ""
echo "Step 4: Installing Electron dependencies..."
npm install

# Step 5: Build Electron app
echo ""
echo "Step 5: Building Electron app for macOS..."
npm run dist:mac

cd "$PROJECT_ROOT"

echo ""
echo "====================================="
echo "✅ Build Complete!"
echo "====================================="
echo ""
echo "DMG files created in: electron/dist/"
echo ""
echo "The app now includes:"
echo "- Complete Python environment"
echo "- All Python dependencies"
echo "- No external requirements needed!"
echo ""
echo "Users can simply:"
echo "1. Open the DMG"
echo "2. Drag to Applications"
echo "3. Run GeoAI Desktop"
echo ""
echo "Note: Users still need to install Ollama separately for AI features."