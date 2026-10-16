--- src/pip/_internal/metadata/importlib/_dists.py.orig	2026-10-16 00:19:33 UTC
+++ src/pip/_internal/metadata/importlib/_dists.py
@@ -91,6 +91,10 @@
             raise UnsupportedWheel(error)
         return text
 
+    def locate_file(self, path: "str | os.PathLike[str]") -> pathlib.Path:
+        # Python 3.15 made this abstract; an in-memory wheel has no files on disk
+        raise NotImplementedError
+
 
 class Distribution(BaseDistribution):
     def __init__(
@@ -204,7 +208,11 @@
         # a ton of fields that we need, including get() and get_payload(). We
         # rely on the implementation that the object is actually a Message now,
         # until upstream can improve the protocol. (python/cpython#94952)
-        return cast(email.message.Message, self._dist.metadata)
+        metadata = self._dist.metadata
+        # Python 3.15 returns None when the distribution has no metadata file
+        if metadata is None:
+            return email.message.Message()
+        return cast(email.message.Message, metadata)
 
     def iter_provided_extras(self) -> Iterable[str]:
         return self.metadata.get_all("Provides-Extra", [])
