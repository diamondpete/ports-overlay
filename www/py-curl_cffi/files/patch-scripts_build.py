--- scripts/build.py.orig	2026-07-02 00:00:00 UTC
+++ scripts/build.py
@@ -154,8 +154,8 @@
             f"-Wl,-force_load,{static_libs[0]}",
             "-lc++",
         ]
-    elif system in ("Linux", "Android"):
-        cxx_lib = "-lc++" if is_android else "-lstdc++"
+    elif system in ("Linux", "Android", "FreeBSD"):
+        cxx_lib = "-lc++" if is_android or system == "FreeBSD" else "-lstdc++"
         extra_link_args = [
             "-Wl,--whole-archive",
             static_libs[0],
