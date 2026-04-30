#include <iostream>
#include <map>
#include "ScriptAnalyzer.h"
#include "../cpp/util/fact_utils.h"

using namespace Chai::Cdd::Util;

/**
 * @Card: script_analyzer_extraction_verification
 * @Is todo_detection_operational == true
 * @Results script_analyzer_extraction_operational == true
 */
void script_analyzer_extraction_card(const std::map<std::string, std::string>& facts) {
    std::string script = "function test() { /* logic */ }\n// TODO: Implement CDD";

    auto symbols = findSymbols(script);
    auto todos = findTodos(script);

    bool has_symbol = !symbols.empty() && symbols[0].name == "test";
    bool has_todo = !todos.empty() && todos[0].text == "Implement CDD";

    bool operational = has_symbol && has_todo;

    std::cout << "script_analyzer_extraction_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("script_analyzer.facts");

    std::cout << "[CDD Card: script_analyzer_extraction_verification]" << std::endl;
    script_analyzer_extraction_card(facts);

    return 0;
}
