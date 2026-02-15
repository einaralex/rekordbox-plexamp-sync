# 1. Activate your virtual environment
source venv/bin/activate

# 2. Install build tools
pip install build twine

# 3. Build the Go shared library (if not already done)
make

# 4. Build the Python package
python -m build

# This will create two files in the dist/ directory:
# - rekordbox_plexamp_sync-0.1.0-py3-none-any.whl (wheel)
# - rekordbox_plexamp_sync-0.1.0.tar.gz (source distribution)

# 5. Install the local build (optional)
pip install dist/rekordbox_plexamp_sync-0.1.0-py3-none-any.whl
# OR install in editable mode
pip install -e .
# OR PUBLISH TO PYPI
python -m twine upload dist/*
