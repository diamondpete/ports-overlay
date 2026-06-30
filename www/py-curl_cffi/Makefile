PORTNAME=	curl_cffi
DISTVERSION=	0.15.1b2
CATEGORIES=	www python
MASTER_SITES=	PYPI \
		https://github.com/lexiforest/curl-impersonate/releases/download/v${LCI_VERSION}/:lci
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}
DISTFILES=	${DISTNAME}${EXTRACT_SUFX} \
		${LCI_DISTFILE}:lci

MAINTAINER=	ports@FreeBSD.org
COMMENT=	Python binding for curl-impersonate (browser TLS/JA3 fingerprints)
WWW=		https://github.com/lexiforest/curl_cffi

LICENSE=	MIT
LICENSE_FILE=	${WRKSRC}/LICENSE

# The cffi extension links the prebuilt libcurl-impersonate static lib; upstream
# ships x86_64 and aarch64 FreeBSD prebuilts.
ONLY_FOR_ARCHS=	amd64 aarch64

# Upstream libcurl-impersonate release that curl_cffi ${DISTVERSION} targets.
LCI_VERSION=	2.0.0a5
# Map FreeBSD ${ARCH} to the upstream asset arch and platform.uname().machine.
LCI_ARCH=	${ARCH:S/amd64/x86_64/}
LCI_MACHINE=	${ARCH:S/aarch64/arm64/}
LCI_DISTFILE=	libcurl-impersonate-v${LCI_VERSION}.${LCI_ARCH}-freebsd.tar.gz
LCI_LIBDIR=	${WRKSRC}/freebsd-libs

# Only the sdist is auto-extracted; the prebuilt lib is unpacked in post-extract.
EXTRACT_ONLY=	${DISTNAME}${EXTRACT_SUFX}

BUILD_DEPENDS=	${PYTHON_PKGNAMEPREFIX}cffi>=2.0.0:devel/py-cffi@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}setuptools>0:devel/py-setuptools@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}wheel>0:devel/py-wheel@${PY_FLAVOR}
RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}cffi>=2.0.0:devel/py-cffi@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}certifi>=2024.2.2:security/py-certifi@${PY_FLAVOR}

USES=		python:3.10+
USE_PYTHON=	autoplist concurrent pep517

# Unpack the prebuilt libcurl-impersonate (static lib + headers) where build.py
# expects it, and register FreeBSD in libs.json so the build links the local lib
# instead of downloading a (non-existent for us) prebuilt at build time.
post-extract:
	@${MKDIR} ${LCI_LIBDIR}
	@${TAR} -xf ${DISTDIR}/${LCI_DISTFILE} -C ${LCI_LIBDIR}

post-patch:
	@${REINPLACE_CMD} -e '1s|^\[|[{"system": "FreeBSD", "machine": "${LCI_MACHINE}", "pointer_size": 64, "sysname": "freebsd", "link_type": "static", "obj_name": "libcurl-impersonate.a", "arch": "${LCI_ARCH}", "libdir": "./freebsd-libs"},|' \
		${WRKSRC}/libs.json

.include <bsd.port.mk>
