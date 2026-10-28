PORTNAME=	libclc
DISTVERSION=	${DISTVERSION_${FLAVOR}}
DISTVERSION_llvm23=	23.1.4
DISTVERSION_llvm22=	22.1.5
DISTVERSION_llvm21=	21.1.8
DISTVERSION_llvm20=	20.1.8
DISTVERSION_llvm19=	19.1.7
DISTVERSION_llvm18=	18.1.8
DISTVERSION_llvm17=	17.0.6
DISTVERSION_llvm16=	16.0.6
CATEGORIES=	devel
MASTER_SITES=	https://github.com/llvm/llvm-project/releases/download/llvmorg-${DISTVERSION}/
DISTNAME=	libclc-${DISTVERSION}.src
PKGNAMESUFFIX=	-${FLAVOR}

MAINTAINER=	x11@FreeBSD.org
COMMENT=	Required library functions for OpenCL C programming language
WWW=		https://libclc.llvm.org/

LICENSE=	LLVM
LICENSE_FILE=	${WRKSRC}/LICENSE.TXT
LICENSE_NAME=	Apache License 2.0 with LLVM Exceptions
LICENSE_PERMS=	dist-mirror dist-sell pkg-mirror pkg-sell auto-accept

BUILD_DEPENDS=	spirv-llvm-translator-${FLAVOR}>0:devel/spirv-llvm-translator@${FLAVOR} \
		libedit>=0:devel/libedit

FLAVORS=	${16 17 18 19 20 21 22 23:L:S/^/llvm/}

USES=		cmake compiler:c++11-lib llvm:${FLAVOR:S/llvm//},build python:build tar:xz
USE_LDCONFIG=	${PREFIX}/${FLAVOR}/lib

BINARY_ALIAS=	python=${PYTHON_CMD}
CMAKE_ARGS+=	-DLLVM_DIR:PATH="${LOCALBASE}/${FLAVOR}" \
		-DCMAKE_PREFIX_PATH="${LOCALBASE}/${FLAVOR}"
CMAKE_INSTALL_PREFIX=		${PREFIX}/${FLAVOR}
DISTINFO_FILE=	${.CURDIR}/distinfo.${FLAVOR}
NO_ARCH=	yes

.if !empty(FLAVOR:Mllvm2[3-9])
LIBCLC_TRIPLES=	amdgcn-- amdgcn-amd-amdhsa amdgcn-mesa-mesa3d nvptx64-- \
		nvptx64--nvidiacl nvptx64-nvidia-cuda spirv32-unknown-unknown \
		spirv64-unknown-unknown spirv64-unknown-vulkan
CMAKE_ARGS+=	-DCMAKE_AR:FILEPATH="${LOCALBASE}/${FLAVOR}/bin/llvm-ar" \
		-DCMAKE_RANLIB:FILEPATH="${LOCALBASE}/${FLAVOR}/bin/llvm-ranlib"

do-configure:
.  for t in ${LIBCLC_TRIPLES}
	${MKDIR} ${WRKDIR}/.build-${t}
	@cd ${WRKDIR}/.build-${t}; ${SETENVI} ${WRK_ENV} ${CONFIGURE_ENV} ${CMAKE_BIN} \
		${CMAKE_ARGS} -DLLVM_DEFAULT_TARGET_TRIPLE=${t} ${CMAKE_SOURCE_PATH}
.  endfor

do-build:
.  for t in ${LIBCLC_TRIPLES}
	@cd ${WRKDIR}/.build-${t}; ${DO_MAKE_BUILD} ${ALL_TARGET}
.  endfor

do-install:
.  for t in ${LIBCLC_TRIPLES}
	@cd ${WRKDIR}/.build-${t}; ${SETENVI} ${WRK_ENV} ${MAKE_ENV} ${FAKEROOT} \
		${MAKE_CMD} ${MAKE_FLAGS} ${MAKEFILE} ${MAKE_ARGS} ${INSTALL_TARGET}
.  endfor
.endif

.include <bsd.port.pre.mk>

.if ${FLAVOR:S/llvm//} >= 22
DISTNAME=	llvm-project-${DISTVERSION}.src
WRKSRC_SUBDIR=	libclc
.endif

.for i in ${FLAVORS:S/llvm//}
.if ${FLAVOR:S/llvm//} >= ${i}
PLIST_SUB+=	LLVM_GE${i}="" LLVM_LT${i}="@comment "
.else
PLIST_SUB+=	LLVM_GE${i}="@comment " LLVM_LT${i}=""
.endif
.endfor
PLIST_SUB+=	LLVM_VERSION=${FLAVOR}

.if ${FLAVOR:S/llvm//} < 23
post-patch:
	@${REINPLACE_CMD} \
		's,$${CMAKE_INSTALL_DATADIR}/pkgconfig,$${CMAKE_INSTALL_PREFIX}/libdata/pkgconfig,' \
		${WRKSRC}/CMakeLists.txt
.endif

.include <bsd.port.post.mk>
