#!/bin/sh
rm -rf /usr/ports/devel/py-cheetah3
rm -rf /usr/ports/sysutils/webmin
rm -rf /usr/ports/ftp/curl
cp -Rp devel/py-cheetah3 /usr/ports/devel/py-cheetah3
cp -Rp sysutils/webmin /usr/ports/sysutils/webmin
cp -Rp ftp/curl /usr/ports/ftp/curl
chown -R root:wheel /usr/ports
