#include "simple_test_framework.h"
#include "WorkspaceManager.h"
#include <fstream>
#include <string>

bool LoggingTest_FileCreation() {
    WorkspaceManager::logActivity("Test log message");
    std::ifstream logFile("haba/activity.log");
    ASSERT_TRUE(logFile.is_open());

    std::string line;
    bool found = false;
    while(std::getline(logFile, line)) {
        if (line.find("Test log message") != std::string::npos) {
            found = true;
            break;
        }
    }
    ASSERT_TRUE(found);
    return true;
}

// Register tests
struct LoggingRegistrar {
    LoggingRegistrar() {
        add_test_case("LoggingTest_FileCreation", LoggingTest_FileCreation);
    }
};

static LoggingRegistrar logging_registrar;
