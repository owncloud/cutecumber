# SPDX-FileCopyrightText: 2026 ownCloud GmbH - A Kiteworks Company and ownCloud contributors
# SPDX-License-Identifier: MIT

function(cutecumber_add_test name)
    add_executable(${name} ${name}.cpp)
    cutecumber_apply_settings(${name})
    target_link_libraries(${name} PRIVATE cutecumber_probe Qt6::Test)
    add_test(NAME cutecumber-${name} COMMAND ${name})
    set_tests_properties(cutecumber-${name} PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen")
endfunction()

cutecumber_add_test(tst_protocol)
cutecumber_add_test(tst_startup)
cutecumber_add_test(tst_selector)
cutecumber_add_test(tst_items)
# tst_quick.qml imports QtQuick.Controls, which a Qt without Qt Quick Controls lacks at run time
find_package(Qt6 QUIET COMPONENTS QuickControls2)
if(Qt6QuickControls2_FOUND)
    cutecumber_add_test(tst_quick)
    qt_add_resources(tst_quick tst_quick_qml PREFIX "/" FILES tst_quick.qml)
    # Qt Quick renders without a GPU under the offscreen platform; the Basic style looks the same everywhere
    set_tests_properties(cutecumber-tst_quick PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software;QT_QUICK_CONTROLS_STYLE=Basic")
else()
    message(WARNING "Qt Quick Controls not found: skipping the probe test tst_quick")
endif()
cutecumber_add_test(tst_actions)
qt_add_resources(tst_actions tst_actions_qml PREFIX "/" FILES tst_actions.qml)
set_tests_properties(cutecumber-tst_actions PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software")
