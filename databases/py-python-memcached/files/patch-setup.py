--- setup.py.orig	2024-01-14 10:55:00 UTC
+++ setup.py
@@ -1,11 +1,12 @@
 #!/usr/bin/env python
 
-from setuptools.depends import get_module_constant
+import re
+
 from setuptools import setup  # noqa
 
 dl_url = "https://github.com/linsomniac/python-memcached/releases/download/{0}/python-memcached-{0}.tar.gz"
 
-version = get_module_constant('memcache', '__version__')
+version = re.search(r'^__version__ = "(.*)"', open("memcache.py").read(), re.M).group(1)
 setup(
     name="python-memcached",
     version=version,
