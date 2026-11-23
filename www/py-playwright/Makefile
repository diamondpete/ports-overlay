PORTNAME=	playwright
DISTVERSION=	1.65.2
CATEGORIES=	www python
MASTER_SITES=	PYPI
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}

MAINTAINER=	ports@FreeBSD.org
COMMENT=	High-level API to automate web browsers
WWW=		https://playwright.dev/python/ \
		https://github.com/Microsoft/playwright-python

LICENSE=	APACHE20
LICENSE_FILE=	${WRKSRC}/LICENSE

BUILD_DEPENDS=	${PY_SETUPTOOLS} \
		${PYTHON_PKGNAMEPREFIX}setuptools-scm>=0:devel/py-setuptools-scm@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}wheel>=0.45.1:devel/py-wheel@${PY_FLAVOR}
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
		node24>0:www/node24 \
		${LINUX_DEPENDS}

USES=		linux:rl9 python
USE_PYTHON=	pep517 concurrent autoplist

LINUX_BASE=	${linux_ARGS}

XARCH:=		${ARCH:S/amd64/x64/:S/aarch64/arm64/}

TEST_ENV=	PYTHONPATH=${STAGEDIR}${PYTHONPREFIX_SITELIBDIR}

# the sdist ships the driver without Node.js and setup.py packs it as-is
post-patch:
	@${REINPLACE_CMD} \
		-e 's|^license = "Apache-2.0"|license = {text = "Apache-2.0"}|' \
		-e 's|^requires = .*|requires = ["setuptools", "setuptools-scm", "wheel"]|' \
		${WRKSRC}/pyproject.toml

post-install:
	# use the FreeBSD native node for the driver
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
