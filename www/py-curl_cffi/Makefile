PORTNAME=	curl_cffi
DISTVERSION=	0.15.1b2
CATEGORIES=	www python
MASTER_SITES=	PYPI
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}

MAINTAINER=	ports@FreeBSD.org
COMMENT=	Python binding for curl-impersonate (browser TLS/JA3 fingerprints)
WWW=		https://github.com/lexiforest/curl_cffi

LICENSE=	MIT
LICENSE_FILE=	${WRKSRC}/LICENSE

ONLY_FOR_ARCHS=	amd64 aarch64

LCI_MACHINE=	${ARCH:S/aarch64/arm64/}
LCI_ARCH=	${ARCH:S/amd64/x86_64/}

BUILD_DEPENDS=	curl-impersonate>0:www/curl-impersonate \
		${PYTHON_PKGNAMEPREFIX}cffi>=2.0.0:devel/py-cffi@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}setuptools>0:devel/py-setuptools@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}wheel>0:devel/py-wheel@${PY_FLAVOR}
RUN_DEPENDS=	curl-impersonate>0:www/curl-impersonate \
		${PYTHON_PKGNAMEPREFIX}cffi>=2.0.0:devel/py-cffi@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}certifi>=2024.2.2:security/py-certifi@${PY_FLAVOR}

USES=		localbase python:3.10+
USE_PYTHON=	autoplist concurrent pep517

post-patch:
	@${REINPLACE_CMD} -e '1s|^\[|[{"system": "FreeBSD", "machine": "${LCI_MACHINE}", "pointer_size": 64, "sysname": "freebsd", "link_type": "dynamic", "obj_name": "libcurl-impersonate.so", "arch": "${LCI_ARCH}", "libdir": "${LOCALBASE}/lib"},|' \
		${WRKSRC}/libs.json
	@${REINPLACE_CMD} -e 's|str(libdir / "include"),|str(libdir / "include"), "${LOCALBASE}/include/curl-impersonate",|' \
		${WRKSRC}/scripts/build.py

.include <bsd.port.mk>
