#include "simple_test_framework.h"
#include <fstream>
#include <string>
#include <map>
#include <cstdio>

// Forward declarations of functions to test (since they are in cli_editor.cpp)
// In a real project, these should be moved to a library or separate logic file.
extern std::map<std::string, std::string> quanta_config;
void load_quanta_config();
std::string call_quanta_model(const std::string& task);

bool LocalModelTest_LoadConfig() {
    // Create a temporary .quanta file
    {
        std::ofstream f(".quanta");
        f << "# Comment line\n";
        f << "engine.model_path = test_model.gguf\n";
        f << "model.llama_cli_path = test_cli\n";
    }

    load_quanta_config();
    
    ASSERT_EQ(std::string("test_model.gguf"), quanta_config["engine.model_path"]);
    ASSERT_EQ(std::string("test_cli"), quanta_config["model.llama_cli_path"]);

    std::remove(".quanta");
    return true;
}

// We can't easily test the popen logic without a real or mocked llama-cli
// but we can verify that it returns a stubbed response if config is missing.
bool LocalModelTest_StubFallback() {
    quanta_config.clear();
    std::string response = call_quanta_model("test task");
    ASSERT_EQ(std::string("Completed: test task"), response);
    return true;
}

// Register tests
struct LocalModelRegistrar {
    LocalModelRegistrar() {
        add_test_case("LocalModelTest_LoadConfig", LocalModelTest_LoadConfig);
        add_test_case("LocalModelTest_StubFallback", LocalModelTest_StubFallback);
    }
};

static LocalModelRegistrar local_model_registrar;
