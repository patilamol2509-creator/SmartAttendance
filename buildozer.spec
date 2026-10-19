[app]
title = Smart Attendance
package.name = smartattendance
package.domain = org.collegedemo
source.dir = .
source.include_exts = py,kv,png,jpg
version = 1.0
requirements = python3,kivy==2.3.1,kivy_garden.zbarcam
orientation = portrait
fullscreen = 0
android.permissions = CAMERA
android.api = 35
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
