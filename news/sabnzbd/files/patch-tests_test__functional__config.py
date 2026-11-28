--- tests/test_functional_config.py.orig	2026-11-28 00:00:00 UTC
+++ tests/test_functional_config.py
@@ -143,6 +143,7 @@
         pass_login.clear()
         pass_login.send_keys("test_password")
         self.driver.find_element(By.TAG_NAME, "button").click()
+        wait_for(lambda: "/login/" not in self.driver.current_url, timeout=15)
 
         # Can we now go to the page and empty the settings again?
         self.open_page("http://%s:%s/config/general" % (SAB_HOST, SAB_PORT))
