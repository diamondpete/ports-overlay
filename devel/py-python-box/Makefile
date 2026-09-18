PORTNAME=	python-box
DISTVERSION=	7.4.1
CATEGORIES=	devel python
MASTER_SITES=	PYPI
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}
DISTNAME=	${PORTNAME:S/-/_/}-${DISTVERSION}

MAINTAINER=	lazeraman@gmail.com
COMMENT=	Advanced Python dictionaries with dot notation access
WWW=		https://github.com/cdgriffith/Box

LICENSE=	MIT
LICENSE_FILE=	${WRKSRC}/LICENSE

BUILD_DEPENDS=	${PY_SETUPTOOLS} \
		${PYTHON_PKGNAMEPREFIX}wheel>=0:devel/py-wheel@${PY_FLAVOR}
RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}msgpack>=0:devel/py-msgpack@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}ruamel.yaml>=0:devel/py-ruamel.yaml@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}tomli-w>=0:textproc/py-tomli-w@${PY_FLAVOR}

USES=		python
USE_PYTHON=	autoplist concurrent pep517

NO_ARCH=	yes

.include <bsd.port.mk>
