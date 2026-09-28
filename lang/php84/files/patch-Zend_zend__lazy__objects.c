--- Zend/zend_lazy_objects.c.orig
+++ Zend/zend_lazy_objects.c
@@ -179,6 +179,18 @@ bool zend_lazy_object_decr_lazy_props(zend_object *obj)
 	return info->lazy_properties_count == 0;
 }
 
+/* See zend_update_class_constants(). */
+static zend_always_inline bool zend_class_constants_are_updated(const zend_class_entry *ce) {
+	if (ce->ce_flags & ZEND_ACC_CONSTANTS_UPDATED) {
+		return true;
+	}
+	if (ZEND_MAP_PTR(ce->mutable_data)) {
+		const zend_class_mutable_data *mutable_data = ZEND_MAP_PTR_GET_IMM(ce->mutable_data);
+		return mutable_data && (mutable_data->ce_flags & ZEND_ACC_CONSTANTS_UPDATED);
+	}
+	return false;
+}
+
 /**
  * Making objects lazy
  */
@@ -259,11 +271,9 @@ ZEND_API zend_object *zend_object_make_lazy(zend_object *obj,
 			return NULL;
 		}
 
-		if (UNEXPECTED(!(reflection_ce->ce_flags & ZEND_ACC_CONSTANTS_UPDATED))) {
-			if (UNEXPECTED(zend_update_class_constants(reflection_ce) != SUCCESS)) {
-				ZEND_ASSERT(EG(exception));
-				return NULL;
-			}
+		if (UNEXPECTED(zend_update_class_constants(reflection_ce) != SUCCESS)) {
+			ZEND_ASSERT(EG(exception));
+			return NULL;
 		}
 
 		obj = zend_objects_new(reflection_ce);
@@ -383,7 +393,9 @@ ZEND_API zend_object *zend_lazy_object_mark_as_initialized(zend_object *obj)
 
 	zend_class_entry *ce = obj->ce;
 
-	ZEND_ASSERT(ce->ce_flags & ZEND_ACC_CONSTANTS_UPDATED);
+#if ZEND_DEBUG
+	ZEND_ASSERT(zend_class_constants_are_updated(ce));
+#endif
 
 	zval *default_properties_table = CE_DEFAULT_PROPERTIES_TABLE(ce);
 	zval *properties_table = obj->properties_table;
@@ -579,7 +591,9 @@ ZEND_API zend_object *zend_lazy_object_init(zend_object *obj)
 
 	zend_class_entry *ce = obj->ce;
 
-	ZEND_ASSERT(ce->ce_flags & ZEND_ACC_CONSTANTS_UPDATED);
+#if ZEND_DEBUG
+	ZEND_ASSERT(zend_class_constants_are_updated(ce));
+#endif
 
 	if (zend_object_is_lazy_proxy(obj)) {
 		return zend_lazy_object_init_proxy(obj);
