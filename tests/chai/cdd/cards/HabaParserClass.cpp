#include <iostream>
#include <map>
#include "HabaParser.h"
#include "../cpp/util/fact_utils.h"

using namespace Chai::Cdd::Util;

/**
 * @Card: haba_parser_multiline_verification
 * @Is multi_line_content_supported == true
 * @Results haba_parser_multiline_operational == true
 */
void haba_parser_multiline_card(const std::map<std::string, std::string>& facts) {
    HabaParser parser;
    std::string raw_text =
        "<content_layer>\n"
        "Line 1\n"
        "Line 2\n"
        "</content_layer>";

    HabaData data = parser.parse(raw_text);

    bool operational = (data.content.find("Line 1") != std::string::npos &&
                        data.content.find("Line 2") != std::string::npos);

    std::cout << "haba_parser_multiline_operational = " << (operational ? "true" : "false") << std::endl;
}

/**
 * @Card: haba_parser_empty_input_verification
 * @Results haba_parser_empty_input_handled == true
 */
void haba_parser_empty_input_card() {
    HabaParser parser;
    HabaData data = parser.parse("");

    bool handled = (data.content.empty() && data.presentation_items.empty() && data.script.empty());

    std::cout << "haba_parser_empty_input_handled = " << (handled ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("haba_parser.facts");

    std::cout << "[CDD Card: haba_parser_multiline_verification]" << std::endl;
    haba_parser_multiline_card(facts);

    std::cout << "[CDD Card: haba_parser_empty_input_verification]" << std::endl;
    haba_parser_empty_input_card();

    return 0;
}
