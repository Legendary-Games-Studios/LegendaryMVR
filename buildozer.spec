[app]

# (str) Title of your application
title = LegendaryMVR

# (str) Package name
package.name = legendarymvr

# (str) Package domain (makes the full package name com.lgs.legendarymvr)
package.domain = com.lgs

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (includes Python files and Web assets)
source.include_exts = py,png,jpg,kv,atlas,html,css,js,json

# (str) Application versioning
version = 0.1.0

# (list) Application requirements
# python3, kivy, and pyjnius are mandatory for our native Android WebView setup
requirements = python3, kivy, pyjnius

# (str) Supported orientations (landscape is essential for VR headsets)
orientation = landscape

# =============================================================================
# Android Specific Configuration
# =============================================================================

# (bool) Indicate if the application should be fullscreen (Hides the status bars)
fullscreen = 1

# (list) Permissions required by the app
# INTERNET is mandatory to pull your HTML games from GitHub
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (bool) Automatically accept the Android SDK license agreement (Fixes AIDL error)
android.accept_sdk_license = True

# (int) Android API to target
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (int) Android NDK version to use
android.ndk = 25b

# (list) Build for modern 64-bit phones
android.archs = arm64-v8a

# =============================================================================
# Buildozer Global Settings
# =============================================================================

[buildozer]

# (int) Log level (2 = debug info, helps find compiler bugs if it errors)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
