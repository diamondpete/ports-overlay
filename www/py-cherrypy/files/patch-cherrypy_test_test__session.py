--- cherrypy/test/test_session.py.orig	2024-06-14 11:11:00 UTC
+++ cherrypy/test/test_session.py
@@ -434,9 +434,12 @@
             return True
         return False
 
+    # memcached refuses to start as root unless told whose identity to assume.
+    as_root = ['-u', 'root'] if os.geteuid() == 0 else []
+
     proc = watcher_getter(
         name='memcached',
-        arguments=['-p', str(port)],
+        arguments=['-p', str(port)] + as_root,
         checker=is_occupied,
         request=request,
     )
