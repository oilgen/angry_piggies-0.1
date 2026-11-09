[app]
title = Angry Piggies
package.name = angrypiggies
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,sql,db,json,ttf,ogg,wav
version = 1.0
requirements = python3,kivy
orientation = landscape
fullscreen = 1
android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.private_storage = True
android.numeric_version = 1
android.enable_androidx = True
android.permissions = INTERNET
android.copy_libs = 1
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
