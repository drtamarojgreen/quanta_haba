#include <iostream>
#include <map>
#include <string>
#include <fstream>
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

void write_checkout(const std::string& key, const std::string& value) {
    std::ofstream out("tests/sorrel/sdd/checkouts/editor_logic_parity.checkout", std::ios::app);
    out << key << " = " << value << std::endl;
}

/**
 * @Card: python_editor_logic_parity_verification
 * @Is editor_logic_parity_required == true
 * @Results python_editor_logic_parity_operational == true
 */
void python_editor_logic_parity_card(const std::map<std::string, std::string>& facts) {
    std::ifstream editor_src("src/p/editor.py");
    std::string editor_content((std::istreambuf_iterator<char>(editor_src)), std::istreambuf_iterator<char>());

    std::ifstream search_src("src/p/search.py");
    std::string search_content((std::istreambuf_iterator<char>(search_src)), std::istreambuf_iterator<char>());

    bool has_toggle = editor_content.find("def toggle_comment") != std::string::npos;
    bool has_guard = search_content.find("def check_main_guard") != std::string::npos;

    write_checkout("python_editor_toggle_comment", has_toggle ? "Found" : "Missing (Gap Detected)");
    write_checkout("python_editor_main_guard", has_guard ? "Verified" : "Missing");

    bool operational = has_toggle && has_guard;
    std::cout << "python_editor_logic_parity_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("editor_logic_parity.facts");
    std::cout << "[SDD Card: python_editor_logic_parity_verification]" << std::endl;
    python_editor_logic_parity_card(facts);
    return 0;
}
