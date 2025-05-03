find_path(LIBNOISE_INCLUDE_DIR libnoise/noise.h
    HINTS
    $ENV{LIBNOISE_DIR}
    ${LIBNOISE_DIR}
    ${CMAKE_BINARY_DIR}/deps/dep_libnoise-prefix/src/dep_libnoise-build
    ${CMAKE_BINARY_DIR}/deps/dep_libnoise-prefix/src/dep_libnoise/include
    PATH_SUFFIXES include
    PATHS
    ${CMAKE_PREFIX_PATH}
    ${CMAKE_INSTALL_PREFIX}
    /usr/local
    /usr
)

find_library(LIBNOISE_LIBRARY
    NAMES noise libnoise libnoise_static
    HINTS
    $ENV{LIBNOISE_DIR}
    ${LIBNOISE_DIR}
    ${CMAKE_BINARY_DIR}/deps/dep_libnoise-prefix/src/dep_libnoise-build/Release
    ${CMAKE_BINARY_DIR}/deps/dep_libnoise-prefix/src/dep_libnoise-build/Debug
    PATH_SUFFIXES lib
    PATHS
    ${CMAKE_PREFIX_PATH}
    ${CMAKE_INSTALL_PREFIX}
    /usr/local
    /usr
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(libnoise DEFAULT_MSG LIBNOISE_INCLUDE_DIR LIBNOISE_LIBRARY)

if(LIBNOISE_FOUND AND NOT TARGET libnoise::libnoise)
    add_library(libnoise::libnoise UNKNOWN IMPORTED)
    set_target_properties(libnoise::libnoise PROPERTIES
        IMPORTED_LOCATION "${LIBNOISE_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${LIBNOISE_INCLUDE_DIR}"
    )
endif()

mark_as_advanced(LIBNOISE_INCLUDE_DIR LIBNOISE_LIBRARY) 