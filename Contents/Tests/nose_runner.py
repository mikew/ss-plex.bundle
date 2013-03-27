# Most of this is from Plex's Framework.bundle/bootstrap.py
# Copied with permission

## CONFIGURE THE PYTHON ENVIRONMENT ##

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os, inspect

# Get python path from Plex Media Server installation
# OS X specific currently
PYTHON_DIR    = os.path.expanduser('~/Library/Application Support/Plex Media Server/Plug-ins/Framework.bundle/Contents/Resources/Versions/2/Python')
FRAMEWORK_DIR = os.path.abspath(os.path.join(PYTHON_DIR, '..'))

# Get the path to our plugin.bundle
bundle_path   = os.path.abspath(inspect.getfile(inspect.currentframe()) + '/../../../')
sys.path.insert(0, PYTHON_DIR)

import subsystem
import os
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
import Framework.constants as const
#from optparse import OptionParser

#parser = OptionParser()
#parser.add_option("-i", "--interface", dest="interface", default=config.default_interface)
#parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True)
#parser.add_option("-p", "--socket-interface-port", dest="socket_interface_port", default=config.socket_interface_port)
#parser.add_option("-s", "--server-version", dest="server_version")
#parser.add_option("-d", "--daemon", dest="daemon_command")
#parser.add_option("-P", "--pid-file", dest="pid_file")
#parser.add_option("-l", "--log-file", dest="log_file")
#parser.add_option("-c", "--config-file", dest="config_file")
#(options, args) = parser.parse_args()

#bundle_path = args[0]

#del parser
#del OptionParser

class BootstrapOptions:
    def __init__(self):
        self.interface      = 'socket'
        self.verbose        = True
        self.server_version = None
        self.daemon_command = None
        self.pid_file       = None
        self.log_file       = None
        self.config_file    = None
        self.socket_interface_port = config.socket_interface_port

options = BootstrapOptions()

# Whack any .pyc files found in Contents/Libraries
libs_path = os.path.join(bundle_path, 'Contents', 'Libraries')
if os.path.exists(libs_path):
    for root, dirs, files in os.walk(libs_path):
        for f in files:
            if f[-4:] == '.pyc':
                fp = os.path.join(root, f)
                os.unlink(fp)

# Select the interface class to use
if options.interface == const.interface.pipe:
    interface_class = Framework.interfaces.PipeInterface
elif options.interface == const.interface.socket:
    interface_class = Framework.interfaces.SocketInterface
    if int(options.socket_interface_port) != config.socket_interface_port:
        config.socket_interface_port = int(options.socket_interface_port)
else:
    #TODO: Error info - no matching interface found
    sys.stderr.write('No matching interface found.\n')
    sys.exit(1)

#if options.server_version != None:
    #config.server_version = options.server_version

# Configure the log_dir, if one was given
#if options.log_file:
    #config.log_file = os.path.abspath(options.log_file)

# Configure the pid file, if one was given
#if options.pid_file:
    #config.pid_file = os.path.abspath(options.pid_file)

# Load the config file if one was provided
#if options.config_file:
    #import simplejson
    #f = open(options.config_file, 'r')
    #json_config = simplejson.load(f)
    #f.close()
    #for key in json_config:
        #setattr(config, key, json_config[key])

daemonized = False
# Copy the damonized attribute into config
setattr(config, 'daemonized', daemonized)

# Create a core object for the plug-in bundle
core = Framework.core.FrameworkCore(bundle_path, FRAMEWORK_DIR, config)

# Try to load the plug-in code
if not core.load_code():
    sys.stderr.write('Error loading bundle code.\n')
    sys.exit(2)

# Create an instance of the selected interface
#interface = interface_class(core)

# Try to start the core
#if not core.start():
    #sys.stderr.write('Error starting framework core.\n')
    #sys.exit(3)

if core.init_code:
    core.sandbox.execute(core.init_code)

# Start listening on the interface
#interface.listen(daemonized)

sys.path.insert(0, core.code_path)

import plex_nose
plex_nose.core = core

#from nose.plugins import Plugin

#class PlexSandbox(Plugin):
    #name = 'plex_sandbox'
    #score = 10000

    #def prepareTestRunner(self, runner):
        #asdfasdfasdf
        #raise Exception(runner)
        #return PlexSandboxRunner(runner.stream)

import sys
import nose
sys.argv.insert(1, '-vv')
sys.argv.insert(1, '-s')
nose.main()

#def nose_runner():
    #import sys
    #import nose

    #sys.argv.insert(1, '-vv')
    #sys.argv.insert(1, '-s')

    #plex_nose.bridge(
        #L = L,
        #F = F,
        #JSON = JSON,
        #XML = XML,
        #HTTP = HTTP,
        #Dict = Dict,
        #Prefs = Prefs
    #)

    #nose.main()

#core.sandbox.execute(nose_runner.func_code)
