PORTNAME=	curl-impersonate
DISTVERSIONPREFIX=	v
DISTVERSION=	2.0.0a5
CATEGORIES=	www
MASTER_SITES+=	https://github.com/nghttp2/nghttp2/releases/download/v${NGHTTP2_VERSION}/:dep \
		https://github.com/ngtcp2/ngtcp2/releases/download/v${NGTCP2_VERSION}/:dep \
		https://github.com/ngtcp2/nghttp3/releases/download/v${NGHTTP3_VERSION}/:dep \
		https://codeload.github.com/google/boringssl/zip/${BORING_SSL_COMMIT}?dummy=/:dep \
		https://codeload.github.com/curl/curl/tar.gz/refs/tags/${CURL_VERSION}?dummy=/:dep
DISTFILES+=	nghttp2-${NGHTTP2_VERSION}.tar.bz2:dep \
		ngtcp2-${NGTCP2_VERSION}.tar.bz2:dep \
		nghttp3-${NGHTTP3_VERSION}.tar.bz2:dep \
		boringssl-${BORING_SSL_COMMIT}.zip:dep \
		curl-${CURL_VERSION}.tar.gz:dep
DIST_SUBDIR=	${PORTNAME}
EXTRACT_ONLY=	${GH_ACCOUNT}-${PORTNAME}-${DISTVERSIONFULL}_GH0${EXTRACT_SUFX}

MAINTAINER=	ports@FreeBSD.org
COMMENT=	Curl fork that impersonates browser TLS/JA3/HTTP2 fingerprints
WWW=		https://github.com/lexiforest/curl-impersonate

LICENSE=	MIT
LICENSE_FILE=	${WRKSRC}/LICENSE

ONLY_FOR_ARCHS=	aarch64 amd64

LIB_DEPENDS=	libbrotlidec.so:archivers/brotli \
		libzstd.so:archivers/zstd
RUN_DEPENDS=	bash:shells/bash

USES=		cmake go:no_targets localbase pkgconfig
USE_GITHUB=	yes
GH_ACCOUNT=	lexiforest
USE_LDCONFIG=	yes

PLIST_SUB=	CURL_SO_VER=4.8.0

BORING_SSL_COMMIT=	673e61fc215b178a90c0e67858bbf162c8158993
NGHTTP2_VERSION=	1.63.0
NGTCP2_VERSION=		1.20.0
NGHTTP3_VERSION=	1.15.0
CURL_VERSION=		curl-8_15_0

_DEP_ARCHIVES=	nghttp2-${NGHTTP2_VERSION}.tar.bz2 \
		ngtcp2-${NGTCP2_VERSION}.tar.bz2 \
		nghttp3-${NGHTTP3_VERSION}.tar.bz2 \
		boringssl-${BORING_SSL_COMMIT}.zip curl-${CURL_VERSION}.tar.gz

post-extract:
	@${MKDIR} ${WRKSRC}/_dist
.for f in ${_DEP_ARCHIVES}
	@${CP} ${DISTDIR}/${DIST_SUBDIR}/${f} ${WRKSRC}/_dist/${f}
.endfor
	@${CP} ${FILESDIR}/curl-openssl-targets.cmake ${WRKSRC}/curl-openssl-targets.cmake

do-build:
	@cd ${BUILD_WRKSRC} && ${SETENV} ${MAKE_ENV} DESTDIR="" \
		${CMAKE_BIN} --build . -j ${MAKE_JOBS_NUMBER}

post-install:
	@${RM} -r ${STAGEDIR}${PREFIX}/lib/CMakeFiles

.include <bsd.port.mk>
