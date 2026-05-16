[app]

title = LegendaryMVR

package.name = legendarymvr
package.domain = com.lgs.legendarymvr

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy

entrypoint = LegendaryMVR.py

# ----------------------------
# ANDROID SETTINGS (STABLE)
# ----------------------------

android.api = 33
android.minapi = 21
android.ndk = 25b

android.sdk = 33.0.2
android.build_tools_version = 33.0.2

android.accept_sdk_license = True

android.archs = arm64-v8a, armeabi-v7a

# ----------------------------
# PERMISSIONS (WEB BROWSER FIX)
# ----------------------------

android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE
