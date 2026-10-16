--- setup/build.py.orig	2026-10-16 11:23:37 UTC
+++ setup/build.py
@@ -470,6 +470,8 @@
                 continue
             if not is_ext_allowed(self.compiling_for, ext):
                 continue
+            if ext.name == 'piper':
+                continue
             if ext.error:
                 if ext.optional:
                     self.warn(ext.error)
@@ -748,6 +750,7 @@
 library-dirs = {ext.lib_dirs}
 qmake-QT = {ext.qt_modules}
 sip-file = {os.path.basename(sipf)!r}
+tags = ["WS_X11"]
 ''')
         shutil.copy2(sipf, src_dir)
 
