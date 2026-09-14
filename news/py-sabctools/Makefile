PORTNAME=	sabctools
PORTVERSION=	9.7.1
CATEGORIES=	news python
MASTER_SITES=	PYPI
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}

MAINTAINER=	sunpoet@FreeBSD.org
COMMENT=	Python yEnc package optimized for use within SABnzbd
WWW=		https://github.com/sabnzbd/sabctools

LICENSE=	GPLv2+
LICENSE_FILE=	${WRKSRC}/LICENSE.md

BUILD_DEPENDS=	${PYTHON_PKGNAMEPREFIX}scikit-build-core>=0:devel/py-scikit-build-core@${PY_FLAVOR}

USES=		cmake:indirect python
USE_PYTHON=	autoplist concurrent pep517

post-install:
	${FIND} ${STAGEDIR}${PYTHON_SITELIBDIR} -name '*.so' -exec ${STRIP_CMD} {} +

.include <bsd.port.mk>
