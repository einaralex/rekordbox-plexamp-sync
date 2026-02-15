#!/bin/bash
# PyInstaller Build Script for Rekordbox Sync Menu Bar App
#
# This script builds a standalone macOS application using PyInstaller.
# PyInstaller is often simpler than py2app and works well for menu bar apps.
#
# Usage:
#   chmod +x build_with_pyinstaller.sh
#   ./build_with_pyinstaller.sh
#
# Requirements:
#   pip install pyinstaller rekordbox-plexamp-sync rumps

set -e  # Exit on error

echo "🚀 Building Rekordbox Sync with PyInstaller..."
echo ""

# Configuration
APP_NAME="RekordboxSync"
SCRIPT_NAME="standalone_menubar_app.py"
ICON_FILE=""  # Set to path of .icns file if you have one

# Check if script exists
if [ ! -f "$SCRIPT_NAME" ]; then
    echo "❌ Error: $SCRIPT_NAME not found in current directory"
    echo "   Make sure you're running this from the examples/ directory"
    exit 1
fi

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist "$APP_NAME.spec"

# Build the app
echo "📦 Building $APP_NAME.app..."

BUILD_CMD="pyinstaller \
    --name=$APP_NAME \
    --windowed \
    --onefile \
    --noconfirm \
    --clean"

# Add icon if specified
if [ -n "$ICON_FILE" ] && [ -f "$ICON_FILE" ]; then
    BUILD_CMD="$BUILD_CMD --icon=$ICON_FILE"
fi

# Hidden imports (add any modules that PyInstaller misses)
BUILD_CMD="$BUILD_CMD \
    --hidden-import=rumps \
    --hidden-import=plexapi \
    --hidden-import=rekordbox_plexamp_sync \
    --hidden-import=ctypes \
    --hidden-import=json"

# Collect data files (add library.so if needed)
# BUILD_CMD="$BUILD_CMD --add-data=/path/to/library.so:."

# Execute build
BUILD_CMD="$BUILD_CMD $SCRIPT_NAME"
eval $BUILD_CMD

# Check if build succeeded
if [ -d "dist/$APP_NAME.app" ]; then
    echo ""
    echo "✅ Build successful!"
    echo "📍 App location: dist/$APP_NAME.app"
    echo ""
    echo "To test the app:"
    echo "  open dist/$APP_NAME.app"
    echo ""
    echo "To distribute:"
    echo "  1. Test the app thoroughly"
    echo "  2. Code sign it (optional):"
    echo "     codesign --deep --force --sign 'Developer ID Application: Your Name' dist/$APP_NAME.app"
    echo "  3. Create a DMG:"
    echo "     hdiutil create -volname '$APP_NAME' -srcfolder dist/$APP_NAME.app -ov -format UDZO $APP_NAME.dmg"
    echo ""
else
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi

# Optional: Create DMG automatically
read -p "📦 Create DMG installer? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating DMG..."
    hdiutil create -volname "$APP_NAME" -srcfolder "dist/$APP_NAME.app" \
        -ov -format UDZO "$APP_NAME.dmg"
    echo "✅ DMG created: $APP_NAME.dmg"
fi

echo ""
echo "🎉 Done!"
