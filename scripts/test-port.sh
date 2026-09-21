#!/bin/sh
# Build a port and its test dependencies in a poudriere jail, then hand over an
# interactive shell to run "make test" in.
set -eu

jail=151Ramd64
ptname=HEAD
overlay=overlay
portsdir=/usr/local/poudriere/ports/${overlay}
poudriered=/usr/local/etc/poudriere.d

if [ $# -eq 0 ]; then
	port=$(make -VPKGORIGIN)
else
	port=$1
fi

buildDependsRaw=$(make -C "${portsdir}/${port}" -VBUILD_DEPENDS)
buildDepends=$(echo ${buildDependsRaw} | sed 's,[^ ]*:,,g')
testDependsRaw=$(make -C "${portsdir}/${port}" -VTEST_DEPENDS)
testDepends=$(echo ${testDependsRaw} | sed 's,[^ ]*:,,g')

# Run the interactive shell as nobody rather than root, so fixtures that spawn
# a daemon are not refused.  poudriere reads this file last, after
# poudriere.conf and the per-tree and per-jail ones, so it wins.  CCACHE_DIR
# has to be cleared with it: poudriere exits rather than build as non-root
# while it is set.
conf=${poudriered}/${jail}-${ptname}-poudriere.conf
if [ -e "${conf}" ]; then
	echo "${0##*/}: ${conf} exists, refusing to overwrite it" >&2
	exit 1
fi
cat > "${conf}" <<-EOF
	BUILD_AS_NON_ROOT=yes
	CCACHE_DIR=
EOF
trap 'rm -f "${conf}"' EXIT HUP INT TERM

poudriere bulk -i -j "${jail}" -p "${ptname}" -O "${overlay}" ${port} ${buildDepends} ${testDepends}
