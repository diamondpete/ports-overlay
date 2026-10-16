--- yao-pkg/node_modules/@yao-pkg/pkg-fetch/lib-es5/build.js.orig	2026-06-20 01:40:33 UTC
+++ yao-pkg/node_modules/@yao-pkg/pkg-fetch/lib-es5/build.js
@@ -49,7 +49,7 @@
     // build past GitHub Actions' 6h job limit (worst on the Intel x64 runner).
     // See yao-pkg/pkg-fetch#170.
     if (major >= 12) {
-        if (system_1.hostPlatform !== 'win' && targetPlatform !== 'macos') {
+        if (system_1.hostPlatform !== 'win' && targetPlatform !== 'macos' && targetPlatform !== 'freebsd') {
             args.push('--enable-lto');
         }
     }
@@ -64,7 +64,16 @@
     args.push('--without-npm');
     // Small ICU
     if (system_1.hostPlatform !== 'win' || major < 24) {
-        args.push('--with-intl=small-icu');
+        args.push('--with-intl=system-icu');
+        args.push('--shared-openssl');
+        args.push('--shared-openssl-includes=%%OPENSSL_INC%%');
+        args.push('--shared-openssl-libpath=%%OPENSSL_LIB%%');
+        args.push('--openssl-use-def-ca-store');
+        args.push('--shared-brotli');
+        args.push('--shared-cares');
+        args.push('--shared-libuv');
+        args.push('--shared-nghttp2');
+        args.push('--shared-zlib');
     }
     // Workaround for nodejs/node#39313
     // All supported macOS versions have zlib as a system library
@@ -214,6 +223,10 @@
     }
     args.push(...getConfigureArgs(getMajor(nodeVersion), targetPlatform, targetArch));
     log_1.log.info("Running configure with: ", args.join(" "));
+    // Node 24 refuses Python 3.15; nodejs/node#65750 allowlists it
+    const configurePath = path_1.default.join(nodePath, 'configure');
+    (0, fs_1.writeFileSync)(configurePath, (0, fs_1.readFileSync)(configurePath, 'utf8')
+        .replace('acceptable_pythons = (', 'acceptable_pythons = ((3, 15), '));
     // TODO same for windows?
     await (0, utils_1.spawn)('/bin/sh', ['./configure', ...args], {
         cwd: nodePath,
