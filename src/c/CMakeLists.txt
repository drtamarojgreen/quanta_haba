cmake_minimum_required(VERSION 3.16)
project(HabaCliTool VERSION 1.0)

# Set the C++ standard to C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Define the executable target and list its source files
add_executable(cli_editor
    editor/cli_editor.cpp
    editor/EditorLogic.cpp
    parser/HabaParser.cpp
    export/html_generator.cpp
    core/StringUtils.cpp
)

add_executable(gui_editor
    editor/gui_editor.cpp
    editor/EditorLogic.cpp
    parser/HabaParser.cpp
    export/html_generator.cpp
    core/StringUtils.cpp
    network/OAuthClient.cpp
    parser/ScriptAnalyzer.cpp
    core/ConfigManager.cpp
)

add_executable(haba-converter
    export/main.cpp
    parser/HabaParser.cpp
    export/html_generator.cpp
    core/StringUtils.cpp
)

add_executable(sorrel
    sorrel/sorrel_cli.cpp
)

# Set include directories for all targets
set(PACKAGE_INCLUDES
    core
    parser
    editor
    network
    export
    sorrel
)

target_include_directories(cli_editor PRIVATE ${PACKAGE_INCLUDES})
target_include_directories(gui_editor PRIVATE ${PACKAGE_INCLUDES})
target_include_directories(haba-converter PRIVATE ${PACKAGE_INCLUDES})
target_include_directories(sorrel PRIVATE ${PACKAGE_INCLUDES})

# Enable testing with CTest
enable_testing()

# Create a test executable
add_executable(run_tests_cmake
    ../../tests/c/main.cpp
    ../../tests/c/test_haba_parser.cpp
    ../../tests/c/test_script_analyzer.cpp
    ../../tests/c/test_config_manager.cpp
    ../../tests/c/test_html_generator.cpp
    ../../tests/c/test_cli_logic.cpp
    ../../tests/c/test_parser_build.cpp
    ../../tests/c/test_gui_logic.cpp
    ../../tests/data/test_logging.cpp
    parser/HabaParser.cpp
    parser/ScriptAnalyzer.cpp
    core/ConfigManager.cpp
    network/OAuthClient.cpp
    export/html_generator.cpp
    editor/EditorLogic.cpp
    core/StringUtils.cpp
)

# Link include directories to the test executable
target_include_directories(run_tests_cmake PRIVATE
    ${PACKAGE_INCLUDES}
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
