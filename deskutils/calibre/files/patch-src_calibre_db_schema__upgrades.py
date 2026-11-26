--- src/calibre/db/schema_upgrades.py.orig	2026-11-26 04:46:28 UTC
+++ src/calibre/db/schema_upgrades.py
@@ -866,7 +866,7 @@ CREATE TRIGGER fkc_annot_update
     def upgrade_version_26(self) -> None:
         "Drop unused columns from books and create pages table"
         assert self.db is not None
-        columns = {x[0] for x in self.db.execute('SELECT name FROM pragma_table_info("books")')}
+        columns = {x[0] for x in self.db.execute("SELECT name FROM pragma_table_info('books')")}
         statements = [
             '''
             CREATE TABLE books_pages_link (
