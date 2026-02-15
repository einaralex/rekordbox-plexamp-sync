# Packaging Guide for rekordbox-plexamp-sync

This guide explains how to use the `rekordbox-plexamp-sync` package in different contexts, especially for building a macOS menu bar application.

## Table of Contents

- [Installation](#installation)
- [Package Structure](#package-structure)
- [Using in Your Application](#using-in-your-application)
- [Building the Package](#building-the-package)
- [Publishing to PyPI](#publishing-to-pypi)
- [Menu Bar App Integration](#menu-bar-app-integration)
- [Troubleshooting](#troubleshooting)

## Installation

### From Local Build

If you've built the package locally:

```bash
# Install from wheel
pip install dist/rekordbox_plexamp_sync-0.1.0-py3-none-any.whl

# Or install in editable/development mode
pip install -e .
```

### From PyPI (after publishing)

```bash
pip install rekordbox-plexamp-sync
```

### Dependencies

The package automatically installs these dependencies:
- `certifi>=2022.6.15`
- `charset-normalizer>=2.1.0`
- `idna>=3.3`
- `PlexAPI>=4.12.1`
- `requests>=2.28.1`
- `tqdm>=4.65.0`
- `urllib3>=1.26.11`

## Package Structure

```
rekordbox_plexamp_sync/
├── __init__.py          # Package exports
├── cli.py               # Command-line interface
├── core.py              # Core sync logic
├── logger.py            # Logging utilities
└── library.so           # Go shared library for rekordbox DB access
```

### Public API

The package exports the following functions and classes:

```python
from rekordbox_plexamp_sync import (
    build_plex_track_map,      # Build map of Plex tracks
    build_plex_playlist_map,   # Build map of Plex playlists
    get_playlists,             # Get playlists from rekordbox
    Logger,                    # Logger class
)

from rekordbox_plexamp_sync.core import (
    sync_playlists,            # Main sync function
    print_sync_summary,        # Print sync results
)
```

## Using in Your Application

### Basic Usage

```python
from plexapi.server import PlexServer
from rekordbox_plexamp_sync import (
    Logger,
    build_plex_track_map,
    build_plex_playlist_map,
    get_playlists,
)
from rekordbox_plexamp_sync.core import sync_playlists

# Initialize
logger = Logger(verbose=False)  # Set verbose=True for detailed output
plex = PlexServer('http://localhost:32400', 'your-token')

# Get rekordbox playlists
rekordbox_playlists = get_playlists()

# Build maps (do this once and cache the results)
track_map = build_plex_track_map(plex, logger)
playlist_map = build_plex_playlist_map(plex, logger)

# Sync
result = sync_playlists(
    plex=plex,
    rekordbox_playlists=rekordbox_playlists,
    track_map=track_map,
    playlist_map=playlist_map,
    logger=logger,
)

# Check results
print(f"Created: {len(result['created_playlists'])}")
print(f"Updated: {len(result['updated_playlists'])}")
```

### Return Value Structure

The `sync_playlists()` function returns a dictionary with:

```python
{
    'created_playlists': [
        {'name': 'Playlist Name', 'tracks': 42},
        # ...
    ],
    'updated_playlists': [
        {
            'name': 'Playlist Name',
            'old_tracks': 40,
            'new_tracks': 42,
            'added': 2
        },
        # ...
    ],
    'skipped_playlists': [
        {'name': 'Playlist Name', 'reason': 'No tracks'},
        # ...
    ],
    'smart_playlists_skipped': ['Smart Playlist 1', 'Smart Playlist 2'],
    'not_found_tracks': [
        {
            'playlist': 'Playlist Name',
            'file_name': 'track.mp3',
            'full_path': '/path/to/track.mp3',
            'title': 'Track Title'
        },
        # ...
    ]
}
```

## Building the Package

### Prerequisites

```bash
# Activate your virtual environment
source venv/bin/activate

# Install build tools
pip install build twine
```

### Build the Shared Library

The package includes a Go shared library for reading the rekordbox database. Build it first:

```bash
make
```

This creates `library.so` which is automatically included in the package.

### Build the Python Package

```bash
# Build both wheel and source distribution
python -m build

# Output will be in dist/:
# - rekordbox_plexamp_sync-0.1.0-py3-none-any.whl
# - rekordbox_plexamp_sync-0.1.0.tar.gz
```

### Test the Package Locally

```bash
# Install in editable mode for development
pip install -e .

# Or install the built wheel
pip install dist/rekordbox_plexamp_sync-0.1.0-py3-none-any.whl

# Test the CLI
rekordbox-plexamp-sync --help
```

## Publishing to PyPI

### Test on TestPyPI First

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI to test
pip install --index-url https://test.pypi.org/simple/ rekordbox-plexamp-sync
```

### Publish to PyPI

```bash
# Upload to PyPI (requires PyPI account and API token)
python -m twine upload dist/*

# Install from PyPI
pip install rekordbox-plexamp-sync
```

### Setting Up PyPI Credentials

1. Create account at https://pypi.org
2. Generate API token at https://pypi.org/manage/account/token/
3. Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-your-api-token-here
```

## Menu Bar App Integration

### Using with rumps (Recommended for macOS)

```python
import rumps
from rekordbox_plexamp_sync import (
    Logger,
    build_plex_track_map,
    build_plex_playlist_map,
    get_playlists,
)
from rekordbox_plexamp_sync.core import sync_playlists
from plexapi.server import PlexServer

class RekordboxSyncApp(rumps.App):
    def __init__(self):
        super().__init__("Rekordbox Sync", icon="🎵")
        self.server_url = "http://localhost:32400"
        self.token = "your-plex-token"
        
    @rumps.clicked("Sync Now")
    def sync_now(self, _):
        try:
            logger = Logger(verbose=False)
            plex = PlexServer(self.server_url, self.token)
            
            rekordbox_playlists = get_playlists()
            track_map = build_plex_track_map(plex, logger)
            playlist_map = build_plex_playlist_map(plex, logger)
            
            result = sync_playlists(
                plex=plex,
                rekordbox_playlists=rekordbox_playlists,
                track_map=track_map,
                playlist_map=playlist_map,
                logger=logger,
            )
            
            created = len(result['created_playlists'])
            updated = len(result['updated_playlists'])
            
            rumps.notification(
                title="Sync Complete",
                subtitle=f"✅ Success",
                message=f"Created: {created}, Updated: {updated}"
            )
        except Exception as e:
            rumps.notification(
                title="Sync Failed",
                subtitle="❌ Error",
                message=str(e)
            )

if __name__ == "__main__":
    RekordboxSyncApp().run()
```

### Using with pystray (Cross-platform)

```python
import pystray
from PIL import Image, ImageDraw
from rekordbox_plexamp_sync import sync_rekordbox_to_plex

def create_image():
    # Create icon
    image = Image.new('RGB', (64, 64), color='black')
    dc = ImageDraw.Draw(image)
    dc.text((10, 10), "RB", fill='white')
    return image

def on_sync(icon, item):
    try:
        result = sync_rekordbox_to_plex(
            server_url="http://localhost:32400",
            token="your-token",
            verbose=False
        )
        icon.notify(f"Synced: {len(result['created_playlists'])} created")
    except Exception as e:
        icon.notify(f"Error: {e}")

icon = pystray.Icon(
    "rekordbox-sync",
    create_image(),
    menu=pystray.Menu(
        pystray.MenuItem("Sync Now", on_sync),
        pystray.MenuItem("Quit", lambda: icon.stop())
    )
)

icon.run()
```

### Building a Standalone App

To create a standalone macOS app with py2app:

```bash
# Install py2app
pip install py2app

# Create setup.py
python setup.py py2app

# Your app will be in dist/YourApp.app
```

Example `setup.py` for py2app:

```python
from setuptools import setup

APP = ['your_menubar_app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['rekordbox_plexamp_sync', 'plexapi', 'rumps'],
    'includes': ['ctypes'],
    'iconfile': 'icon.icns',
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

## Troubleshooting

### Library.so Not Found

If you get `FileNotFoundError: Could not find library.so`:

1. Make sure you've built the Go shared library: `make`
2. The `library.so` file should be in the package directory
3. Or specify the path explicitly: `get_playlists(library_path='/path/to/library.so')`

### Import Errors

If you get import errors after installation:

```bash
# Reinstall in editable mode
pip uninstall rekordbox-plexamp-sync
pip install -e .

# Or rebuild and reinstall
python -m build
pip install --force-reinstall dist/rekordbox_plexamp_sync-0.1.0-py3-none-any.whl
```

### Plex Connection Issues

```python
from plexapi.server import PlexServer

# Test connection
try:
    plex = PlexServer('http://localhost:32400', 'your-token')
    print(f"Connected to: {plex.friendlyName}")
except Exception as e:
    print(f"Connection failed: {e}")
```

### Getting Your Plex Token

1. Open Plex Web App in browser
2. Open browser developer tools (F12)
3. Go to Application/Storage → Local Storage
4. Look for `myPlexAccessToken` or similar

### Verbose Output for Debugging

```python
# Enable verbose mode to see what's happening
logger = Logger(verbose=True)
```

## Additional Resources

- See `examples/menubar_app_example.py` for complete examples
- Original CLI usage: `python app.py <server-url> <token> --verbose`
- Package CLI: `rekordbox-plexamp-sync <server-url> <token> --verbose`

## Version History

- **0.1.0** (Initial Release)
  - Core sync functionality
  - CLI interface
  - Package distribution support
  - Menu bar app integration examples