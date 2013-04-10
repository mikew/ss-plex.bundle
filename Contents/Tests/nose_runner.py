# Most of this is from Plex's Framework.bundle/bootstrap.py
# Copied with permission

## CONFIGURE THE PYTHON ENVIRONMENT ##

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os, inspect

# Get python path from Plex Media Server installation
# OS X specific currently
PYTHON_DIR    = os.path.expanduser(os.environ['PLEX_FRAMEWORK_PATH'])
FRAMEWORK_DIR = os.path.abspath(os.path.join(PYTHON_DIR, '..'))

# Get the path to our plugin.bundle
bundle_path   = os.path.abspath(inspect.getfile(inspect.currentframe()) + '/../../../')
sys.path.insert(0, PYTHON_DIR)

import subsystem
import config

# Redirect stdout to stderr
sys.stdout = sys.stderr

if sys.platform == "win32":
    os_name = "Windows"
    cpu_name = "i386"
    #TODO - support Windows x64 (Win64)
else:
    uname = os.uname()
    os_name = uname[0]
    cpu_name = uname[4]

mapped_cpu = config.cpu_map[cpu_name]

# Special case for Linux/x64 (really should be special case for OS X...)
if os_name == 'Linux' and cpu_name == 'x86_64':
    mapped_cpu = 'x86_64'

PLATFORM_DIR = os.path.abspath(os.path.join(FRAMEWORK_DIR, '..', '..', "Platforms", config.os_map[os_name], mapped_cpu))
SHARED_DIR = os.path.abspath(os.path.join(FRAMEWORK_DIR, '..', '..', "Platforms", "Shared"))
#TODO: Check for errors

# Append the library paths to sys.path
if sys.platform != "darwin":
    # The binary lib path goes at the end, because binary extensions should be picked up from 
    # the PMS Exts directory first (on non-Mac platforms). In addition, if the environment 
    # variable PLEXBUNDLEDEXTS is set, this indicates a newer server which comes bundled with its 
    # own binaries so we'll skip it competely.
    #
    if 'PLEXBUNDLEDEXTS' not in os.environ:
        sys.path.append(os.path.join(PLATFORM_DIR, "Libraries"))
else:
    sys.path.insert(0, os.path.join(PLATFORM_DIR, "Libraries"))

sys.path.insert(0, os.path.join(SHARED_DIR, "Libraries"))

## LOAD AND CONFIGURE THE FRAMEWORK ##

import Framework

# Whack any .pyc files found in Contents/Libraries
libs_path = os.path.join(bundle_path, 'Contents', 'Libraries')
if os.path.exists(libs_path):
    for root, dirs, files in os.walk(libs_path):
        for f in files:
            if f[-4:] == '.pyc':
                fp = os.path.join(root, f)
                os.unlink(fp)

daemonized = False
# Copy the damonized attribute into config
setattr(config, 'daemonized', daemonized)
setattr(config, 'log_file', bundle_path + '/test.log')
setattr(config, 'services_bundle_path', bundle_path)

# Create a core object for the plug-in bundle
core = Framework.core.FrameworkCore(bundle_path, FRAMEWORK_DIR, config)

# Try to load the plug-in code
if not core.load_code():
    sys.stderr.write('Error loading bundle code.\n')
    sys.exit(2)

if core.init_code:
    core.sandbox.execute(core.init_code)

sys.path.insert(0, core.code_path)

import plex_nose
import spec
import sys

sys.argv.insert(1, '-vv')
sys.argv.insert(1, '-s')
sys.argv.insert(1, '--with-spec')
sys.argv.insert(1, '--spec-color')

plex_nose.core = core
plex_nose.nose.run(addplugins=[spec.Spec()])
os._exit(0)
