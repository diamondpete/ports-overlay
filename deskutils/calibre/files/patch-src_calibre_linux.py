--- src/calibre/linux.py.orig	2026-10-25 03:20:04 UTC
+++ src/calibre/linux.py
@@ -1237,7 +1237,7 @@
 GenericName=Viewer for E-books
 Comment=Viewer for E-books in all the major formats
 TryExec=ebook-viewer
-Exec=ebook-viewer --detach %f
+Exec=ebook-viewer %f
 Icon=calibre-viewer
 Categories=Office;Viewer;
 Keywords=epub;ebook;viewer;
@@ -1251,7 +1251,7 @@
 GenericName=Editor for E-books
 Comment=Edit E-books in various formats
 TryExec=ebook-edit
-Exec=ebook-edit --detach %f
+Exec=ebook-edit %f
 Icon=calibre-ebook-edit
 Categories=Office;WordProcessor
 Keywords=epub;ebook;editor;
@@ -1265,7 +1265,7 @@
 GenericName=E-book library management
 Comment=E-book library management: Convert, view, share, catalogue all your e-books
 TryExec=calibre
-Exec=calibre --detach %U
+Exec=calibre %U
 Icon=calibre-gui
 Categories=Office;
 X-GNOME-UsesNotifications=true
