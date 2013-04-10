#!/bin/sh

export PLEXLOCALAPPDATA="/var/lib/plexmediaserver/Library/Application Support"
#export PLEX_MEDIA_SERVER_APPLICATION_SUPPORT_DIR="/var/lib/plexmediaserver/Library/Application Support"
export PLEX_MEDIA_SERVER_APPLICATION_SUPPORT_DIR="$HOME/.plex-nose"
export PYTHONHOME="/usr/lib/plexmediaserver/Resources/Python"
export PLEX_MEDIA_SERVER_HOME="/usr/lib/plexmediaserver"
export PLEX_MEDIA_SERVER_MAX_STACK_SIZE="3000"
export PLEX_MEDIA_SERVER_TMPDIR="/tmp"
export LD_LIBRARY_PATH="/usr/lib/plexmediaserver"
export PLEX_MEDIA_SERVER_MAX_PLUGIN_PROCS="6"
export PLEX_FRAMEWORK_PATH="/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-ins/Framework.bundle/Contents/Resources/Versions/2/Python"

test_file="$PWD/$1"
/usr/lib/plexmediaserver/Resources/Python/bin/python "Contents/Tests/nose_runner.py" "$test_file"
