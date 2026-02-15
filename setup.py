import os

from setuptools import setup

# Read README for long description
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

# Read requirements
with open('requirements.txt', 'r', encoding='utf-8') as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith('#')
    ]

setup(
    name='rekordbox-plexamp-sync',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Sync Rekordbox playlists to Plex/Plexamp',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/rekordbox-plexamp-sync',
    py_modules=['app', 'logger', '__init__'],
    include_package_data=True,
    package_data={
        '': ['library.so', '*.dylib', '*.png', '*.h'],
    },
    install_requires=requirements,
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
    ],
    entry_points={
        'console_scripts': [
            'rekordbox-plex-sync=app:main',
        ],
    },
)
