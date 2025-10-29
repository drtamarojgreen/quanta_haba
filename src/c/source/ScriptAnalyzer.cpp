#include "../include/ScriptAnalyzer.h"
#include <regex>
#include <sstream>

std::vector<Symbol> findSymbols(const std::string& scriptContent) {
    std::vector<Symbol> symbols;
    std::regex functionRegex(R"(function\s+([a-zA-Z0-9_]+)\s*\()");
    std::regex varRegex(R"((?:var|let|const)\s+([a-zA-Z0-9_]+))");

    std::stringstream ss(scriptContent);
    std::string line;
    int lineNum = 1;

    while (std::getline(ss, line)) {
        std::smatch match;
        if (std::regex_search(line, match, functionRegex)) {
            symbols.push_back({match[1], "function", lineNum});
        }
        if (std::regex_search(line, match, varRegex)) {
            symbols.push_back({match[1], "variable", lineNum});
        }
        lineNum++;
    }

    return symbols;
}

std::vector<Todo> findTodos(const std::string& scriptContent) {
    std::vector<Todo> todos;
    std::regex todoRegex(R"(\/\/\s*TODO:\s*(.*))");

    std::stringstream ss(scriptContent);
    std::string line;
    int lineNum = 1;

    while (std::getline(ss, line)) {
        std::smatch match;
        if (std::regex_search(line, match, todoRegex)) {
            todos.push_back({match[1], lineNum});
        }
        lineNum++;
    }

    return todos;
}
