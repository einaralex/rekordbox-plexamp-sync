"""
Standalone Menu Bar App Example for rekordbox-plexamp-sync

This is a complete, ready-to-use menu bar application that syncs rekordbox
playlists to Plex/Plexamp. It demonstrates:
- Basic rumps integration
- Event callback handling for real-time updates
- Configuration management
- Error handling
- User notifications

Requirements:
    pip install rekordbox-plexamp-sync rumps

Usage:
    python standalone_menubar_app.py
"""

import rumps
from plexapi.server import PlexServer

from rekordbox_plexamp_sync import (
    Logger,
    build_plex_playlist_map,
    build_plex_track_map,
    get_playlists,
)
from rekordbox_plexamp_sync.core import sync_playlists


class RekordboxSyncApp(rumps.App):
    """Menu bar app for syncing rekordbox playlists to Plex"""

    def __init__(self):
        super().__init__('🎵', quit_button=None)

        # Configuration - TODO: Load from config file or preferences
        self.config = {
            'server_url': 'http://localhost:32400',
            'token': 'your-plex-token-here',  # Get from Plex web app localStorage
        }

        self.current_status = 'Idle'
        self.syncing = False

    def handle_sync_event(self, event_type: str, data: dict):
        """Handle events from the Logger during sync"""

        if event_type == 'building_track_map':
            self.title = '🔄'
            self.current_status = 'Building track map...'

        elif event_type == 'track_map_complete':
            self.current_status = f'Indexed {data["filename_count"]} tracks'

        elif event_type == 'building_playlist_map':
            self.current_status = 'Building playlist map...'

        elif event_type == 'rekordbox_playlists_found':
            self.current_status = f'Found {data["count"]} playlists to sync'
            rumps.notification(
                title='Rekordbox Sync',
                subtitle='Starting sync',
                message=f'Processing {data["count"]} playlists',
            )

        elif event_type == 'processing_playlist':
            self.current_status = f'Syncing: {data["name"]}'

        elif event_type == 'playlist_created':
            # Optionally show notification for each created playlist
            pass

        elif event_type == 'playlist_updated':
            # Show notification with track delta info
            delta = data['added']
            delta_str = f'+{delta}' if delta > 0 else str(delta)
            # Optionally show notification for each updated playlist
            # rumps.notification(
            #     title='Playlist Updated',
            #     subtitle=data['name'],
            #     message=f'{data["old_count"]} → {data["new_count"]} tracks ({delta_str})'
            # )

        elif event_type == 'sync_complete':
            self.title = '✅'
            self.current_status = (
                f'Complete! Processed {data["total_processed"]} playlists'
            )
            self.syncing = False

    @rumps.clicked('Sync Now')
    def sync_now(self, _):
        """Perform sync operation"""
        if self.syncing:
            rumps.alert(
                title='Sync in Progress',
                message='A sync operation is already running. Please wait.',
            )
            return

        self.syncing = True
        self.title = '🔄'
        self.current_status = 'Starting sync...'

        try:
            # Create logger with event callback for real-time updates
            logger = Logger(verbose=False, event_callback=self.handle_sync_event)

            # Connect to Plex
            plex = PlexServer(self.config['server_url'], self.config['token'])

            # Get rekordbox playlists
            rekordbox_playlists = get_playlists()

            # Build maps
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

            # Show summary notification with details
            created = len(result['created_playlists'])
            updated = len(result['updated_playlists'])
            not_found = len(result['not_found_tracks'])

            # Calculate total tracks added/removed across all updates
            total_delta = sum(pl['added'] for pl in result['updated_playlists'])

            message = f'Created: {created}, Updated: {updated}'
            if updated > 0 and total_delta != 0:
                delta_str = f'+{total_delta}' if total_delta > 0 else str(total_delta)
                message += f' ({delta_str} tracks)'
            if not_found > 0:
                message += f'\n⚠️ {not_found} tracks not found'

            rumps.notification(
                title='Rekordbox Sync',
                subtitle='✅ Complete',
                message=message,
            )

            self.title = '✅'

        except FileNotFoundError as e:
            self.title = '❌'
            self.current_status = 'Error: library.so not found'
            self.syncing = False
            rumps.alert(
                title='Sync Failed',
                message="Could not find library.so. Please ensure the Go shared library is built (run 'make').",
            )

        except Exception as e:
            self.title = '❌'
            self.current_status = f'Error: {str(e)}'
            self.syncing = False
            rumps.notification(
                title='Rekordbox Sync',
                subtitle='❌ Failed',
                message=str(e),
            )

    @rumps.clicked('Status')
    def show_status(self, _):
        """Show current status"""
        rumps.alert(
            title='Current Status',
            message=self.current_status,
        )

    @rumps.clicked('Configuration...')
    def show_config(self, _):
        """Show configuration dialog"""
        config_text = (
            f'Server URL: {self.config["server_url"]}\n'
            f'Token: {"*" * 20 if self.config["token"] else "Not set"}\n\n'
            'To update configuration, edit the code or implement a settings dialog.'
        )
        rumps.alert(
            title='Configuration',
            message=config_text,
        )

    @rumps.clicked('About')
    def show_about(self, _):
        """Show about dialog"""
        rumps.alert(
            title='Rekordbox to Plex Sync',
            message=(
                'Version 0.1.0\n\n'
                'Syncs rekordbox playlists to Plex/Plexamp.\n\n'
                'Built with rekordbox-plexamp-sync package.'
            ),
        )

    @rumps.clicked('Quit')
    def quit_app(self, _):
        """Quit the application"""
        if self.syncing:
            response = rumps.alert(
                title='Sync in Progress',
                message='A sync is currently running. Are you sure you want to quit?',
                ok='Quit Anyway',
                cancel='Cancel',
            )
            if response == 0:  # Cancel
                return

        rumps.quit_application()


def main():
    """Main entry point"""
    app = RekordboxSyncApp()
    app.run()


if __name__ == '__main__':
    main()
