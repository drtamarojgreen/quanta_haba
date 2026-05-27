#ifndef SCRIPT_ANALYZER_H
#define SCRIPT_ANALYZER_H

#include <string>
#include <vector>

struct Symbol {
    std::string name;
    std::string type;
    int line;
};

struct Todo {
    std::string text;
    int line;
};

std::vector<Symbol> findSymbols(const std::string& scriptContent);
std::vector<Todo> findTodos(const std::string& scriptContent);

#endif // SCRIPT_ANALYZER_H
