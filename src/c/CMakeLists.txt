cmake_minimum_required(VERSION 3.16)
project(HabaCliTool VERSION 1.0)

# Set the C++ standard to C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Define the executable target and list its source files
add_executable(cli_editor
    source/cli_editor.cpp
)

add_executable(gui_editor
    source/gui_editor.cpp
)

add_executable(haba-converter
    source/main.cpp
    source/HabaParser.cpp
)

# Add the include directory to the include path
target_include_directories(cli_editor PRIVATE
    include
)

target_include_directories(haba-converter PRIVATE
    include
)

# Enable testing with CTest
enable_testing()

# Create a test executable
add_executable(run_tests_cmake
    ../../tests/c/test_haba_parser.cpp
    source/HabaParser.cpp
)

# Link include directories to the test executable
target_include_directories(run_tests_cmake PRIVATE
    include
    ../../tests/c/
)

# Add a test to be run by CTest
add_test(NAME HabaParserTest COMMAND run_tests_cmake)

# A message to the user on how to build
message(STATUS "--------------------------------------------------")
message(STATUS "Haba CLI Tool build instructions:")
message(STATUS "1. Install CMake and a C++ compiler.")
message(STATUS "2. Run the following commands from the 'src/c' directory:")
message(STATUS "   mkdir build")
message(STATUS "   cd build")
message(STATUS "   cmake ..")
message(STATUS "   cmake --build .")
message(STATUS "--------------------------------------------------")
