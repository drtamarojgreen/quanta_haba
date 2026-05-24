#include <iostream>
#include <map>
#include <string>
#include <fstream>
#include "EditorLogic.h"
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

void write_checkout(const std::string& key, const std::string& value) {
    std::ofstream out("tests/sorrel/sdd/checkouts/editor_logic_parity.checkout", std::ios::app);
    out << key << " = " << value << std::endl;
}

/**
 * @Card: editor_logic_toggle_comment_verification
 * @Is editor_logic_parity_required == true
 * @Results editor_logic_toggle_comment_operational == true
 */
void editor_logic_toggle_comment_card(const std::map<std::string, std::string>& facts) {
    EditorState state;
    state.lines = {"code"};
    state.cursor_line = 0;
    toggle_comment(state);
    bool ok = (state.lines[0] == "//code");
    write_checkout("cpp_editor_toggle_comment", ok ? "Verified" : "Failed");
    std::cout << "editor_logic_toggle_comment_operational = " << (ok ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("editor_logic_parity.facts");
    std::cout << "[SDD Card: editor_logic_toggle_comment_verification]" << std::endl;
    editor_logic_toggle_comment_card(facts);
    return 0;
}
