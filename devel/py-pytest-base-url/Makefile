PORTNAME=	pytest-base-url
DISTVERSION=	2.1.0
CATEGORIES=	devel python
MASTER_SITES=	PYPI
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}
DISTNAME=	${PORTNAME:S/-/_/g}-${DISTVERSION}

MAINTAINER=	lazeraman@gmail.com
COMMENT=	Pytest plugin for URL based testing
WWW=		https://github.com/pytest-dev/pytest-base-url

LICENSE=	MPL20
LICENSE_FILE=	${WRKSRC}/LICENSE

BUILD_DEPENDS=	${PYTHON_PKGNAMEPREFIX}hatch-vcs>=0.3:devel/py-hatch-vcs@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}hatchling>=1.13:devel/py-hatchling@${PY_FLAVOR}
RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}pytest>=7.0.0:devel/py-pytest@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}requests>=2.9:www/py-requests@${PY_FLAVOR}
TEST_DEPENDS=	${PYTHON_PKGNAMEPREFIX}packaging>=0:devel/py-packaging@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pytest-localserver>=0.7.1:devel/py-pytest-localserver@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pytest-metadata>=0:devel/py-pytest-metadata@${PY_FLAVOR}

USES=		python
USE_PYTHON=	autoplist concurrent pep517 pytest

NO_ARCH=	yes

OPTIONS_DEFINE=	METADATA
METADATA_DESC=	Record the base URL in pytest-metadata reports

METADATA_RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}pytest-metadata>=0:devel/py-pytest-metadata@${PY_FLAVOR}

.include <bsd.port.mk>
