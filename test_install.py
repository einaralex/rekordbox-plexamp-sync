#!/usr/bin/env python3
"""Test script to verify rekordbox-plexamp-sync installation"""

import sys


def test_imports():
    """Test that all modules can be imported"""
    print('Testing imports...')

    try:
        import app

        print('  ✓ app module imports successfully')
    except ImportError as e:
        print(f'  ✗ Failed to import app: {e}')
        return False

    try:
        import logger

        print('  ✓ logger module imports successfully')
    except ImportError as e:
        print(f'  ✗ Failed to import logger: {e}')
        return False

    try:
        from __init__ import get_rekordbox_playlists, sync_playlists

        print('  ✓ Library functions import successfully')
    except ImportError as e:
        print(f'  ✗ Failed to import library functions: {e}')
        return False

    return True


def test_library_exists():
    """Test that the Go library exists"""
    import os

    print('\nTesting Go library...')

    if os.path.exists('library.so'):
        print('  ✓ library.so found')
        return True
    else:
        print("  ✗ library.so not found - run 'make' to build it")
        return False


def test_cli_callable():
    """Test that the CLI main function is callable"""
    print('\nTesting CLI interface...')

    try:
        import app

        if hasattr(app, 'main'):
            print('  ✓ app.main() function exists')
            return True
        else:
            print('  ✗ app.main() function not found')
            return False
    except Exception as e:
        print(f'  ✗ Error checking app.main(): {e}')
        return False


def test_dependencies():
    """Test that required dependencies are installed"""
    print('\nTesting dependencies...')

    dependencies = [
        'plexapi',
        'tqdm',
        'requests',
    ]

    all_ok = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f'  ✓ {dep} installed')
        except ImportError:
            print(f'  ✗ {dep} not installed')
            all_ok = False

    return all_ok


def main():
    """Run all tests"""
    print('=' * 60)
    print('Rekordbox-Plexamp-Sync Installation Test')
    print('=' * 60)

    results = []

    results.append(('Imports', test_imports()))
    results.append(('Go Library', test_library_exists()))
    results.append(('CLI Interface', test_cli_callable()))
    results.append(('Dependencies', test_dependencies()))

    print('\n' + '=' * 60)
    print('Test Results:')
    print('=' * 60)

    all_passed = True
    for test_name, passed in results:
        status = '✓ PASS' if passed else '✗ FAIL'
        print(f'  {test_name}: {status}')
        if not passed:
            all_passed = False

    print('=' * 60)

    if all_passed:
        print('\n✓ All tests passed! Installation is ready.')
        print('\nYou can now:')
        print('  • Use as CLI: python app.py <url> <token>')
        print(
            '  • Import as library: from rekordbox_plexamp_sync import sync_playlists'
        )
        return 0
    else:
        print('\n✗ Some tests failed. Please check the errors above.')
        if not results[1][1]:  # Go library test failed
            print('\nTo build the Go library, run: make')
        if not results[3][1]:  # Dependencies test failed
            print('\nTo install dependencies, run: pip install -r requirements.txt')
        return 1


if __name__ == '__main__':
    sys.exit(main())
