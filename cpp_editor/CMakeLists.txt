cmake_minimum_required(VERSION 3.16)
project(HabaEditor VERSION 1.0)

# Set the C++ standard to C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Automatically handle Qt's meta-object compiler (moc), resource compiler (rcc), and UI compiler (uic)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# Find the required Qt packages
find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets WebEngineCore WebEngineWidgets)

# Define the executable target and list its source files
add_executable(HabaEditor
    src/main.cpp
    src/MainWindow.cpp
    src/HabaParser.cpp
)

# Link the executable to the Qt libraries
target_link_libraries(HabaEditor PRIVATE
    Qt::Core
    Qt::Gui
    Qt::Widgets
    Qt::WebEngineCore
    Qt::WebEngineWidgets
)

# Add the 'include' directory to the include path
target_include_directories(HabaEditor PRIVATE
    "${PROJECT_SOURCE_DIR}/include"
)

# A message to the user on how to build
message(STATUS "--------------------------------------------------")
message(STATUS "HabaEditor build instructions:")
message(STATUS "1. Install CMake and a C++ compiler.")
message(STATUS "2. Install the Qt 6 development libraries (including WebEngine).")
message(STATUS "3. Run the following commands from the 'cpp_editor' directory:")
message(STATUS "   mkdir build")
message(STATUS "   cd build")
message(STATUS "   cmake ..")
message(STATUS "   cmake --build .")
message(STATUS "--------------------------------------------------")
