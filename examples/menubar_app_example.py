"""
Example: How to use rekordbox-plexamp-sync in a macOS menu bar application.

This example shows how to import and use the core sync functionality
in your menu bar app built with libraries like rumps, pystray, or similar.

Includes examples of how to listen to Logger events for real-time updates.
"""

from plexapi.server import PlexServer

from rekordbox_plexamp_sync import (
    Logger,
    build_plex_playlist_map,
    build_plex_track_map,
    get_playlists,
)
from rekordbox_plexamp_sync.core import print_sync_summary, sync_playlists


def sync_rekordbox_to_plex(server_url: str, token: str, verbose: bool = False) -> dict:
    """
    Sync rekordbox playlists to Plex.

    Args:
        server_url: Plex server URL (e.g., 'http://localhost:32400')
        token: Plex authentication token
        verbose: Enable verbose logging

    Returns:
        Dictionary with sync results containing:
        - created_playlists: List of newly created playlists
        - updated_playlists: List of updated playlists
        - skipped_playlists: List of skipped playlists
        - smart_playlists_skipped: List of smart playlists that were skipped
        - not_found_tracks: List of tracks not found in Plex

    Raises:
        FileNotFoundError: If library.so is not found
        Exception: For any Plex connection or sync errors
    """
    # Initialize logger
    logger = Logger(verbose=verbose)

    # Connect to Plex
    plex = PlexServer(server_url, token)

    # Get rekordbox playlists
    rekordbox_playlists = get_playlists()

    # Build track and playlist maps (these are cached for performance)
    track_map = build_plex_track_map(plex, logger)
    playlist_map = build_plex_playlist_map(plex, logger)

    # Perform the sync
    result = sync_playlists(
        plex=plex,
        rekordbox_playlists=rekordbox_playlists,
        track_map=track_map,
        playlist_map=playlist_map,
        logger=logger,
        export_not_found=True,
        not_found_path='not-found.json',
    )

    # Optionally print summary (or handle it in your UI)
    if verbose:
        print_sync_summary(result, logger)

    return result


# Example 1: Simple sync with minimal output
def example_simple_sync():
    """Simple sync with quiet output - good for menu bar app"""
    try:
        result = sync_rekordbox_to_plex(
            server_url='http://localhost:32400',
            token='your-plex-token-here',
            verbose=False,  # Quiet mode for menu bar
        )

        # Check results
        created_count = len(result['created_playlists'])
        updated_count = len(result['updated_playlists'])

        print(f'✅ Sync complete: {created_count} created, {updated_count} updated')

        return result
    except Exception as e:
        print(f'❌ Sync failed: {e}')
        return None


# Example 2: Sync with verbose output
def example_verbose_sync():
    """Verbose sync - good for debugging or showing in a terminal"""
    try:
        result = sync_rekordbox_to_plex(
            server_url='http://localhost:32400',
            token='your-plex-token-here',
            verbose=True,  # Detailed output
        )
        return result
    except Exception as e:
        print(f'❌ Sync failed: {e}')
        return None


# Example 3: Integration with rumps (macOS menu bar framework)
def example_rumps_integration():
    """
    Example of integrating with a rumps-based menu bar app.
    Install rumps: pip install rumps
    """
    try:
        import rumps
    except ImportError:
        print("This example requires 'rumps'. Install it with: pip install rumps")
        return

    class RekordboxSyncApp(rumps.App):
        def __init__(self):
            super(RekordboxSyncApp, self).__init__(
                'Rekordbox Sync', icon='🎵', quit_button=None
            )
            self.server_url = 'http://localhost:32400'
            self.token = 'your-plex-token-here'

        @rumps.clicked('Sync Now')
        def sync_now(self, _):
            """Handle sync button click"""
            self.title = '🔄'  # Show syncing icon
            rumps.notification(
                title='Rekordbox Sync',
                subtitle='Starting sync...',
                message='Syncing playlists to Plex',
            )

            try:
                result = sync_rekordbox_to_plex(
                    server_url=self.server_url, token=self.token, verbose=False
                )

                # Update menu bar with result
                created = len(result['created_playlists'])
                updated = len(result['updated_playlists'])

                rumps.notification(
                    title='Rekordbox Sync',
                    subtitle='Sync Complete! ✅',
                    message=f'Created: {created}, Updated: {updated}',
                )

                self.title = '✅'  # Show success icon
            except Exception as e:
                rumps.notification(
                    title='Rekordbox Sync',
                    subtitle='Sync Failed ❌',
                    message=str(e),
                )
                self.title = '❌'  # Show error icon

        @rumps.clicked('Quit')
        def quit_app(self, _):
            rumps.quit_application()

    # Run the app
    RekordboxSyncApp().run()


# Example 3b: Integration with rumps using event callbacks
def example_rumps_with_events():
    """
    Example showing how to use Logger event callbacks with rumps.
    This provides real-time updates during the sync process.
    Install rumps: pip install rumps
    """
    try:
        import rumps
    except ImportError:
        print("This example requires 'rumps'. Install it with: pip install rumps")
        return

    class RekordboxSyncApp(rumps.App):
        def __init__(self):
            super(RekordboxSyncApp, self).__init__(
                'Rekordbox Sync', icon='🎵', quit_button=None
            )
            self.server_url = 'http://localhost:32400'
            self.token = 'your-plex-token-here'
            self.current_status = 'Idle'

        def handle_logger_event(self, event_type: str, data: dict):
            """Handle events from the Logger"""
            if event_type == 'building_track_map':
                self.title = '🔄'
                self.current_status = 'Building track map...'
            elif event_type == 'track_map_complete':
                self.current_status = f'Indexed {data["filename_count"]} tracks'
            elif event_type == 'building_playlist_map':
                self.current_status = 'Building playlist map...'
            elif event_type == 'rekordbox_playlists_found':
                self.current_status = f'Found {data["count"]} playlists'
                rumps.notification(
                    title='Rekordbox Sync',
                    subtitle='Starting sync',
                    message=f'Processing {data["count"]} playlists',
                )
            elif event_type == 'processing_playlist':
                self.current_status = f'Syncing: {data["name"]}'
            elif event_type == 'playlist_created':
                rumps.notification(
                    title='Playlist Created',
                    subtitle=data['name'],
                    message='✅ New playlist created',
                )
            elif event_type == 'playlist_updated':
                rumps.notification(
                    title='Playlist Updated',
                    subtitle=data['name'],
                    message='🔄 Playlist updated',
                )
            elif event_type == 'sync_complete':
                self.title = '✅'
                self.current_status = 'Sync complete!'
                rumps.notification(
                    title='Rekordbox Sync',
                    subtitle='Complete! ✅',
                    message=f'Processed {data["total_processed"]} playlists',
                )

        @rumps.clicked('Sync Now')
        def sync_now(self, _):
            """Handle sync button click with event callbacks"""
            self.title = '🔄'
            self.current_status = 'Starting sync...'

            try:
                # Create logger with event callback
                logger = Logger(verbose=False, event_callback=self.handle_logger_event)
                plex = PlexServer(self.server_url, self.token)

                # Get and sync
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

                self.title = '✅'

            except Exception as e:
                self.title = '❌'
                self.current_status = f'Error: {str(e)}'
                rumps.notification(
                    title='Rekordbox Sync',
                    subtitle='Sync Failed ❌',
                    message=str(e),
                )

        @rumps.clicked('Status')
        def show_status(self, _):
            """Show current status"""
            rumps.alert(title='Current Status', message=self.current_status)

        @rumps.clicked('Quit')
        def quit_app(self, _):
            rumps.quit_application()

    # Run the app
    RekordboxSyncApp().run()


# Example 4: Using as a library programmatically
def example_programmatic_usage():
    """
    Example showing how to use individual functions for more control.
    This is useful if you want to build your own UI or notification system.
    """
    from plexapi.server import PlexServer

    try:
        # Step 1: Connect to Plex
        plex = PlexServer('http://localhost:32400', 'your-plex-token-here')
        print(f'Connected to: {plex.friendlyName}')

        # Step 2: Get rekordbox playlists
        logger = Logger(verbose=False)
        rekordbox_playlists = get_playlists()
        print(f'Found {len(rekordbox_playlists)} rekordbox playlists')

        # Step 3: Build maps (do this once and reuse)
        track_map = build_plex_track_map(plex, logger)
        playlist_map = build_plex_playlist_map(plex, logger)

        # Step 4: Sync playlists
        result = sync_playlists(
            plex=plex,
            rekordbox_playlists=rekordbox_playlists,
            track_map=track_map,
            playlist_map=playlist_map,
            logger=logger,
        )

        # Step 5: Handle results in your own way
        for playlist in result['created_playlists']:
            print(f'✨ Created: {playlist["name"]} ({playlist["tracks"]} tracks)')

        for playlist in result['updated_playlists']:
            print(
                f'🔄 Updated: {playlist["name"]} '
                f'({playlist["old_tracks"]} → {playlist["new_tracks"]} tracks)'
            )

        if result['not_found_tracks']:
            print(f'\n⚠️  {len(result["not_found_tracks"])} tracks not found in Plex')

        return result

    except Exception as e:
        print(f'Error: {e}')
        return None


if __name__ == '__main__':
    # Run the simple example
    print('Running simple sync example...\n')
    example_simple_sync()

    # Uncomment to try other examples:
    # example_verbose_sync()
    # example_rumps_integration()
    # example_rumps_with_events()  # NEW: with event callbacks
    # example_programmatic_usage()
