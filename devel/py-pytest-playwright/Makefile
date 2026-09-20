PORTNAME=	pytest-playwright
DISTVERSION=	0.9.0
CATEGORIES=	devel python
MASTER_SITES=	PYPI
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}
DISTNAME=	${PORTNAME:S/-/_/g}-${DISTVERSION}

MAINTAINER=	lazeraman@gmail.com
COMMENT=	Pytest plugin with fixtures for Playwright browser automation
WWW=		https://github.com/microsoft/playwright-pytest

LICENSE=	APACHE20
LICENSE_FILE=	${WRKSRC}/LICENSE

BUILD_DEPENDS=	${PY_SETUPTOOLS} \
		${PYTHON_PKGNAMEPREFIX}setuptools-scm>=0:devel/py-setuptools-scm@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}wheel>=0:devel/py-wheel@${PY_FLAVOR}
RUN_DEPENDS=	${PY_EXCEPTIONGROUP} \
		${PYTHON_PKGNAMEPREFIX}playwright>=1.18:www/py-playwright@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pytest>=6.2.4:devel/py-pytest@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pytest-base-url>=1.0.0:devel/py-pytest-base-url@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}python-slugify>=6.0.0:textproc/py-python-slugify@${PY_FLAVOR}

USES=		python:3.10+
USE_PYTHON=	autoplist concurrent pep517

NO_ARCH=	yes

.include <bsd.port.mk>
