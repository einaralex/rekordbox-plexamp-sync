"""
py2app setup script for building a standalone macOS application.

This script builds a standalone .app bundle that can be distributed to users
without requiring them to install Python or any dependencies.

Usage:
    # Development/alias mode (for testing)
    python setup_py2app.py py2app -A

    # Production build (creates standalone .app)
    python setup_py2app.py py2app

    # The resulting app will be in: dist/RekordboxSync.app

Requirements:
    pip install py2app

Note: Make sure to update APP_NAME and adjust OPTIONS as needed for your app.
"""

from setuptools import setup

# The main script that launches your app
APP = ['standalone_menubar_app.py']

# Additional data files to include (if any)
DATA_FILES = []

# py2app options
OPTIONS = {
    # Basic app metadata
    'argv_emulation': False,  # Don't emulate sys.argv (not needed for menu bar apps)
    'iconfile': None,  # Path to .icns file (create one if you want a custom icon)
    # Python packages to include
    'packages': [
        'rekordbox_plexamp_sync',
        'plexapi',
        'rumps',
        'requests',
        'urllib3',
        'tqdm',
        'ctypes',
        'json',
    ],
    # Modules to explicitly include
    'includes': [
        'ctypes',
        'json',
    ],
    # Exclude unnecessary packages to reduce app size
    'excludes': [
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'IPython',
        'pygments',
        'PIL',
        'wx',
    ],
    # Resources to include
    'resources': [],
    # Strip debug symbols (makes app smaller)
    'strip': True,
    # Don't use system python (ensures it works on other Macs)
    'semi_standalone': False,
    # macOS plist settings
    'plist': {
        'CFBundleName': 'RekordboxSync',
        'CFBundleDisplayName': 'Rekordbox to Plex Sync',
        'CFBundleIdentifier': 'com.yourcompany.rekordboxsync',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHumanReadableCopyright': 'Copyright © 2024. All rights reserved.',
        'LSUIElement': True,  # Hide from Dock (menu bar only)
        'LSBackgroundOnly': False,
        'NSHighResolutionCapable': True,
    },
}

setup(
    name='RekordboxSync',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

"""
Build Instructions:
===================

1. Install dependencies:
   pip install rekordbox-plexamp-sync rumps py2app

2. Build the app:
   python setup_py2app.py py2app

3. Test the app:
   open dist/RekordboxSync.app

4. For debugging, use alias mode:
   python setup_py2app.py py2app -A
   ./dist/RekordboxSync.app/Contents/MacOS/RekordboxSync

5. To clean build artifacts:
   rm -rf build dist

Distribution:
=============

The resulting .app bundle in dist/ can be:
- Compressed into a .zip file for distribution
- Notarized for distribution outside the Mac App Store
- Distributed via DMG for a professional installer experience

Creating a DMG:
--------------
hdiutil create -volname "Rekordbox Sync" -srcfolder dist/RekordboxSync.app \
  -ov -format UDZO RekordboxSync.dmg

Code Signing (Optional but Recommended):
---------------------------------------
1. Get a Developer ID certificate from Apple
2. Sign the app:
   codesign --deep --force --verify --verbose \
     --sign "Developer ID Application: Your Name" \
     dist/RekordboxSync.app

3. Verify signature:
   codesign --verify --verbose=4 dist/RekordboxSync.app

Notarization (Required for macOS 10.15+):
-----------------------------------------
1. Create an app-specific password at appleid.apple.com
2. Submit for notarization:
   xcrun notarytool submit RekordboxSync.zip \
     --apple-id your@email.com \
     --password your-app-specific-password \
     --team-id YOUR_TEAM_ID

3. Staple the notarization:
   xcrun stapler staple dist/RekordboxSync.app

Troubleshooting:
===============

If the app crashes on launch:
- Run in alias mode for debugging: python setup_py2app.py py2app -A
- Check Console.app for error messages
- Ensure library.so is included and accessible

If library.so is not found:
- Add it explicitly to resources in OPTIONS:
  'resources': ['path/to/library.so']

If dependencies are missing:
- Add them to 'packages' or 'includes' in OPTIONS
- Use --packages option: python setup_py2app.py py2app --packages=missing_package

Common Issues:
-------------
1. "No module named 'rumps'" - Add 'rumps' to packages
2. "library.so not found" - Add library.so to resources or ensure it's in the package
3. App icon not showing - Create an .icns file and set iconfile path
4. App appears in Dock - Set LSUIElement to True in plist
"""
