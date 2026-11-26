#!/bin/sh
# Build a port and its test dependencies in a poudriere jail, then hand over an
# interactive shell to run "make test" in.
set -eu

jail=151Ramd64
ptname=HEAD
overlay=
treesdir=/usr/local/poudriere/ports
poudriered=/usr/local/etc/poudriere.d

asRoot=no
while getopts op:r opt; do
	case ${opt} in
	o)	overlay=overlay ;;
	p)	ptname=${OPTARG} ;;
	r)	asRoot=yes ;;
	*)	echo "usage: ${0##*/} [-or] [-p tree] [origin]" >&2; exit 1 ;;
	esac
done
shift $((OPTIND - 1))

if [ $# -eq 0 ]; then
	port=$(make -VPKGORIGIN)
else
	port=$1
fi

portsdir=${treesdir}/${ptname}
portdir=${portsdir}/${port%%@*}
if [ -n "${overlay}" ] && [ -d "${treesdir}/${overlay}/${port%%@*}" ]; then
	portdir=${treesdir}/${overlay}/${port%%@*}
fi

# make test runs every phase from fetch, so the shell needs all of their deps.
# Entries are pattern:origin[:target]; keep the origin, never a trailing target.
# PORTSDIR points an overlay port at the tree it overlays, which holds Mk/.
dependsRaw=$(make -C "${portdir}" PORTSDIR="${portsdir}" -VFETCH_DEPENDS -VEXTRACT_DEPENDS \
	-VPATCH_DEPENDS -VBUILD_DEPENDS -VLIB_DEPENDS -VRUN_DEPENDS -VTEST_DEPENDS)
depends=$(echo ${dependsRaw} | tr ' ' '\n' | cut -d: -f2 | sort -u)

# Run the interactive shell as nobody rather than root, so fixtures that spawn
# a daemon are not refused.  poudriere reads this file last, after
# poudriere.conf and the per-tree and per-jail ones, so it wins.  poudriere
# refuses non-root with CCACHE_DIR set unless the cache is marked safe for it,
# which needs the host setup in scripts/README.md.  -r pins root instead.
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
		CCACHE_DIR_NON_ROOT_SAFE=yes
	EOF
fi
echo "$(echo "${port%%@*}" | tr / _)_SET_FORCE+=NLS" > "${makeconf}"

poudriere bulk -i -j "${jail}" -p "${ptname}" ${overlay:+-O "${overlay}"} ${port} ${depends}
