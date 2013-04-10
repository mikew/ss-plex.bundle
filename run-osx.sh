#!/bin/sh

framework_resources="$HOME/Library/Application Support/Plex Media Server/Plug-ins/Framework.bundle/Contents/Resources"

export DYLD_LIBRARY_PATH="${framework_resources}/Platforms/MacOSX/i386/Frameworks/:${framework_resources}/Versions/2/Platforms/MacOSX/i386/Frameworks/:${framework_resources}/Versions/2/Frameworks/"

export PLEX_FRAMEWORK_PATH="${framework_resources}/Versions/2/Python"

test_file="$PWD/$1"
python2.5 "Contents/Tests/nose_runner.py" "$test_file"
