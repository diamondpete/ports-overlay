PORTNAME=	zc.lockfile
PORTVERSION=	4.0
CATEGORIES=	devel python
MASTER_SITES=	PYPI
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}
DISTNAME=		zc_lockfile-${PORTVERSION}

MAINTAINER=	sunpoet@FreeBSD.org
COMMENT=	Basic inter-process locks
WWW=		https://github.com/zopefoundation/zc.lockfile

LICENSE=	ZPL21
LICENSE_FILE=	${WRKSRC}/LICENSE.txt

BUILD_DEPENDS=	${PY_SETUPTOOLS} \
		${PYTHON_PKGNAMEPREFIX}wheel>=0:devel/py-wheel@${PY_FLAVOR}

USES=		python
USE_PYTHON=	autoplist concurrent pep517

NO_ARCH=	yes

.include <bsd.port.mk>
