#include "simple_test_framework.h"
#include "EditorLogic.h"
#include <string>
#include <vector>

bool CliLogicTest_ToggleComment() {
    EditorState state;
    state.lines = {"  int x = 0;", "//  int y = 1;"};

    state.cursor_line = 0;
    toggle_comment(state);
    ASSERT_EQ(std::string("//  int x = 0;"), state.lines[0]);

    toggle_comment(state);
    ASSERT_EQ(std::string("  int x = 0;"), state.lines[0]);

    state.cursor_line = 1;
    toggle_comment(state);
    ASSERT_EQ(std::string("  int y = 1;"), state.lines[1]);

    return true;
}

bool CliLogicTest_GenerateGuardSymbol() {
    ASSERT_EQ(std::string("INCLUDE_HABA_H"), generate_guard_symbol("include/haba.h"));
    ASSERT_EQ(std::string("SRC_MAIN_HPP"), generate_guard_symbol("src/main.hpp"));
    ASSERT_EQ(std::string("MY_FILE_H"), generate_guard_symbol("my-file.h"));
    return true;
}

// Register tests
struct CliLogicRegistrar {
    CliLogicRegistrar() {
        add_test_case("CliLogicTest_ToggleComment", CliLogicTest_ToggleComment);
        add_test_case("CliLogicTest_GenerateGuardSymbol", CliLogicTest_GenerateGuardSymbol);
    }
};

static CliLogicRegistrar cli_logic_registrar;
