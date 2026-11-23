--- setup/commands.py.orig	2026-11-21 06:05:05 UTC
+++ setup/commands.py
@@ -36,7 +36,6 @@
     'manual',
     'mathjax',
     'osx',
-    'piper_voices',
     'pot',
     'publish',
     'publish_betas',
@@ -101,10 +100,6 @@
 
 hyphenation = Hyphenation()
 
-from setup.piper import PiperVoices
-
-piper_voices = PiperVoices()
-
 from setup.kokoro import KokoroVoices
 
 kokoro_voices = KokoroVoices()
