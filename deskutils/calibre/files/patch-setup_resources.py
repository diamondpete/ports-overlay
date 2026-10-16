--- setup/resources.py.orig	2026-10-16 20:23:57 UTC
+++ setup/resources.py
@@ -51,7 +51,9 @@
             shutil.rmtree(self.CA_PATH)
         os.mkdir(self.CA_PATH)
         create_CA_dir(raw, self.CA_PATH)
-        self.verify_ca_certs()
+        # Verifying needs network access; a supplied bundle is trusted as is
+        if not opts.path_to_cacerts:
+            self.verify_ca_certs()
 
     def verify_ca_certs(self):
         from calibre.utils.https import get_https_resource_securely
@@ -116,7 +118,7 @@
 
 class Resources(Command):  # {{{
     description = 'Compile various needed calibre resources'
-    sub_commands = ['liberation_fonts', 'mathjax', 'rapydscript', 'hyphenation', 'piper_voices']
+    sub_commands = ['liberation_fonts', 'mathjax', 'rapydscript', 'hyphenation']
     SYSTEM_CAMOUFOX_PATH = os.path.join(Command.RESOURCES, 'system-camoufox.json')
 
     def add_options(self, parser):
