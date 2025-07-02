#!/bin/bash

# Icon Generation Script for GeoAI
# This script converts an SVG icon to all required formats for Mac and Windows

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "ImageMagick is required but not installed."
    echo "Install it using:"
    echo "  Mac: brew install imagemagick"
    echo "  Ubuntu: sudo apt-get install imagemagick"
    echo "  Windows: Download from https://imagemagick.org/script/download.php"
    exit 1
fi

# Check if source SVG exists
if [ ! -f "geoai-icon.svg" ]; then
    echo "Error: geoai-icon.svg not found in current directory"
    exit 1
fi

echo "Starting icon generation for GeoAI..."

# Create directories
mkdir -p icons/png
mkdir -p icons/iconset

# Generate PNG files from SVG
echo "Generating PNG files..."

# Standard sizes for both platforms
convert -background none -resize 16x16 geoai-icon.svg icons/png/icon-16.png
convert -background none -resize 24x24 geoai-icon.svg icons/png/icon-24.png
convert -background none -resize 32x32 geoai-icon.svg icons/png/icon-32.png
convert -background none -resize 48x48 geoai-icon.svg icons/png/icon-48.png
convert -background none -resize 64x64 geoai-icon.svg icons/png/icon-64.png
convert -background none -resize 128x128 geoai-icon.svg icons/png/icon-128.png
convert -background none -resize 256x256 geoai-icon.svg icons/png/icon-256.png
convert -background none -resize 512x512 geoai-icon.svg icons/png/icon-512.png
convert -background none -resize 1024x1024 geoai-icon.svg icons/png/icon-1024.png

echo "PNG files generated successfully!"

# Generate Windows ICO file
echo "Generating Windows ICO file..."
convert icons/png/icon-16.png icons/png/icon-24.png icons/png/icon-32.png \
        icons/png/icon-48.png icons/png/icon-64.png icons/png/icon-128.png \
        icons/png/icon-256.png icons/icon.ico

echo "Windows ICO file generated: icons/icon.ico"

# Generate macOS ICNS file
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Generating macOS ICNS file..."
    
    # Create iconset directory with properly named files
    cp icons/png/icon-16.png icons/iconset/icon_16x16.png
    cp icons/png/icon-32.png icons/iconset/icon_16x16@2x.png
    cp icons/png/icon-32.png icons/iconset/icon_32x32.png
    cp icons/png/icon-64.png icons/iconset/icon_32x32@2x.png
    cp icons/png/icon-128.png icons/iconset/icon_128x128.png
    cp icons/png/icon-256.png icons/iconset/icon_128x128@2x.png
    cp icons/png/icon-256.png icons/iconset/icon_256x256.png
    cp icons/png/icon-512.png icons/iconset/icon_256x256@2x.png
    cp icons/png/icon-512.png icons/iconset/icon_512x512.png
    cp icons/png/icon-1024.png icons/iconset/icon_512x512@2x.png
    
    # Use iconutil to create ICNS
    iconutil -c icns -o icons/icon.icns icons/iconset
    
    echo "macOS ICNS file generated: icons/icon.icns"
    
    # Clean up iconset
    rm -rf icons/iconset
else
    echo "Note: ICNS generation requires macOS. You can use online converters for other platforms."
fi

# Copy Linux icon
cp icons/png/icon-512.png icons/icon.png
echo "Linux PNG icon copied: icons/icon.png"

# Create electron assets directory structure
echo "Setting up Electron assets..."
mkdir -p electron/assets
cp icons/icon.ico electron/assets/
cp icons/icon.png electron/assets/
if [ -f icons/icon.icns ]; then
    cp icons/icon.icns electron/assets/
fi

echo ""
echo "✅ Icon generation complete!"
echo ""
echo "Generated files:"
echo "  - icons/icon.ico (Windows)"
echo "  - icons/icon.png (Linux)"
if [ -f icons/icon.icns ]; then
    echo "  - icons/icon.icns (macOS)"
fi
echo "  - icons/png/ (All PNG sizes)"
echo ""
echo "Files have been copied to electron/assets/ for your build."
echo ""
echo "If you're not on macOS and need an ICNS file, use:"
echo "  - https://cloudconvert.com/png-to-icns"
echo "  - Upload icons/png/icon-1024.png"