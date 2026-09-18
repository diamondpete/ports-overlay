PORTNAME=	tavern
DISTVERSION=	3.6.3
CATEGORIES=	devel python
MASTER_SITES=	PYPI
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}

MAINTAINER=	ports@FreeBSD.org
COMMENT=	Command-line tool and pytest plugin for testing RESTful APIs
WWW=		https://taverntesting.github.io/

LICENSE=	MIT
LICENSE_FILE=	${WRKSRC}/LICENSE

BUILD_DEPENDS=	${PYTHON_PKGNAMEPREFIX}flit-core>=3.2:devel/py-flit-core@${PY_FLAVOR}
RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}jmespath>=1:devel/py-jmespath@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}jsonschema>=4:devel/py-jsonschema@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pyjwt>=2.5.0:www/py-pyjwt@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pykwalify>=1.8.0:textproc/py-pykwalify@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}python-box>=6:devel/py-python-box@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pyyaml>=6.0.1:devel/py-pyyaml@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}requests>=2.22.0:www/py-requests@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}simpleeval>=1.0.3:devel/py-simpleeval@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}stevedore>=4:devel/py-stevedore@${PY_FLAVOR}

USES=		python:3.11+
USE_PYTHON=	autoplist concurrent pep517 pytest

NO_ARCH=	yes

.include <bsd.port.mk>
