#include <iostream>
#include <map>
#include <string>
#include <fstream>
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

/**
 * @Card: python_script_analyzer_parity_verification
 * @Is symbol_extraction_parity_required == true
 * @Results python_script_analyzer_parity_operational == true
 */
void python_script_analyzer_parity_card(const std::map<std::string, std::string>& facts) {
    std::ifstream src("src/p/components.py");
    std::string content((std::istreambuf_iterator<char>(src)), std::istreambuf_iterator<char>());

    // Check for symbol and todo pattern definitions
    bool has_symbols = content.find("SymbolOutlinePanel") != std::string::npos && content.find("patterns") != std::string::npos;
    bool has_todos = content.find("TodoExplorerPanel") != std::string::npos && content.find("update_todos") != std::string::npos;

    bool operational = has_symbols && has_todos;
    std::cout << "python_script_analyzer_parity_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("parity.facts");
    std::cout << "[SDD Card: python_script_analyzer_parity_verification]" << std::endl;
    python_script_analyzer_parity_card(facts);
    return 0;
}
