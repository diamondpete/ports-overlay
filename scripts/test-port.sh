#!/bin/sh
# Build a port and its test dependencies in a poudriere jail, then hand over an
# interactive shell to run "make test" in.
set -eu

jail=151Ramd64
ptname=HEAD
overlay=overlay
portsdir=/usr/local/poudriere/ports/${overlay}
poudriered=/usr/local/etc/poudriere.d

asRoot=no
while getopts r opt; do
	case ${opt} in
	r)	asRoot=yes ;;
	*)	echo "usage: ${0##*/} [-r] [origin]" >&2; exit 1 ;;
	esac
done
shift $((OPTIND - 1))

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
# while it is set.  -r pins root instead and leaves CCACHE_DIR alone.
conf=${poudriered}/${jail}-${ptname}-poudriere.conf
# NLS is forced on for the port under test only, so translation tests have a
# locale to load; _SET_FORCE outranks saved options, dependencies keep theirs.
makeconf=${poudriered}/${jail}-${ptname}-make.conf
for f in "${conf}" "${makeconf}"; do
	if [ -e "${f}" ]; then
		echo "${0##*/}: ${f} exists, refusing to overwrite it" >&2
		exit 1
	fi
done
trap 'rm -f "${conf}" "${makeconf}"' EXIT HUP INT TERM
if [ "${asRoot}" = yes ]; then
	echo "BUILD_AS_NON_ROOT=no" > "${conf}"
else
	cat > "${conf}" <<-EOF
		BUILD_AS_NON_ROOT=yes
		CCACHE_DIR=
	EOF
fi
echo "$(echo "${port%%@*}" | tr / _)_SET_FORCE+=NLS" > "${makeconf}"

poudriere bulk -i -j "${jail}" -p "${ptname}" -O "${overlay}" ${port} ${buildDepends} ${testDepends}
