cmake_minimum_required(VERSION 3.20)
project(QuantumDispatchGUI LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets Network Charts)

include_directories(gui/include)

set(SOURCES
    gui/src/main.cpp
    gui/src/main_window.cpp
    gui/src/auth_dialog.cpp
    gui/src/cloud_sync.cpp
    gui/src/local_runner.cpp
)

set(HEADERS
    gui/include/main_window.hpp
    gui/include/auth_dialog.hpp
    gui/include/cloud_sync.hpp
    gui/include/local_runner.hpp
)

add_executable(quantum_dispatch_gui ${SOURCES} ${HEADERS})

target_link_libraries(quantum_dispatch_gui PRIVATE
    Qt6::Core
    Qt6::Gui
    Qt6::Widgets
    Qt6::Network
    Qt6::Charts
)