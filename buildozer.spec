[app]
title = RubiksDetector
package.name = rubiksdetector
package.domain = org.rubiksdetector
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,numpy,opencv==4.5.2,opencv_extras==4.5.2,matplotlib, kociemba, pydot, python-statemachine
orientation = portrait
fullscreen = 0
android.permissions= CAMERA
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
[buildozer]
log_level = 2
warn_on_root = 1
