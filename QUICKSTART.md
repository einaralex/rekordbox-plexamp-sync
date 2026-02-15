# Quick Start Guide for Menu Bar App Integration

This guide gets you up and running with `rekordbox-plexamp-sync` in your macOS menu bar app in 5 minutes.

## 1. Install the Package

```bash
# Install from the built wheel
pip install dist/rekordbox_plexamp_sync-0.1.0-py3-none-any.whl

# Or in development mode
pip install -e .
```

## 2. Make Sure the Go Library is Built

```bash
make
```

This creates `library.so` which is needed to read the rekordbox database.

## 3. Basic Integration

Here's the simplest way to use it in your menu bar app:

```python
from plexapi.server import PlexServer
from rekordbox_plexamp_sync import (
    Logger,
    build_plex_track_map,
    build_plex_playlist_map,
    get_playlists,
)
from rekordbox_plexamp_sync.core import sync_playlists

def sync_now(server_url: str, token: str) -> dict:
    """Sync rekordbox to Plex - returns results dict"""
    # Create logger (verbose=False for quiet operation)
    logger = Logger(verbose=False)
    
    # Connect to Plex
    plex = PlexServer(server_url, token)
    
    # Get rekordbox playlists
    rekordbox_playlists = get_playlists()
    
    # Build maps (do this once, cache if possible)
    track_map = build_plex_track_map(plex, logger)
    playlist_map = build_plex_playlist_map(plex, logger)
    
    # Perform sync
    result = sync_playlists(
        plex=plex,
        rekordbox_playlists=rekordbox_playlists,
        track_map=track_map,
        playlist_map=playlist_map,
        logger=logger,
    )
    
    return result

# Use it
result = sync_now('http://localhost:32400', 'your-plex-token')
print(f"Created {len(result['created_playlists'])} playlists")
print(f"Updated {len(result['updated_playlists'])} playlists")
```

## 3b. With Event Callbacks (Real-time Updates)

```python
def event_handler(event_type: str, data: dict):
    """Handle events from the sync process"""
    if event_type == 'building_track_map':
        print("🔄 Building track map...")
    elif event_type == 'rekordbox_playlists_found':
        print(f"📋 Found {data['count']} playlists to sync")
    elif event_type == 'processing_playlist':
        print(f"⚙️  Processing: {data['name']}")
    elif event_type == 'playlist_created':
        print(f"✅ Created: {data['name']}")
    elif event_type == 'playlist_updated':
        print(f"🔄 Updated: {data['name']}")
    elif event_type == 'sync_complete':
        print(f"🎉 Complete! Processed {data['total_processed']} playlists")

def sync_with_events(server_url: str, token: str) -> dict:
    """Sync with real-time event notifications"""
    # Create logger with event callback
    logger = Logger(verbose=False, event_callback=event_handler)
    
    plex = PlexServer(server_url, token)
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
    
    return result
```

## 4. Result Structure

The `sync_playlists()` function returns a dictionary with:

```python
{
    'created_playlists': [
        {'name': 'My Playlist', 'tracks': 42}
    ],
    'updated_playlists': [
        {'name': 'Another Playlist', 'old_tracks': 40, 'new_tracks': 42, 'added': 2}
    ],
    'skipped_playlists': [...],
    'smart_playlists_skipped': [...],
    'not_found_tracks': [...]
}
```

## 5. Menu Bar App Example (rumps)

```python
import rumps
from plexapi.server import PlexServer
from rekordbox_plexamp_sync import (
    Logger,
    build_plex_track_map,
    build_plex_playlist_map,
    get_playlists,
)
from rekordbox_plexamp_sync.core import sync_playlists

class RekordboxSyncApp(rumps.App):
    def __init__(self):
        super().__init__("🎵", quit_button=None)
        self.server_url = "http://localhost:32400"
        self.token = "your-plex-token-here"
    
    def handle_event(self, event_type: str, data: dict):
        """Handle Logger events for real-time updates"""
        if event_type == 'building_track_map':
            self.title = "🔄"
        elif event_type == 'rekordbox_playlists_found':
            rumps.notification(
                title="Starting Sync",
                message=f"Processing {data['count']} playlists"
            )
        elif event_type == 'playlist_created':
            rumps.notification(
                title="Created",
                message=data['name']
            )
        elif event_type == 'playlist_updated':
            rumps.notification(
                title="Updated", 
                message=data['name']
            )
        elif event_type == 'sync_complete':
            self.title = "✅"
            rumps.notification(
                title="Sync Complete ✅",
                message=f"Processed {data['total_processed']} playlists"
            )
        
    @rumps.clicked("Sync Now")
    def sync_now(self, _):
        self.title = "🔄"  # Show syncing
        
        try:
            # Create logger with event callback
            logger = Logger(verbose=False, event_callback=self.handle_event)
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
            
            self.title = "✅"
            
        except Exception as e:
            rumps.notification(
                title="Sync Failed ❌",
                message=str(e)
            )
            self.title = "❌"
    
    @rumps.clicked("Quit")
    def quit_app(self, _):
        rumps.quit_application()

if __name__ == "__main__":
    RekordboxSyncApp().run()
```

## 6. Install rumps

If you want to use the menu bar example above:

```bash
pip install rumps
```

## 7. Run Your App

```bash
python your_menubar_app.py
```

## Getting Your Plex Token

1. Open Plex Web in browser
2. Press F12 (Developer Tools)
3. Go to Application → Local Storage
4. Find `myPlexAccessToken`

## Troubleshooting

### "Could not find library.so"

```bash
# Make sure you built the Go library
make

# Check it exists
ls -la rekordbox_plexamp_sync/library.so
```

### Import errors

```bash
# Reinstall the package
pip uninstall rekordbox-plexamp-sync
pip install -e .
```

### Want to see what's happening?

```python
# Enable verbose logging
logger = Logger(verbose=True)
```

## Next Steps

- See `examples/menubar_app_example.py` for more complete examples
- Read `PACKAGING.md` for detailed documentation
- Check out the CLI: `rekordbox-plexamp-sync --help`

## What You Get

✅ All your rekordbox playlists synced to Plex  
✅ Automatic playlist updates when tracks change  
✅ Smart playlist detection and skipping  
✅ Detailed sync reports  
✅ Fast performance with pre-built track maps  

## Key Functions

| Function | Purpose |
|----------|---------|
| `get_playlists()` | Get all playlists from rekordbox |
| `build_plex_track_map()` | Build searchable map of Plex tracks |
| `build_plex_playlist_map()` | Build map of existing Plex playlists |
| `sync_playlists()` | Perform the actual sync |
| `Logger(verbose=bool, event_callback=func)` | Control output verbosity and event callbacks |

## Event Types

When using `event_callback`, these events are emitted:

| Event Type | Data | When |
|------------|------|------|
| `building_track_map` | `{'status': 'started'}` | Track map building starts |
| `track_map_complete` | `{'filename_count': int, 'title_count': int}` | Track map complete |
| `building_playlist_map` | `{'status': 'started'}` | Playlist map building starts |
| `playlist_map_complete` | `{'count': int}` | Playlist map complete |
| `rekordbox_playlists_found` | `{'count': int}` | Found playlists to sync |
| `processing_playlist` | `{'name': str, 'status': 'started'}` | Processing a playlist |
| `playlist_created` | `{'name': str, 'status': 'success'}` | Playlist created |
| `playlist_updated` | `{'name': str, 'status': 'success'}` | Playlist updated |
| `playlist_updating` | `{'name': str, 'old_count': int, 'new_count': int}` | Updating playlist |
| `playlist_up_to_date` | `{'name': str, 'track_count': int}` | Playlist already synced |
| `sync_complete` | `{'total_processed': int}` | Sync finished |

That's it! You're ready to integrate rekordbox-plexamp-sync into your menu bar app. 🎉