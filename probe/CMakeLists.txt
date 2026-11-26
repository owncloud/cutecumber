# SPDX-FileCopyrightText: 2026 ownCloud GmbH - A Kiteworks Company and ownCloud contributors
# SPDX-License-Identifier: MIT

# Builds on its own (cmake -S probe) and as a subproject of an application
# (add_subdirectory or FetchContent), which then links cutecumber::probe.
cmake_minimum_required(VERSION 3.18)
project(CutecumberProbe VERSION 0.1.0 LANGUAGES CXX)

if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    set(CUTECUMBER_STANDALONE ON)
    set(CMAKE_CXX_STANDARD 17)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
    include(CTest)
else()
    set(CUTECUMBER_STANDALONE OFF)
endif()

find_package(Qt6 6.8 REQUIRED COMPONENTS Widgets Network Test Quick QuickWidgets)

# The probe throws ProbeError internally; applications may build with -fno-exceptions.
# The definitions keep the sources clean under the strict Qt settings applications commonly use.
function(cutecumber_apply_settings target)
    set_target_properties(${target} PROPERTIES AUTOMOC ON)
    target_compile_features(${target} PUBLIC cxx_std_17)
    target_compile_options(${target} PRIVATE $<$<CXX_COMPILER_ID:GNU,Clang,AppleClang>:-fexceptions>)
    target_compile_definitions(${target}
        PRIVATE
            QT_NO_CAST_TO_ASCII
            QT_NO_CAST_FROM_ASCII
            QT_NO_URL_CAST_FROM_STRING
            QT_NO_CAST_FROM_BYTEARRAY
            QT_USE_QSTRINGBUILDER
            QT_NO_NARROWING_CONVERSIONS_IN_CONNECT
            QT_NO_KEYWORDS
            QT_NO_FOREACH
    )
endfunction()

# An OBJECT library, so the linker cannot drop the Q_COREAPP_STARTUP_FUNCTION that starts the probe.
add_library(cutecumber_probe OBJECT
    probe.cpp
    probe.h
    registry.cpp
    registry.h
    jsonvalue.cpp
    jsonvalue.h
    selector.cpp
    selector.h
    items.cpp
    items.h
    quick.cpp
    quick.h
    actions.cpp
    actions.h
    keys.cpp
    keys.h
)
add_library(cutecumber::probe ALIAS cutecumber_probe)
# Installed and exported as cutecumber::probe too
set_target_properties(cutecumber_probe PROPERTIES EXPORT_NAME probe)
cutecumber_apply_settings(cutecumber_probe)
target_include_directories(cutecumber_probe
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:include/CutecumberProbe>
)
target_link_libraries(cutecumber_probe
    PUBLIC
        Qt6::Widgets
        Qt6::Network
        Qt6::Test
        Qt6::Quick
        Qt6::QuickWidgets
)

# Only a standalone build installs the probe; an application that adds it as a subdirectory must not ship it.
if(CUTECUMBER_STANDALONE)
    include(GNUInstallDirs)
    include(CMakePackageConfigHelpers)
    set(CUTECUMBER_CMAKE_DIR ${CMAKE_INSTALL_LIBDIR}/cmake/CutecumberProbe)
    install(TARGETS cutecumber_probe EXPORT CutecumberProbeTargets OBJECTS DESTINATION ${CMAKE_INSTALL_LIBDIR}/CutecumberProbe)
    install(FILES probe.h registry.h jsonvalue.h selector.h items.h quick.h actions.h keys.h DESTINATION include/CutecumberProbe)
    install(EXPORT CutecumberProbeTargets NAMESPACE cutecumber:: DESTINATION ${CUTECUMBER_CMAKE_DIR})
    configure_package_config_file(CutecumberProbeConfig.cmake.in ${CMAKE_CURRENT_BINARY_DIR}/CutecumberProbeConfig.cmake
        INSTALL_DESTINATION ${CUTECUMBER_CMAKE_DIR}
    )
    # 0.x: a minor version may break compatibility, so only the same minor version matches
    write_basic_package_version_file(${CMAKE_CURRENT_BINARY_DIR}/CutecumberProbeConfigVersion.cmake
        COMPATIBILITY SameMinorVersion
    )
    install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/CutecumberProbeConfig.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/CutecumberProbeConfigVersion.cmake
        DESTINATION ${CUTECUMBER_CMAKE_DIR}
    )
endif()

# The probe's own tests build by default only when the probe is the top-level project and BUILD_TESTING (from
# CTest) is on. An application that wants them sets CUTECUMBER_BUILD_TESTS=ON and runs them with:
# ctest --test-dir <build>/<path to probe>
if(CUTECUMBER_STANDALONE AND BUILD_TESTING)
    set(CUTECUMBER_BUILD_TESTS_DEFAULT ON)
else()
    set(CUTECUMBER_BUILD_TESTS_DEFAULT OFF)
endif()
option(CUTECUMBER_BUILD_TESTS "Build the probe's tests" ${CUTECUMBER_BUILD_TESTS_DEFAULT})
if(CUTECUMBER_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()
