# rekordbox-plexamp-sync

Available at https://pypi.org/project/rekordbox-plexamp-sync/0.1.0/

Sync rekordbox playlists to Plexamp/Plex - available as both a Python package and CLI tool.

<p float="left">
  <img src="./rekordbox.png" width="350" />
  <img src="./plexamp.png" width="350" />
</p>

## Features

- 🎵 Sync all rekordbox playlists to Plex/Plexamp
- 🚀 Fast track matching using pre-built maps
- 📦 Available as a Python package for integration into other apps
- 💻 Command-line interface for manual syncing
- 🔄 Smart playlist detection and skipping
- 📊 Detailed sync reports with track-level information

## How it works

This tool extracts all playlists from the rekordbox database, then interacts with the Plex Media Server API to create or update playlists. 

**Note:** This will only work if your rekordbox library is indexed by Plex. Make sure you deactivate all content matchers for Albums so that Plex does not match and rename tracks. This messes with the track matching to rekordbox - the titles need to be identical for better results.

## Installation

### As a Package (for integration into other apps)

```bash
# Install from local build
pip install dist/rekordbox_plexamp_sync-0.1.0-py3-none-any.whl

# Or install in development mode
pip install -e .

# Or from PyPI (after publishing)
pip install rekordbox-plexamp-sync
```

### For CLI Usage

```bash
# Clone the repository
git clone <your-repo-url>
cd rekordbox-plexamp-sync

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the package
pip install -e .

# Build the Go shared library
make
```

## Usage

### As a CLI Tool

```bash
# Basic usage
rekordbox-plexamp-sync http://localhost:32400 your-plex-token

# With verbose output
rekordbox-plexamp-sync http://localhost:32400 your-plex-token --verbose

# Get help
rekordbox-plexamp-sync --help
```

**Legacy CLI (still works):**
```bash
python app.py http://localhost:32400 your-plex-token --verbose
```

### As a Python Package

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
logger = Logger(verbose=False)
plex = PlexServer('http://localhost:32400', 'your-token')

# Get rekordbox playlists
rekordbox_playlists = get_playlists()

# Build maps (cache these for performance)
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

### In a macOS Menu Bar App

See `examples/menubar_app_example.py` for complete examples using rumps, pystray, and other frameworks.

```python
import rumps
from rekordbox_plexamp_sync import sync_rekordbox_to_plex

class RekordboxSyncApp(rumps.App):
    @rumps.clicked("Sync Now")
    def sync_now(self, _):
        result = sync_rekordbox_to_plex(
            server_url="http://localhost:32400",
            token="your-token",
            verbose=False
        )
        rumps.notification(
            title="Sync Complete",
            message=f"Created: {len(result['created_playlists'])}"
        )

RekordboxSyncApp("Rekordbox Sync").run()
```

## Usage (windows)
I don't have a windows machine to try this on, but build the shared library with Golang.

Edit `main.go` and change the rekordbox pathes. Check the [go-rekordbox README](https://github.com/dvcrn/go-rekordbox#usage) about where to find these pathes:

```go
	optionsFilePath := filepath.Join(homeDir, "/Library/Application Support/Pioneer/rekordboxAgent/storage/", "options.json")

	// Files and paths
	asarPath := "/Applications/rekordbox 6/rekordbox.app/Contents/MacOS/rekordboxAgent.app/Contents/Resources/app.asar"
```

Then build the shared lib and generate a dll

```
go build -buildmode=c-shared -o library.dll main.go
```

Update `app.py` `get_playlists()` to load the new dll instead:

```go
library = ctypes.cdll.LoadLibrary('./library.dll')
```

Then, follow steps from "Usage (mac)"

## Limitations and todos
- Intelligent Playlists aren't supported yet, this needs some extra work
- Matching happens against filename and then title as backup, this can still be improved

## Getting Your Plex Token

1. Open Plex Web App in your browser
2. Open browser developer tools (F12)
3. Go to Application/Storage → Local Storage
4. Look for `myPlexAccessToken`

Alternatively, you can find it by following [Plex's official guide](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).

## Building the Package

```bash
# Install build tools
pip install build twine

# Build the Go shared library
make

# Build the Python package
python -m build

# Output will be in dist/:
# - rekordbox_plexamp_sync-0.1.0-py3-none-any.whl (installable package)
# - rekordbox_plexamp_sync-0.1.0.tar.gz (source distribution)
```

For detailed packaging instructions, see [PACKAGING.md](PACKAGING.md).

## Documentation

- **[PACKAGING.md](PACKAGING.md)** - Complete guide for packaging and distribution
- **[examples/menubar_app_example.py](examples/menubar_app_example.py)** - Integration examples for menu bar apps

## Requirements

- Python 3.8+
- macOS (for the Go shared library)
- Plex Media Server with music library
- rekordbox 6

## Limitations and TODOs

- Smart/Intelligent Playlists aren't supported yet (requires extra work)
- Matching happens against filename first, then title as backup (can be improved)
- Currently macOS only (Windows support needs testing and binary compilation)

## Acknowledgements

This tool is powered by:
- [go-rekordbox](https://github.com/dvcrn/go-rekordbox) - SDK to interact with the rekordbox database
- [python-plexapi](https://github.com/pkkid/python-plexapi) - Python bindings for the Plex API
