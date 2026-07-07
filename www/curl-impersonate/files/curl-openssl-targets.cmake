# Injected into the curl subproject via CMAKE_PROJECT_CURL_INCLUDE, i.e. right
# after project() and before find_package(OpenSSL). CMake's FindOpenSSL does not
# create the OpenSSL:: imported targets for a static BoringSSL on FreeBSD (the
# version string parses empty), so curl's target_link_libraries(OpenSSL::SSL)
# fails. Define the targets here from the paths the superbuild already passes.
if(DEFINED OPENSSL_CRYPTO_LIBRARY AND NOT TARGET OpenSSL::Crypto)
  add_library(OpenSSL::Crypto STATIC IMPORTED)
  set_target_properties(OpenSSL::Crypto PROPERTIES
    IMPORTED_LOCATION "${OPENSSL_CRYPTO_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES "${OPENSSL_INCLUDE_DIR}")
endif()
if(DEFINED OPENSSL_SSL_LIBRARY AND NOT TARGET OpenSSL::SSL)
  add_library(OpenSSL::SSL STATIC IMPORTED)
  set_target_properties(OpenSSL::SSL PROPERTIES
    IMPORTED_LOCATION "${OPENSSL_SSL_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES "${OPENSSL_INCLUDE_DIR}"
    INTERFACE_LINK_LIBRARIES OpenSSL::Crypto)
endif()
