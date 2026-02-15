"""Rekordbox to Plexamp sync - minimal wrapper for library usage"""

import os
import sys
from typing import Any, Callable, Dict, Optional

__version__ = '1.0.0'


def sync_playlists(
    server_url: str,
    token: str,
    verbose: bool = False,
    output_callback: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """
    Sync Rekordbox playlists to Plex

    Args:
        server_url: Plex server URL (e.g., 'http://localhost:32400')
        token: Plex authentication token
        verbose: Enable verbose logging
        output_callback: Optional callback to capture print output

    Returns:
        Dictionary with results:
        {
            'success': bool,
            'not_found': int,
            'error': str (if success=False)
        }
    """
    # Capture the original stdout if callback provided
    if output_callback:
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        try:
            with redirect_stdout(f):
                result = _run_sync(server_url, token, verbose)
            output_callback(f.getvalue())
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    else:
        return _run_sync(server_url, token, verbose)


def _run_sync(server_url: str, token: str, verbose: bool) -> Dict[str, Any]:
    """Internal function that runs the sync by calling app.main()"""
    # Temporarily modify sys.argv to simulate CLI
    original_argv = sys.argv.copy()

    try:
        sys.argv = ['app.py', server_url, token]
        if verbose:
            sys.argv.append('--verbose')

        # Import and run the main app logic
        from . import app

        app.main()

        # Parse results from not-found.json if it exists
        result = {'success': True, 'not_found': 0}

        # Check if not-found.json was created
        if os.path.exists('not-found.json'):
            import json

            with open('not-found.json', 'r') as f:
                not_found = json.load(f)
                result['not_found'] = len(not_found)

        sys.argv = original_argv
        return result

    except Exception as e:
        sys.argv = original_argv
        return {'success': False, 'error': str(e)}


def get_rekordbox_playlists():
    """
    Get all playlists from Rekordbox database

    Returns:
        List of playlist objects with metadata and tracks
    """
    from . import app

    return app.get_playlists()


__all__ = ['sync_playlists', 'get_rekordbox_playlists']
