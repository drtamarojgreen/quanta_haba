#include "simple_test_framework.h"
#include "ScriptAnalyzer.h"

bool ScriptAnalyzerTest_FindSymbols_FunctionsAndVariables() {
    std::string script = "function myFunc() { const x = 1; } var anotherVar = 2;";
    auto symbols = findSymbols(script);
    ASSERT_EQ(size_t(2), symbols.size());
    ASSERT_EQ(std::string("myFunc"), symbols[0].name);
    ASSERT_EQ(std::string("function"), symbols[0].type);
    ASSERT_EQ(std::string("anotherVar"), symbols[1].name);
    ASSERT_EQ(std::string("variable"), symbols[1].type);
    return true;
}

bool ScriptAnalyzerTest_FindTodos_SingleAndMultiLine() {
    std::string script = "// TODO: Fix this\n// Another line\n//TODO:Implement that";
    auto todos = findTodos(script);
    ASSERT_EQ(size_t(2), todos.size());
    ASSERT_EQ(std::string("Fix this"), todos[0].text);
    ASSERT_EQ(std::string("Implement that"), todos[1].text);
    return true;
}

bool ScriptAnalyzerTest_NoSymbolsOrTodos() {
    std::string script = "console.log('Hello');";
    auto symbols = findSymbols(script);
    auto todos = findTodos(script);
    ASSERT_EQ(size_t(0), symbols.size());
    ASSERT_EQ(size_t(0), todos.size());
    return true;
}


// Register tests
struct TestRegistrar_ScriptAnalyzer {
    TestRegistrar_ScriptAnalyzer() {
        add_test_case("ScriptAnalyzerTest_FindSymbols_FunctionsAndVariables", ScriptAnalyzerTest_FindSymbols_FunctionsAndVariables);
        add_test_case("ScriptAnalyzerTest_FindTodos_SingleAndMultiLine", ScriptAnalyzerTest_FindTodos_SingleAndMultiLine);
        add_test_case("ScriptAnalyzerTest_NoSymbolsOrTodos", ScriptAnalyzerTest_NoSymbolsOrTodos);
    }
};

static TestRegistrar_ScriptAnalyzer registrar_instance_script;
