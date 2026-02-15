# rekordbox-plexamp-sync

Syncs rekordbox playlists to Plex/Plexamp. Works as both a CLI tool and importable Python library.

<p float="left">
  <img src="./rekordbox.png" width="350" />
  <img src="./plexamp.png" width="350" />
</p>

## How It Works

Extracts playlists from the rekordbox database using a Go library, then creates matching playlists in Plex via the Plex API. Track matching is done by filename first, then title as fallback.

**Important:** Your rekordbox library must be indexed by Plex. Disable all content matchers for Albums to prevent Plex from renaming tracks - titles must match exactly for best results.

## Quick Start

### CLI Usage

```bash
make  # Builds the Go library
pip install -r requirements.txt

# Run sync
python app.py 'http://localhost:32400' 'YOUR_PLEX_TOKEN' --verbose
```

Get your Plex token from the browsers localStorage `myPlexAccessToken when connected to your server.

### Library Usage (for GUI apps)

```bash
pip install git+https://github.com/dvcrn/rekordbox-plexamp-sync.git
```

```python
from rekordbox_plexamp_sync import sync_playlists

result = sync_playlists(
    server_url='http://localhost:32400',
    token='YOUR_PLEX_TOKEN',
    verbose=True,
    output_callback=lambda text: print(text)  # Optional: capture output
)

if result['success']:
    print(f"Synced! {result['not_found']} tracks not found.")
else:
    print(f"Error: {result['error']}")
```

## Installation as Package

```bash
# Development mode
pip install -e .

# Use as CLI command
rekordbox-plex-sync 'http://localhost:32400' 'token' --verbose
```

## Project Structure

```
.
├── app.py              # Main CLI logic
├── __init__.py         # Library wrapper for GUI integration
├── main.go             # Go library for rekordbox DB access
├── library.so          # Compiled Go library (created by make)
├── setup.py            # Package configuration
├── MANIFEST.in         # Distribution file inclusion rules
└── test_install.py     # Installation verification
```

## Key Files

- **`app.py`**: Core sync logic. Contains `main()` function for CLI and `get_playlists()` for DB access
- **`__init__.py`**: Library wrapper exposing `sync_playlists()` and `get_rekordbox_playlists()`
- **`main.go`**: Go shared library wrapping [go-rekordbox](https://github.com/dvcrn/go-rekordbox) for Python
- **`setup.py`**: Defines package metadata, dependencies, and CLI entry point

## Windows Support

> ⚠️ This has not been tested on Windows.

Windows requires building the Go library as a DLL:

1. Set rekordbox path using environment variable (see [go-rekordbox docs](https://github.com/dvcrn/go-rekordbox#usage) for Windows paths):
   ```bash
   set REKORDBOX_OPTIONS_PATH=C:\path\to\your\options.json
   ```

2. Build DLL:
   ```bash
   go build -buildmode=c-shared -o library.dll main.go
   ```

3. Update `app.py` `get_playlists()`:
   ```python
   library = ctypes.cdll.LoadLibrary('./library.dll')
   ```

## API Reference

### `sync_playlists(server_url, token, verbose=False, output_callback=None)`

Syncs all rekordbox playlists to Plex.

**Parameters:**
- `server_url` (str): Plex server URL (e.g., 'http://localhost:32400')
- `token` (str): Plex authentication token
- `verbose` (bool): Enable verbose logging
- `output_callback` (callable): Function to receive output (for GUI integration)

**Returns:**
```python
{
    'success': bool,
    'not_found': int,  # Number of tracks not found
    'error': str       # Error message if success=False
}
```

### `get_rekordbox_playlists()`

Returns list of rekordbox playlists without syncing.

**Returns:** List of playlist dictionaries with track information.

## Maintenance Notes

### Dependencies
- Python 3.8+
- Go 1.16+ (for building)
- [go-rekordbox](https://github.com/dvcrn/go-rekordbox) - Rekordbox DB SDK
- [python-plexapi](https://github.com/pkkid/python-plexapi) - Plex API wrapper

### Limitations
- Intelligent Playlists not supported (requires additional work)
- Matching is filename-first, title-fallback (can be improved)
- rekordbox database paths are hardcoded in `main.go` (macOS paths)

### Testing

```bash
# Verify installation
python test_install.py

# Test library import
python -c "from rekordbox_plexamp_sync import sync_playlists; print('OK')"

# Rebuild Go library
make clean
make
```

## Architecture

1. **Go Library** (`main.go`) → Compiled to `library.so`
   - Reads rekordbox database via go-rekordbox SDK
   - Exports `GetPlaylistsJSON()` function to Python

2. **Python Core** (`app.py`)
   - Loads Go library via ctypes
   - Matches rekordbox tracks to Plex tracks
   - Creates/updates Plex playlists via python-plexapi

3. **Library Wrapper** (`__init__.py`)
   - Wraps `app.py` for library usage
   - Handles stdout redirection for GUI integration
   - Provides clean API with callbacks

## Troubleshooting

**Go library not found:**
```bash
make
```

**Import errors after installation:**
```bash
pip install -e .
```

**Tracks not matching:**
- Ensure Plex hasn't renamed your tracks
- Disable content matchers for Albums in Plex
- Check that filenames match between rekordbox and Plex

**Custom rekordbox paths:**
Set the `REKORDBOX_OPTIONS_PATH` environment variable to override the default macOS path:
```bash
export REKORDBOX_OPTIONS_PATH="/path/to/your/options.json"
python app.py 'http://localhost:32400' 'token'
```

Default path: `~/Library/Application Support/Pioneer/rekordboxAgent/storage/options.json`


## Acknowledgements

Powered by:
- [go-rekordbox](https://github.com/dvcrn/go-rekordbox) - Rekordbox SDK
- [python-plexapi](https://github.com/pkkid/python-plexapi) - Plex API client
