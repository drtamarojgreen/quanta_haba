#ifndef WORKSPACE_MANAGER_H
#define WORKSPACE_MANAGER_H

#include <string>
#include <vector>
#include <fstream>
#include <ctime>
#include "StringUtils.h"

class WorkspaceManager {
public:
    static void logActivity(const std::string& message) {
        StringUtils::ensureDirectoryExists("haba");
        std::ofstream logFile("haba/activity.log", std::ios::app);
        std::time_t now = std::time(0);
        char* dt = std::ctime(&now);
        std::string ts(dt);
        ts.pop_back(); // remove newline
        logFile << "[" << ts << "] " << message << std::endl;
    }

    static void saveSession(const std::string& currentFile, int cursorPos) {
        StringUtils::ensureDirectoryExists("haba");
        std::ofstream sessionFile("haba/session.json");
        sessionFile << "{\n";
        sessionFile << "  \"last_file\": \"" << currentFile << "\",\n";
        sessionFile << "  \"cursor_pos\": " << cursorPos << "\n";
        sessionFile << "}\n";
    }

    static void autoSave(const std::string& content, const std::string& filePath) {
        StringUtils::ensureDirectoryExists("haba");
        std::string savePath = filePath.empty() ? "haba/autosave.haba" : filePath + ".autosave";
        std::ofstream outFile(savePath);
        outFile << content;
    }
};

#endif
