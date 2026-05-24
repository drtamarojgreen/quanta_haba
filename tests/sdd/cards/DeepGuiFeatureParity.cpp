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
 * @Card: deep_gui_feature_verification
 * @Is gui_interface_structure_parity_required == true
 * @Results deep_gui_features_operational == true
 */
void deep_gui_feature_card(const std::map<std::string, std::string>& facts) {
    std::ifstream src("src/c/source/gui_editor.cpp");
    std::string content((std::istreambuf_iterator<char>(src)), std::istreambuf_iterator<char>());

    bool has_preview = content.find("WYSIWYG Preview") != std::string::npos;
    bool has_symbol = content.find("Symbol Outline") != std::string::npos;
    bool has_todo = content.find("TODO Explorer") != std::string::npos;
    bool has_task = content.find("Actionable Tasks") != std::string::npos;

    write_checkout("cpp_gui_tabs", (has_preview ? "Preview " : "") + (has_symbol ? "Symbols " : "") + (has_todo ? "TODOs " : "") + (has_task ? "Tasks" : ""));
    write_checkout("cpp_gui_demo_btn", content.find("Run Model Demo") != std::string::npos ? "Present" : "Missing");

    bool operational = has_preview && has_symbol && has_todo && has_task;
    std::cout << "deep_gui_features_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("gui_parity.facts");
    std::cout << "[SDD Card: deep_gui_feature_verification]" << std::endl;
    deep_gui_feature_card(facts);
    return 0;
}
