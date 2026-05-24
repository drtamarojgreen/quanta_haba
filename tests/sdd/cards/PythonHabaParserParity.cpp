#include <iostream>
#include <map>
#include <string>
#include <fstream>
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

void write_checkout(const std::string& key, const std::string& value) {
    std::ofstream out("tests/sorrel/sdd/checkouts/parser_parity.checkout", std::ios::app);
    out << key << " = " << value << std::endl;
}

/**
 * @Card: python_haba_parser_parity_verification
 * @Is json_serialization_parity_required == true
 * @Results python_haba_parser_parity_operational == true
 */
void python_haba_parser_parity_card(const std::map<std::string, std::string>& facts) {
    std::ifstream src("src/p/haba_parser.py");
    std::string content((std::istreambuf_iterator<char>(src)), std::istreambuf_iterator<char>());

    bool has_to_json = content.find("def to_json") != std::string::npos;
    bool has_from_json = content.find("def from_json") != std::string::npos;

    write_checkout("python_parser_methods_raw", (has_to_json ? "to_json " : "") + (has_from_json ? "from_json" : ""));

    bool operational = has_to_json && has_from_json;
    std::cout << "python_haba_parser_parity_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("parser_parity.facts");
    std::cout << "[SDD Card: python_haba_parser_parity_verification]" << std::endl;
    python_haba_parser_parity_card(facts);
    return 0;
}
