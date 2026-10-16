--- qpy/QtCore/qpycore_qmetaobjectbuilder.h.orig	2026-10-16 20:03:31 UTC
+++ qpy/QtCore/qpycore_qmetaobjectbuilder.h
@@ -64,7 +64,11 @@
 class Q_CORE_EXPORT QMetaMethodBuilder
 {
 public:
+#if QT_VERSION >= QT_VERSION_CHECK(6, 11, 2)
+    QMetaMethodBuilder() : _mobj(0), _index(0), _type(QMetaMethod::Method) {}
+#else
     QMetaMethodBuilder() : _mobj(0), _index(0) {}
+#endif
 
     void setReturnType(const QByteArray &type);
     void setParameterNames(const QList<QByteArray> &parameter_names);
@@ -73,6 +77,9 @@
 private:
     const QMetaObjectBuilder *_mobj;
     int _index;
+#if QT_VERSION >= QT_VERSION_CHECK(6, 11, 2)
+    QMetaMethod::MethodType _type;
+#endif
 };
 
 
