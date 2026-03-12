[app]
title = Dario Electricista
package.name = darioelectricista
package.domain = ar.dario.electricista
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,CAMERA,INTERNET
android.api = 33
android.accept_sdk_license = True
android.build_tools_version = 34.0.0
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
