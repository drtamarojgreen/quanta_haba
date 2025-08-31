cmake_minimum_required(VERSION 3.16)
project(HabaCliTool VERSION 1.0)

# Set the C++ standard to C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Define the executable target and list its source files
add_executable(haba-converter
    src/c/main.cpp
    src/c/HabaParser.cpp
)

# Add the 'src/c' directory to the include path
target_include_directories(haba-converter PRIVATE
    "${PROJECT_SOURCE_DIR}/src/c"
)

# A message to the user on how to build
message(STATUS "--------------------------------------------------")
message(STATUS "Haba CLI Tool build instructions:")
message(STATUS "1. Install CMake and a C++ compiler.")
message(STATUS "2. Run the following commands from the 'cpp_editor' directory:")
message(STATUS "   mkdir build")
message(STATUS "   cd build")
message(STATUS "   cmake ..")
message(STATUS "   cmake --build .")
message(STATUS "--------------------------------------------------")
