--- qpy/QtCore/qpycore_pyqtslot.cpp.orig	2026-10-16 01:01:45 UTC
+++ qpy/QtCore/qpycore_pyqtslot.cpp
@@ -207,7 +207,15 @@
 {
     // Use the weak reference if possible.
     if (mself_wr)
-        return PyWeakref_GetObject(mself_wr);
+    {
+        // Python 3.15 removed PyWeakref_GetObject(); calling the weakref gives a
+        // new reference, released so this still returns a borrowed one.
+        PyObject *obj = PyObject_CallNoArgs(mself_wr);
+
+        Py_XDECREF(obj);
+
+        return obj;
+    }
 
     return mself;
 }
