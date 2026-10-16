PORTNAME=	podofo
PORTVERSION=	1.1.2
CATEGORIES=	graphics print

MAINTAINER=	sunpoet@FreeBSD.org
COMMENT=	PDF manipulation library and tools
WWW=		https://podofo.sourceforge.net/ \
		https://github.com/podofo/podofo

LICENSE=	LGPL20+ MPL20
LICENSE_COMB=	dual
LICENSE_FILE_LGPL20+ =	${WRKSRC}/COPYING.LGPL
LICENSE_FILE_MPL20=	${WRKSRC}/COPYING.MPL

BUILD_DEPENDS=	fast_float>=0:math/fast_float \
		date>=0:devel/date \
		libfmt>=0:devel/libfmt
LIB_DEPENDS=	libfontconfig.so:x11-fonts/fontconfig \
		libfreetype.so:print/freetype2 \
		libutf8proc.so:textproc/utf8proc

USES=		cmake compiler:c++17-lang cpe gnome localbase:ldflags pkgconfig ssl
USE_GNOME=	libxml2

CMAKE_ARGS=	-DFONTCONFIG_LIBRARIES=${LOCALBASE}/lib/libfontconfig.so \
		-DOPENSSL_INCLUDE_DIR=${OPENSSLINC} \
		-DOPENSSL_LIBRARIES=${OPENSSLLIB}
CMAKE_ON=	PODOFO_DEVENDOR_DATE \
		PODOFO_DEVENDOR_FASTFLOAT \
		PODOFO_DEVENDOR_FMT_HEADER_ONLY \
		PODOFO_DEVENDOR_UTF8PROC
CMAKE_OFF=	PODOFO_BUILD_EXAMPLES \
		PODOFO_BUILD_LIB_ONLY \
		PODOFO_BUILD_STATIC \
		PODOFO_BUILD_TEST \
		PODOFO_BUILD_UNSUPPORTED_TOOLS
CMAKE_TESTING_ON=	PODOFO_BUILD_TEST
USE_LDCONFIG=	yes

PLIST_SUB=	PORTVERSION=${PORTVERSION}

USE_GITHUB=	yes

CPE_VENDOR=	podofo_project

OPTIONS_DEFINE=	JPEG PNG TIFF
OPTIONS_DEFAULT=JPEG PNG TIFF

JPEG_CMAKE_BOOL=	WANT_LIBJPEG
JPEG_USES=		jpeg
PNG_CMAKE_BOOL=		WANT_PNG
PNG_LIB_DEPENDS=	libpng.so:graphics/png
TIFF_CMAKE_BOOL=	WANT_TIFF
TIFF_LIB_DEPENDS=	libtiff.so:graphics/tiff

# Clean up bundled libraries
.if !defined(MAINTAINER_MODE)
EXTRACT_AFTER_ARGS=	--exclude ${GH_PROJECT_DEFAULT}-${GH_TAGNAME_EXTRACT}/3rdparty/date \
			--exclude ${GH_PROJECT_DEFAULT}-${GH_TAGNAME_EXTRACT}/3rdparty/fastfloat \
			--exclude ${GH_PROJECT_DEFAULT}-${GH_TAGNAME_EXTRACT}/3rdparty/fmtlib \
			--exclude ${GH_PROJECT_DEFAULT}-${GH_TAGNAME_EXTRACT}/3rdparty/utf8proc \
			--no-same-owner --no-same-permissions
.else
post-patch:
	@${RM} -r ${WRKSRC}/3rdparty/date/
	@${RM} -r ${WRKSRC}/3rdparty/fastfloat/
	@${RM} -r ${WRKSRC}/3rdparty/fmtlib/
	@${RM} -r ${WRKSRC}/3rdparty/utf8proc/
.endif

.include <bsd.port.mk>
