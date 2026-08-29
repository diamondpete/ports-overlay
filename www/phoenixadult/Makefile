PORTNAME=	phoenixadult
DISTVERSION=	1.0.0a476
CATEGORIES=	www

MAINTAINER=	ports@FreeBSD.org
COMMENT=	Plex metadata provider for scene videos from adult sites
WWW=		https://codeberg.org/PhoenixAdultProvider/PhoenixAdult

LICENSE=	GPLv3+
LICENSE_FILE=	${WRKSRC}/LICENSE

PA_COMMIT=	b2b4f7a5effe93bc216b1ade8d0784b192d262a0
MASTER_SITES=	https://codeberg.org/PhoenixAdultProvider/PhoenixAdult/archive/
DISTFILES=	${PA_COMMIT}${EXTRACT_SUFX}
DIST_SUBDIR=	${PORTNAME}
WRKSRC=		${WRKDIR}/${PORTNAME}-src

BUILD_DEPENDS=	${PYTHON_PKGNAMEPREFIX}setuptools>0:devel/py-setuptools@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}wheel>0:devel/py-wheel@${PY_FLAVOR}
RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}Jinja2>=3.1:devel/py-Jinja2@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}fastapi>=0.115:www/py-fastapi@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pydantic2>=2.9:devel/py-pydantic2@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}starlette>=0.40:www/py-starlette@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}sqlite3>0:databases/py-sqlite3@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}uvicorn>=0.34:www/py-uvicorn@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}uvloop>0:devel/py-uvloop@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}httptools>0:www/py-httptools@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}websockets>0:devel/py-websockets@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}watchfiles>0:devel/py-watchfiles@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}httpx2>=2.0:www/py-httpx2@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}lxml>=5.0:devel/py-lxml@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}parsel>=1.9:textproc/py-parsel@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pillow>=11.0:graphics/py-pillow@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}python-dotenv>=1.0:www/py-python-dotenv@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}python-multipart>=0.0.20:www/py-python-multipart@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}python-slugify>=8.0:textproc/py-python-slugify@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}rapidfuzz>=3.10:devel/py-rapidfuzz@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}python-dateutil>=2.9:devel/py-python-dateutil@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}text-unidecode>=1.3:converters/py-text-unidecode@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}text2digits>=0.1:textproc/py-text2digits@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}w3lib>=1.21:www/py-w3lib@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}zxcvbn>=4.4:security/py-zxcvbn@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}cachetools>=5.3:devel/py-cachetools@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}cryptography>=43.0:security/py-cryptography@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}ddgs>=9.0:www/py-ddgs@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}filelock>=3.12:sysutils/py-filelock@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}ftfy>=6.1:textproc/py-ftfy@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}argon2-cffi>=23.1:security/py-argon2-cffi@${PY_FLAVOR}
TEST_DEPENDS=	${PYTHON_PKGNAMEPREFIX}httpx>=0.27:www/py-httpx@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pytest>=8.3,1:devel/py-pytest@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pytest-asyncio>=0.24:devel/py-pytest-asyncio@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pytest-httpx2>=1.0:devel/py-pytest-httpx2@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}respx>=0.21:www/py-respx@${PY_FLAVOR}

USES=		python:3.13+
USE_PYTHON=	autoplist noflavors pep517 pytest
USE_RC_SUBR=	phoenixadult

NO_ARCH=	yes

PA_USER=	phoenixadult
PA_GROUP=	phoenixadult
PA_DIR=		/var/db/phoenixadult

OPTIONS_DEFINE=		IMPERSONATE FACE PLAYWRIGHT
OPTIONS_DEFAULT=	IMPERSONATE FACE MAGICKNOX11
OPTIONS_RADIO=		MAGICK
OPTIONS_RADIO_MAGICK=	MAGICKX11 MAGICKNOX11
IMPERSONATE_DESC=	Cloudflare TLS-fingerprint bypass (curl-impersonate)
FACE_DESC=		Face-detection headshot cropping (OpenCV + YuNet)
MAGICK_DESC=		SVG clearLogo rasterization (librsvg + ImageMagick)
MAGICKX11_DESC=		ImageMagick7 with X11
MAGICKNOX11_DESC=	ImageMagick7 without X11
PLAYWRIGHT_DESC=	JS / AWS-WAF bypass via Playwright (needs a browser)

IMPERSONATE_RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}curl_cffi>0:www/py-curl_cffi@${PY_FLAVOR}
FACE_RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}opencv-python-headless>0:graphics/py-opencv-python-headless@${PY_FLAVOR} \
			${PYTHON_PKGNAMEPREFIX}numpy>0:math/py-numpy@${PY_FLAVOR}
MAGICKX11_RUN_DEPENDS=	magick:graphics/ImageMagick7@x11 \
			rsvg-convert:graphics/librsvg2-rust
MAGICKNOX11_RUN_DEPENDS=	magick:graphics/ImageMagick7@nox11 \
			rsvg-convert:graphics/librsvg2-rust
PLAYWRIGHT_RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}playwright>0:www/py-playwright@${PY_FLAVOR}

SUB_FILES=	phoenixadult-run pkg-message
SUB_LIST=	PYTHON_CMD=${PYTHON_CMD} \
		DATADIR=${DATADIR} \
		PA_USER=${PA_USER} \
		PA_GROUP=${PA_GROUP} \
		PA_DIR=${PA_DIR}

PLIST_FILES=	%%DATADIR%%/phoenixadult-run \
		%%DATADIR%%/env.sample \
		%%DATADIR%%/scripts/rename_studio.py \
		%%DATADIR%%/scripts/find_artwork_mismatches.py \
		%%DATADIR%%/scripts/migrate_snapshot_layout.py \
		%%DATADIR%%/scripts/rebuild_from_bundles.py

post-extract:
	@${MV} ${WRKDIR}/${PORTNAME} ${WRKSRC}

post-install:
	@${MKDIR} ${STAGEDIR}${DATADIR} ${STAGEDIR}${DATADIR}/scripts
	${INSTALL_SCRIPT} ${WRKDIR}/phoenixadult-run ${STAGEDIR}${DATADIR}/phoenixadult-run
	${INSTALL_DATA} ${FILESDIR}/phoenixadult.env.sample ${STAGEDIR}${DATADIR}/env.sample
	${INSTALL_SCRIPT} ${WRKSRC}/scripts/rename_studio.py ${STAGEDIR}${DATADIR}/scripts/
	${INSTALL_SCRIPT} ${WRKSRC}/scripts/find_artwork_mismatches.py ${STAGEDIR}${DATADIR}/scripts/
	${INSTALL_SCRIPT} ${WRKSRC}/scripts/migrate_snapshot_layout.py ${STAGEDIR}${DATADIR}/scripts/
	${INSTALL_SCRIPT} ${WRKSRC}/scripts/rebuild_from_bundles.py ${STAGEDIR}${DATADIR}/scripts/

.include <bsd.port.mk>
