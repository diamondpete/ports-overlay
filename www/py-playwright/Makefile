PORTNAME=	playwright
DISTVERSIONPREFIX=	v
DISTVERSION=	1.61.0
PORTREVISION=	1
CATEGORIES=	www python
MASTER_SITES+=	https://registry.npmjs.org/playwright-core/-/:npm # the JS "driver" ships as the playwright-core npm package
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}
DISTFILES=	playwright-core-${DRIVER_VERSION}.tgz:npm
EXTRACT_ONLY=	${DISTNAME}${EXTRACT_SUFX} # do not extract the npm driver package; it is assembled in pre-build

MAINTAINER=	ports@FreeBSD.org
COMMENT=	High-level API to automate web browsers
WWW=		https://playwright.dev/python/ \
		https://github.com/Microsoft/playwright-python

LICENSE=	APACHE20
LICENSE_FILE=	${WRKSRC}/LICENSE

DRIVER_VERSION=	1.61.1-beta-1782139630000

BUILD_DEPENDS=	${PY_SETUPTOOLS} \
		${PYTHON_PKGNAMEPREFIX}setuptools-scm>=0:devel/py-setuptools-scm@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}wheel>=0.45.1:devel/py-wheel@${PY_FLAVOR} \
		zip:archivers/zip
LINUX_DEPENDS=	linux-${LINUX_BASE}-alsa-lib>0:audio/linux-${LINUX_BASE}-alsa-lib \
		linux-${LINUX_BASE}-at-spi2-atk>0:accessibility/linux-${LINUX_BASE}-at-spi2-atk \
		linux-${LINUX_BASE}-atk>0:accessibility/linux-${LINUX_BASE}-atk \
		linux-${LINUX_BASE}-cairo>0:graphics/linux-${LINUX_BASE}-cairo \
		linux-${LINUX_BASE}-cups-libs>0:print/linux-${LINUX_BASE}-cups-libs \
		linux-${LINUX_BASE}-dbus-libs>0:devel/linux-${LINUX_BASE}-dbus-libs \
		linux-${LINUX_BASE}-dri>0:graphics/linux-${LINUX_BASE}-dri \
		linux-${LINUX_BASE}-gstreamer1>0:multimedia/linux-${LINUX_BASE}-gstreamer1 \
		linux-${LINUX_BASE}-libxkbcommon>0:x11/linux-${LINUX_BASE}-libxkbcommon \
		linux-${LINUX_BASE}-nspr>0:devel/linux-${LINUX_BASE}-nspr \
		linux-${LINUX_BASE}-nss>0:security/linux-${LINUX_BASE}-nss \
		linux-${LINUX_BASE}-pango>0:x11-toolkits/linux-${LINUX_BASE}-pango
RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}greenlet>=3.1.1:devel/py-greenlet@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pyee>=13:devel/py-pyee@${PY_FLAVOR}
RUN_DEPENDS+=	node24>0:www/node24 \
		${LINUX_DEPENDS}

USES=		linux:rl9 python
USE_PYTHON=	pep517 concurrent autoplist

USE_GITHUB=	yes
GH_ACCOUNT=	Microsoft
GH_PROJECT=	playwright-python

LINUX_BASE=	${linux_ARGS}

MAKE_ENV=	SETUPTOOLS_SCM_PRETEND_VERSION=${PORTVERSION}

XARCH:=		${ARCH:S/amd64/x64/:S/aarch64/arm64/}

TEST_ENV=	${MAKE_ENV} PYTHONPATH=${STAGEDIR}${PYTHONPREFIX_SITELIBDIR}

post-patch:
	@${REINPLACE_CMD} \
		-e 's|^license = "Apache-2.0"|license = {text = "Apache-2.0"}|' \
		-e 's|^requires = .*|requires = ["setuptools", "setuptools-scm", "wheel"]|' \
		${WRKSRC}/pyproject.toml
	# select the Linux wheel bundle; FreeBSD is not a recognized platform
	@${REINPLACE_CMD} \
		-e 's|lambda wheel: wheel\["platform"\] == sys.platform|lambda wheel: wheel["zip_name"] == "linux" or wheel["platform"] == sys.platform|' \
		-e 's|lambda wheel: wheel\["machine"\] == platform.machine().lower()|lambda wheel: wheel["zip_name"] == "linux" or wheel["machine"] == platform.machine().lower()|' \
		${WRKSRC}/setup.py

pre-build:
	@${MKDIR} ${WRKDIR}/driver-bundle
	@${TAR} -xf ${DISTDIR}/playwright-core-${DRIVER_VERSION}.tgz -C ${WRKDIR}/driver-bundle
	@${TOUCH} ${WRKDIR}/driver-bundle/node
	@${CHMOD} 0755 ${WRKDIR}/driver-bundle/node
	@${CP} ${WRKSRC}/LICENSE ${WRKDIR}/driver-bundle/LICENSE
	@${MKDIR} ${WRKSRC}/driver
	@cd ${WRKDIR}/driver-bundle && \
		${LOCALBASE}/bin/zip -qr ${WRKSRC}/driver/playwright-${DRIVER_VERSION}-linux.zip .

post-install:
	# replace the placeholder node with the FreeBSD native binary
	@cd ${STAGEDIR}${PYTHONPREFIX_SITELIBDIR}/playwright/driver && \
		${RM} -f node && \
		${LN} -s ${LOCALBASE}/bin/node
	# patch JS scripts: process.platform
	@${GREP} -rl 'process.platform === "linux"' ${STAGEDIR}${PYTHONPREFIX_SITELIBDIR} | \
		${GREP} "\.js$$" | \
		${XARGS} ${REINPLACE_CMD} -i '' \
			-e 's/process.platform === "linux"/(process.platform === "linux" || process.platform === "freebsd")/'
	@${GREP} -rl 'process.platform !== "linux"' ${STAGEDIR}${PYTHONPREFIX_SITELIBDIR} | \
		${GREP} "\.js$$" | \
		${XARGS} ${REINPLACE_CMD} -i '' \
			-e 's/process.platform !== "linux"/(process.platform !== "linux" \&\& process.platform !== "freebsd")/'
	# force host platform (moved from hostPlatform.js into coreBundle.js in 1.61)
	@${REINPLACE_CMD} \
		-i '' \
		-e 's/if (process.env.PLAYWRIGHT_HOST_PLATFORM_OVERRIDE) {/if (true) {/' \
		-e 's/process.env.PLAYWRIGHT_HOST_PLATFORM_OVERRIDE/"ubuntu24.04-${XARCH}"/' \
		${STAGEDIR}${PYTHONPREFIX_SITELIBDIR}/playwright/driver/package/lib/coreBundle.js

do-test:
	@${SETENV} ${TEST_ENV} ${STAGEDIR}${PREFIX}/bin/playwright install
.for test in test-sync.py test-async.py
	@cd ${TEST_WRKSRC} && \
		${SETENV} ${TEST_ENV} ${PYTHON_CMD} ${FILESDIR}/${test}
.endfor

.include <bsd.port.mk>
