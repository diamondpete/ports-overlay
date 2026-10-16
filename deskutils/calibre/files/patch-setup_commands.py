--- setup/commands.py.orig	2026-10-16 11:23:37 UTC
+++ setup/commands.py
@@ -35,7 +35,6 @@
     'manual',
     'mathjax',
     'osx',
-    'piper_voices',
     'pot',
     'publish',
     'publish_betas',
@@ -100,10 +99,6 @@
 
 hyphenation = Hyphenation()
 
-from setup.piper import PiperVoices
-
-piper_voices = PiperVoices()
-
 from setup.kokoro import KokoroVoices
 
 kokoro_voices = KokoroVoices()
