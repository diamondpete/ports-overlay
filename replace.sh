#!/bin/sh
rm -rf /usr/ports/devel/py-cheetah3
rm -rf /usr/ports/sysutils/webmin
cp -Rp devel/py-cheetah3 /usr/ports/devel/py-cheetah3
cp -Rp sysutils/webmin /usr/ports/sysutils/webmin
chown -R root:wheel /usr/ports
