PORTNAME=	opencv-python-headless
DISTVERSION=	5.0.0.93
PORTREVISION=	1
CATEGORIES=	graphics
MASTER_SITES=	PYPI
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}

MAINTAINER=	ports@FreeBSD.org
COMMENT=	Wrapper package for OpenCV python bindings
WWW=		https://github.com/opencv/opencv-python

LICENSE=	MIT
LICENSE_FILE=	${WRKSRC}/LICENSE.txt

BUILD_DEPENDS=	${PYTHON_PKGNAMEPREFIX}scikit-build>=0.14.0:devel/py-scikit-build@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}numpy>0:math/py-numpy@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}setuptools>0:devel/py-setuptools@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pip>0:devel/py-pip@${PY_FLAVOR} \
		cmake:devel/cmake
LIB_DEPENDS=	libavif.so:graphics/libavif \
		libwebp.so:graphics/webp \
		libpng16.so:graphics/png \
		libtiff.so:graphics/tiff \
		libopenjp2.so:graphics/openjpeg \
		libavcodec.so:multimedia/ffmpeg \
		libopenblas.so:math/openblas

USES=		gnome gstreamer jpeg python
USE_GNOME=	glib20
USE_GSTREAMER1=	yes
USE_PYTHON=	pep517 autoplist pytest

USE_GITHUB=	yes
GH_ACCOUNT=	opencv
GH_PROJECT=	opencv-python
GH_TAGNAME=	93
GH_TUPLE=	opencv:opencv:40738fb16ceddb5fb3fea747585f7ce6abb0605b:opencv/opencv \
		opencv:opencv_contrib:755e50675d97db9b7d449d8bd6b09888646f6c6e:opencv_contrib/opencv_contrib

MAKE_ENV=	ENABLE_HEADLESS=1 \
		OPENCV_PYTHON_PACKAGE_NAME=opencv-python-headless

TEST_ENV=	${MAKE_ENV} PYTHONPATH=${STAGEDIR}${PYTHONPREFIX_SITELIBDIR}
TEST_WRKSRC=	${WRKSRC}/opencv/modules/python

CONFLICTS_INSTALL=	opencv # opencv has the same python bindings bundled in

OPTIONS_DEFINE=		PROTOBUF
OPTIONS_DEFAULT=	PROTOBUF

PROTOBUF_DESC=		DNN module support (uses system protobuf)
PROTOBUF_LIB_DEPENDS=	libprotobuf.so:devel/protobuf

post-patch:
	@${PRINTF} 'opencv_version = "${DISTVERSION}"\ncontrib = False\nheadless = True\nrolling = False\nci_build = False' \
		> ${WRKSRC}/cv2/version.py

post-patch-PROTOBUF-on:
	@${REINPLACE_CMD} -e \
		's|"-DWITH_PROTOBUF=OFF",|"-DWITH_PROTOBUF=ON", "-DBUILD_PROTOBUF=OFF", "-DPROTOBUF_UPDATE_FILES=ON",|' \
		${WRKSRC}/setup.py
	@${CP} ${FILESDIR}/opencv-caffe.proto ${WRKSRC}/opencv/modules/dnn/src/caffe/

.include <bsd.port.mk>
