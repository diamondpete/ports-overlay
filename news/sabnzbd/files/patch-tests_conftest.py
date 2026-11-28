--- tests/conftest.py.orig	2026-11-28 00:00:00 UTC
+++ tests/conftest.py
@@ -165,7 +165,6 @@
 
     # Headless during CI testing
     if "CI" in os.environ:
-        driver_options.browser_version = "127"
         driver_options.add_argument("--headless")
         driver_options.add_argument("--no-sandbox")
 
