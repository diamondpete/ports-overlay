--- setup/iso_codes.py.orig	2026-10-16 11:22:40 UTC
+++ setup/iso_codes.py
@@ -2,6 +2,7 @@
 # License: GPLv3 Copyright: 2023, Kovid Goyal <kovid at kovidgoyal.net>
 
 import fnmatch
+import glob
 import optparse
 import os
 import shutil
@@ -24,13 +25,19 @@
     description = 'Get ISO codes name localization data'
     top_level_filename = 'iso-codes-main'
     _zip_data = None
+    extracted = False
 
     def add_options(self, parser):
         with suppress(optparse.OptionConflictError):  # ignore if option already added
             parser.add_option('--path-to-isocodes', help='Path to previously downloaded iso-codes-main.zip')
+            parser.add_option('--isocodes-extracted', default=False, action='store_true',
+                    help='Isocodes is a directory')
 
     def run(self, opts):
-        if self._zip_data is None and opts.path_to_isocodes:
+        if opts.isocodes_extracted:
+            self.top_level = opts.path_to_isocodes
+            self.extracted = True
+        elif self._zip_data is None and opts.path_to_isocodes:
             with open(opts.path_to_isocodes, 'rb') as f:
                 self._zip_data = f.read()
             # get top level directory
@@ -49,12 +56,22 @@
         return self._zip_data or iso_codes_data()
 
     def db_data(self, name: str) -> bytes:
+        if self.extracted:
+            src = f'{self.top_level}/data/{name}'
+            if not os.path.exists(src):
+                raise Exception(src + ' does not exist')
+            with open(src, 'rb') as f:
+                return f.read()
         with zipfile.ZipFile(BytesIO(self.zip_data)) as zf:
             with zf.open(f'{self.top_level_filename}/data/{name}') as f:
                 return f.read()
 
     def extract_po_files(self, name: str, output_dir: str) -> None:
         name = name.split('.', 1)[0]
+        if self.extracted:
+            for name in glob.glob(f'{self.top_level}/{name}/*.po'):
+                shutil.copy2(name, os.path.join(output_dir, name.split('/')[-1]))
+            return
         pat = f'{self.top_level_filename}/{name}/*.po'
         with zipfile.ZipFile(BytesIO(self.zip_data)) as zf:
             for name in fnmatch.filter(zf.namelist(), pat):
