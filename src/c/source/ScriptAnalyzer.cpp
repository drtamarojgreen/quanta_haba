#include "../include/ScriptAnalyzer.h"
#include <regex>
#include <sstream>
#include <iterator>

std::vector<Symbol> findSymbols(const std::string& scriptContent) {
    std::vector<Symbol> symbols;
    // Combined regex to find all symbol types at once.
    std::regex symbolRegex(R"(function\s+([a-zA-Z0-9_]+)\s*\(|(?:var|let|const)\s+([a-zA-Z0-9_]+))");

    std::stringstream ss(scriptContent);
    std::string line;
    int lineNum = 1;

    while (std::getline(ss, line)) {
        // Use sregex_iterator to find all non-overlapping matches in the line.
        auto matches_begin = std::sregex_iterator(line.begin(), line.end(), symbolRegex);
        auto matches_end = std::sregex_iterator();

        for (std::sregex_iterator i = matches_begin; i != matches_end; ++i) {
            const std::smatch& match = *i;
            // The first submatch is the function name, the second is the variable name.
            // One of them will be empty for each match.
            if (match[1].matched) {
                symbols.push_back({match[1].str(), "function", lineNum});
            } else if (match[2].matched) {
                symbols.push_back({match[2].str(), "variable", lineNum});
            }
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
        auto matches_begin = std::sregex_iterator(line.begin(), line.end(), todoRegex);
        auto matches_end = std::sregex_iterator();

        for (std::sregex_iterator i = matches_begin; i != matches_end; ++i) {
            const std::smatch& match = *i;
            todos.push_back({match[1].str(), lineNum});
        }
        lineNum++;
    }
    return todos;
}
