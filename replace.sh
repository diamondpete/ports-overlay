#!/bin/sh
rm -rf /usr/ports/ftp/curl
rm -rf /usr/ports/net-p2p/jackett
rm -rf /usr/ports/sysutils/webmin
rm -rf /usr/ports/textproc/py-sphinx
cp -Rp ftp/curl /usr/ports/ftp/curl
cp -Rp net-p2p/jackett /usr/ports/net-p2p/jackett
cp -Rp sysutils/webmin /usr/ports/sysutils/webmin
cp -Rp textproc/py-sphinx /usr/ports/textproc/py-sphinx
chown -R root:wheel /usr/ports
