#include <iostream>
#include <map>
#include <string>
#include <fstream>
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

void write_checkout(const std::string& key, const std::string& value) {
    std::ofstream out("tests/sorrel/sdd/checkouts/gui_parity.checkout", std::ios::app);
    out << key << " = " << value << std::endl;
}

/**
 * @Card: deep_python_gui_evaluation
 * @Is gui_interface_structure_parity_required == true
 * @Results deep_python_gui_operational == true
 */
void deep_python_gui_card(const std::map<std::string, std::string>& facts) {
    std::ifstream display_src("src/p/display.py");
    std::string display_content((std::istreambuf_iterator<char>(display_src)), std::istreambuf_iterator<char>());

    bool has_preview = display_content.find("WYSIWYG Preview") != std::string::npos;
    bool has_symbol = display_content.find("Symbol Outline") != std::string::npos;
    bool has_todo = display_content.find("TODO Explorer") != std::string::npos;
    bool has_task = display_content.find("Actionable Tasks") != std::string::npos;

    write_checkout("python_gui_tabs", (has_preview ? "Preview " : "") + (has_symbol ? "Symbols " : "") + (has_todo ? "TODOs " : "") + (has_task ? "Tasks" : ""));
    write_checkout("python_gui_notebook_usage", display_content.find("ttk.Notebook") != std::string::npos ? "Verified" : "Missing");

    bool operational = has_preview && has_symbol && has_todo && has_task;
    std::cout << "deep_python_gui_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("gui_parity.facts");
    std::cout << "[SDD Card: deep_python_gui_evaluation]" << std::endl;
    deep_python_gui_card(facts);
    return 0;
}
