[app]

# (str) Title of your application
title = Fool P2P

# (str) Package name
package.name = foolp2p

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source directory
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application version
version = 0.1

# (list) Application requirements
# Ensure 'kivy' is included
requirements = python3,kivy,aiortc,python-socketio[client]==5.8.0,aioice

# (str) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation
orientation = portrait

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# (str) Android API to use
#android.api = 31

# (str) Android SDK directory (if undefined, it will be automatically downloaded)
#android.sdk_path =

# (str) Android NDK directory (if undefined, it will be automatically downloaded)
#android.ndk_path =

# (str) Android NDK API to use (optional)
#android.ndk_api = 21

# (bool) If True, Kivy will be included by default
#kivy.requirements = True

# (str) Android entry point (default is org.kivy.android.PythonActivity)
#android.entrypoint = org.kivy.android.PythonActivity

#
# Default configuration for debug mode
#
[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) The default command to run (can be overridden by command line argument)
#default_command = android debug

# (list) Global exclude patterns
#global_exclude_patterns = .git,*.pyc,__pycache__,.DS_Store

# (str) The directory for build files
#build_dir = .buildozer

# (str) The directory for distribution files
#bin_dir = bin

# (str) The directory for app-specific files (e.g., local recipes)
#app_dir = app

# (str) The default command to run if nothing is specified
#default_command = android debug
