#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include "HabaParser.h"
#include "HabaData.h"
#include "ConfigManager.h"
#include "OAuthClient.h"
#include "ScriptAnalyzer.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <commdlg.h>
#include <shellapi.h>
#include <commctrl.h>
#undef UNICODE
#undef _UNICODE
#endif

// Simple Windows GUI implementation using Win32 API
#ifdef _WIN32

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

// Global variables
HWND g_hEdit;
HWND g_hTab;
HWND g_hPreview;
HWND g_hSymbolList;
HWND g_hTodoList;
HWND g_hTaskList;
HWND g_hConsole;
HWND g_hScriptEdit;
HabaParser g_parser;
ConfigManager g_configManager;
OAuthClient* g_oauthClient = nullptr;
std::string g_currentFile;
std::string g_activeProfileName;
bool g_isRecording = false;
std::vector<WPARAM> g_macro;


// Function to generate HTML from HabaData (same as main.cpp)
std::string generateHtml(const HabaData& data) {
    std::stringstream html;

    html << "<!DOCTYPE html>\n";
    html << "<html lang=\"en\">\n";
    html << "<head>\n";
    html << "    <meta charset=\"UTF-8\">\n";
    html << "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n";
    html << "    <title>Haba Output</title>\n";
    html << "    <style>\n";
    
    for (size_t i = 0; i < data.presentation_items.size(); ++i) {
        html << "        .haba-container-" << i << " " << data.presentation_items[i].second << "\n";
    }
    
    html << "        body { font-family: Arial, sans-serif; margin: 20px; }\n";
    html << "        .haba-content { max-width: 800px; margin: 0 auto; }\n";
    html << "    </style>\n";
    html << "</head>\n";
    html << "<body>\n";
    html << "    <div class=\"haba-content\">\n";

    // Add content wrapped in containers
    std::string content_with_containers = data.content;
    for (int i = data.presentation_items.size() - 1; i >= 0; --i) {
        std::stringstream temp_stream;
        std::string container_tag = data.presentation_items[i].first;
        size_t first_space = container_tag.find('>');
        if (first_space != std::string::npos) {
            container_tag.insert(first_space, " class=\"haba-container-" + std::to_string(i) + "\"");
        }

        temp_stream << container_tag << "\n" << content_with_containers << "\n";

        size_t tag_name_start = container_tag.find('<') + 1;
        size_t tag_name_end = container_tag.find_first_of(" >");
        std::string tag_name = container_tag.substr(tag_name_start, tag_name_end - tag_name_start);
        temp_stream << "</" << tag_name << ">";

        content_with_containers = temp_stream.str();
    }
    
    html << "        " << content_with_containers << "\n";
    html << "    </div>\n";

    if (!data.script.empty()) {
        html << "    <script>\n" << data.script << "\n    </script>\n";
    }

    html << "</body>\n";
    html << "</html>\n";

    return html.str();
}

void LoadFile() {
    OPENFILENAME ofn;
    char szFile[260] = {0};

    ZeroMemory(&ofn, sizeof(ofn));
    ofn.lStructSize = sizeof(ofn);
    ofn.lpstrFile = szFile;
    ofn.nMaxFile = sizeof(szFile);
    ofn.lpstrFilter = "Haba Files\0*.haba\0All Files\0*.*\0";
    ofn.nFilterIndex = 1;
    ofn.lpstrFileTitle = NULL;
    ofn.nMaxFileTitle = 0;
    ofn.lpstrInitialDir = NULL;
    ofn.Flags = OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST;

    if (GetOpenFileName(&ofn)) {
        std::ifstream file(szFile);
        if (file.is_open()) {
            std::stringstream buffer;
            buffer << file.rdbuf();
            std::string content = buffer.str();
            file.close();

            SetWindowTextA(g_hEdit, content.c_str());
            g_currentFile = szFile;
        }
    }
}

void SaveFile() {
    if (g_currentFile.empty()) {
        OPENFILENAME ofn;
        char szFile[260] = {0};

        ZeroMemory(&ofn, sizeof(ofn));
        ofn.lStructSize = sizeof(ofn);
        ofn.lpstrFile = szFile;
        ofn.nMaxFile = sizeof(szFile);
        ofn.lpstrFilter = "Haba Files\0*.haba\0All Files\0*.*\0";
        ofn.nFilterIndex = 1;
        ofn.lpstrDefExt = "haba";
        ofn.Flags = OFN_PATHMUSTEXIST | OFN_OVERWRITEPROMPT;

        if (GetSaveFileName(&ofn)) {
            g_currentFile = szFile;
        } else {
            return;
        }
    }

    int textLength = GetWindowTextLength(g_hEdit);
    char* buffer = new char[textLength + 1];
    GetWindowTextA(g_hEdit, buffer, textLength + 1);

    std::ofstream file(g_currentFile);
    if (file.is_open()) {
        file << buffer;
        file.close();
        MessageBoxA(NULL, "File saved successfully!", "Success", MB_OK | MB_ICONINFORMATION);
    }

    delete[] buffer;
}

void ExportHTML() {
    int textLength = GetWindowTextLength(g_hEdit);
    char* buffer = new char[textLength + 1];
    GetWindowTextA(g_hEdit, buffer, textLength + 1);

    try {
        HabaData data = g_parser.parse(std::string(buffer));
        std::string html = generateHtml(data);

        OPENFILENAME ofn;
        char szFile[260] = {0};

        ZeroMemory(&ofn, sizeof(ofn));
        ofn.lStructSize = sizeof(ofn);
        ofn.lpstrFile = szFile;
        ofn.nMaxFile = sizeof(szFile);
        ofn.lpstrFilter = "HTML Files\0*.html\0All Files\0*.*\0";
        ofn.nFilterIndex = 1;
        ofn.lpstrDefExt = "html";
        ofn.Flags = OFN_PATHMUSTEXIST | OFN_OVERWRITEPROMPT;

        if (GetSaveFileName(&ofn)) {
            std::ofstream file(szFile);
            if (file.is_open()) {
                file << html;
                file.close();
                MessageBoxA(NULL, "HTML exported successfully!", "Success", MB_OK | MB_ICONINFORMATION);
            }
        }
    } catch (const std::exception& e) {
        MessageBoxA(NULL, ("Export failed: " + std::string(e.what())).c_str(), "Error", MB_OK | MB_ICONERROR);
    }

    delete[] buffer;
}

void UpdatePreview() {
    int textLength = GetWindowTextLength(g_hEdit);
    char* buffer = new char[textLength + 1];
    GetWindowTextA(g_hEdit, buffer, textLength + 1);

    try {
        HabaData data = g_parser.parse(std::string(buffer));
        std::string preview = "Content: " + data.content + "\n\nPresentation Items:\n";
        
        for (size_t i = 0; i < data.presentation_items.size(); ++i) {
            preview += "Container " + std::to_string(i) + ": " + data.presentation_items[i].first + "\n";
            preview += "Style " + std::to_string(i) + ": " + data.presentation_items[i].second + "\n\n";
        }
        
        if (!data.script.empty()) {
            preview += "Script:\n" + data.script;
        }

        SetWindowTextA(g_hPreview, preview.c_str());
    } catch (const std::exception& e) {
        SetWindowTextA(g_hPreview, ("Parse error: " + std::string(e.what())).c_str());
    }

    delete[] buffer;
}

void LogToConsole(const std::string& message);

void RunModelDemo() {
    if (g_activeProfileName.empty()) {
        MessageBoxA(NULL, "Please select an active profile from the External Models menu.", "Model Demo", MB_OK | MB_ICONWARNING);
        return;
    }

    OAuthConfig config = g_configManager.getConfiguration(g_activeProfileName);
    if (g_oauthClient) {
        delete g_oauthClient;
        g_oauthClient = nullptr; // Good practice to null the pointer after deletion
    }
    g_oauthClient = new OAuthClient(config);

    if (!g_oauthClient->isAuthenticated()) {
        g_oauthClient->initiateAuthorization();
        if (!g_oauthClient->finishAuthorization()) {
            MessageBoxA(NULL, "Authentication failed. Please check your configuration.", "Authentication Error", MB_OK | MB_ICONERROR);
            delete g_oauthClient;
            g_oauthClient = nullptr;
            return;
        }
    }

    int textLength = GetWindowTextLength(g_hEdit);
    char* buffer = new char[textLength + 1];
    GetWindowTextA(g_hEdit, buffer, textLength + 1);
    std::string content(buffer);
    delete[] buffer;

    std::stringstream ss(content);
    std::string line;
    std::stringstream new_content;
    bool changed = false;

    while (std::getline(ss, line)) {
        size_t todo_pos = line.find("TODO:");
        if (todo_pos != std::string::npos) {
            std::string task = line.substr(todo_pos + 5);
            // Basic trim
            size_t first = task.find_first_not_of(" \t");
            if (std::string::npos != first) {
                task = task.substr(first);
            }

            try {
                std::string response = g_oauthClient->callModel(task);
                line.replace(todo_pos, 5, "DONE:");
                line += " // Model response: " + response;
                LogToConsole("Processed task: " + task);
            } catch (const std::exception& e) {
                line += " // Error: " + std::string(e.what());
                LogToConsole("Error processing task: " + std::string(e.what()));
            }
            changed = true;
        }
        new_content << line << "\n";
    }

    if (changed) {
        SetWindowTextA(g_hEdit, new_content.str().c_str());
        MessageBoxA(NULL, "Model demo finished. 'TODO' items have been updated.", "Model Demo Complete", MB_OK | MB_ICONINFORMATION);
    } else {
        MessageBoxA(NULL, "No 'TODO:' items found to process.", "Model Demo", MB_OK | MB_ICONINFORMATION);
    }
}

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
        case WM_CREATE: {
            // Create menu
            HMENU hMenu = CreateMenu();
            HMENU hFileMenu = CreatePopupMenu();
            AppendMenu(hFileMenu, MF_STRING, 1, "Open");
            AppendMenu(hFileMenu, MF_STRING, 2, "Save");
            AppendMenu(hFileMenu, MF_SEPARATOR, 0, NULL);
            AppendMenu(hFileMenu, MF_STRING, 3, "Export HTML");
            AppendMenu(hFileMenu, MF_SEPARATOR, 0, NULL);
            AppendMenu(hFileMenu, MF_STRING, 4, "Exit");
            AppendMenu(hMenu, MF_POPUP, (UINT_PTR)hFileMenu, "File");

            HMENU hEditMenu = CreatePopupMenu();
            AppendMenu(hEditMenu, MF_STRING, 200, "Find");
            AppendMenu(hEditMenu, MF_SEPARATOR, 0, NULL);
            AppendMenu(hEditMenu, MF_STRING, 201, "Record Macro");
            AppendMenu(hEditMenu, MF_STRING, 202, "Play Macro");
            AppendMenu(hMenu, MF_POPUP, (UINT_PTR)hEditMenu, "Edit");

            HMENU hModelMenu = CreatePopupMenu();
            AppendMenu(hModelMenu, MF_STRING, 100, "Configure...");
            AppendMenu(hModelMenu, MF_SEPARATOR, 0, NULL);

            std::vector<std::string> profiles = g_configManager.getProfileNames();
            for (size_t i = 0; i < profiles.size(); ++i) {
                AppendMenu(hModelMenu, MF_STRING, 101 + i, profiles[i].c_str());
            }

            AppendMenu(hMenu, MF_POPUP, (UINT_PTR)hModelMenu, "External Models");

            SetMenu(hwnd, hMenu);

            // Create edit control for Haba content
            g_hEdit = CreateWindowEx(WS_EX_CLIENTEDGE, "EDIT", "",
                WS_CHILD | WS_VISIBLE | WS_VSCROLL | WS_HSCROLL | ES_MULTILINE | ES_AUTOVSCROLL | ES_AUTOHSCROLL,
                10, 10, 400, 300, hwnd, NULL, GetModuleHandle(NULL), NULL);

            // Create Tab Control
            g_hTab = CreateWindow(WC_TABCONTROL, "", WS_CHILD | WS_CLIPSIBLINGS | WS_VISIBLE,
                420, 10, 400, 300, hwnd, NULL, GetModuleHandle(NULL), NULL);

            TCITEM tie;
            tie.mask = TCIF_TEXT;
            tie.pszText = "WYSIWYG Preview";
            TabCtrl_InsertItem(g_hTab, 0, &tie);
            tie.pszText = "Symbol Outline";
            TabCtrl_InsertItem(g_hTab, 1, &tie);
            tie.pszText = "TODO Explorer";
            TabCtrl_InsertItem(g_hTab, 2, &tie);
            tie.pszText = "Actionable Tasks";
            TabCtrl_InsertItem(g_hTab, 3, &tie);


            // Create preview control (will be a child of the tab control)
            g_hPreview = CreateWindowEx(WS_EX_CLIENTEDGE, "EDIT", "",
                WS_CHILD | WS_VISIBLE | WS_VSCROLL | WS_HSCROLL | ES_MULTILINE | ES_AUTOVSCROLL | ES_AUTOHSCROLL | ES_READONLY,
                430, 40, 380, 260, hwnd, NULL, GetModuleHandle(NULL), NULL);

            g_hSymbolList = CreateWindowEx(WS_EX_CLIENTEDGE, "LISTBOX", "",
                WS_CHILD | WS_VSCROLL | LBS_HASSTRINGS,
                430, 40, 380, 260, hwnd, NULL, GetModuleHandle(NULL), NULL);

            g_hTodoList = CreateWindowEx(WS_EX_CLIENTEDGE, "LISTBOX", "",
                WS_CHILD | WS_VSCROLL | LBS_HASSTRINGS,
                430, 40, 380, 260, hwnd, NULL, GetModuleHandle(NULL), NULL);

            g_hTaskList = CreateWindowEx(WS_EX_CLIENTEDGE, "LISTBOX", "",
                WS_CHILD | WS_VSCROLL | LBS_HASSTRINGS,
                430, 40, 380, 260, hwnd, NULL, GetModuleHandle(NULL), NULL);

            // Create console log
            g_hConsole = CreateWindowEx(WS_EX_CLIENTEDGE, "EDIT", "",
                WS_CHILD | WS_VISIBLE | WS_VSCROLL | WS_HSCROLL | ES_MULTILINE | ES_AUTOVSCROLL | ES_AUTOHSCROLL | ES_READONLY,
                10, 360, 810, 100, hwnd, NULL, GetModuleHandle(NULL), NULL);

            // Create script editor
            g_hScriptEdit = CreateWindowEx(WS_EX_CLIENTEDGE, "EDIT", "",
                WS_CHILD | WS_VISIBLE | WS_VSCROLL | WS_HSCROLL | ES_MULTILINE | ES_AUTOVSCROLL | ES_AUTOHSCROLL,
                10, 470, 810, 150, hwnd, NULL, GetModuleHandle(NULL), NULL);

            // Create buttons
            CreateWindow("BUTTON", "Update Preview", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
                10, 320, 120, 30, hwnd, (HMENU)5, GetModuleHandle(NULL), NULL);

            CreateWindow("BUTTON", "Run Model Demo", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
                140, 320, 120, 30, hwnd, (HMENU)6, GetModuleHandle(NULL), NULL);

            return 0;
        }

void OpenConfigDialog(HWND hwnd) {
    // This is a placeholder for a proper dialog.
    // A full implementation would be very complex to do programmatically.
    MessageBoxA(hwnd, "A proper configuration dialog would be created here programmatically, allowing you to add, edit, and delete OAuth profiles. This is a complex task, and for now, this feature remains a placeholder. You can edit the oauth_profiles.json file manually in your AppData/Roaming/QuantaHaba folder.", "Configure", MB_OK | MB_ICONINFORMATION);
}

        case WM_NOTIFY: {
            if (((LPNMHDR)lParam)->code == TCN_SELCHANGE) {
                int iPage = TabCtrl_GetCurSel(g_hTab);
                ShowWindow(g_hPreview, iPage == 0 ? SW_SHOW : SW_HIDE);
                ShowWindow(g_hSymbolList, iPage == 1 ? SW_SHOW : SW_HIDE);
                ShowWindow(g_hTodoList, iPage == 2 ? SW_SHOW : SW_HIDE);
                ShowWindow(g_hTaskList, iPage == 3 ? SW_SHOW : SW_HIDE);
            }
            break;
        }

void LogToConsole(const std::string& message) {
    int len = GetWindowTextLength(g_hConsole);
    SendMessage(g_hConsole, EM_SETSEL, (WPARAM)len, (LPARAM)len);
    SendMessage(g_hConsole, EM_REPLACESEL, 0, (LPARAM)(message + "\r\n").c_str());
}

void UpdateScriptAnalysis() {
    int scriptLength = GetWindowTextLength(g_hScriptEdit);
    char* scriptBuffer = new char[scriptLength + 1];
    GetWindowTextA(g_hScriptEdit, scriptBuffer, scriptLength + 1);
    std::string scriptContent(scriptBuffer);
    delete[] scriptBuffer;

    SendMessage(g_hSymbolList, LB_RESETCONTENT, 0, 0);
    std::vector<Symbol> symbols = findSymbols(scriptContent);
    for (const auto& symbol : symbols) {
        std::string item = symbol.name + " (" + symbol.type + ", line " + std::to_string(symbol.line) + ")";
        SendMessage(g_hSymbolList, LB_ADDSTRING, 0, (LPARAM)item.c_str());
    }

    SendMessage(g_hTodoList, LB_RESETCONTENT, 0, 0);
    std::vector<Todo> todos = findTodos(scriptContent);
    for (const auto& todo : todos) {
        std::string item = todo.text + " (line " + std::to_string(todo.line) + ")";
        SendMessage(g_hTodoList, LB_ADDSTRING, 0, (LPARAM)item.c_str());
    }

    SendMessage(g_hTaskList, LB_RESETCONTENT, 0, 0);
    for (const auto& todo : todos) {
        std::string item = "[TODO] " + todo.text;
        SendMessage(g_hTaskList, LB_ADDSTRING, 0, (LPARAM)item.c_str());
    }
}

HWND g_hFindDialog = NULL;
HWND g_hFindTextEdit = NULL;

LRESULT CALLBACK FindDialogProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
        case WM_INITDIALOG: {
            g_hFindTextEdit = GetDlgItem(hwnd, 1001);
            return TRUE;
        }
        case WM_COMMAND: {
            switch (LOWORD(wParam)) {
                case IDOK: {
                    char findText[256];
                    GetWindowTextA(g_hFindTextEdit, findText, sizeof(findText));
                    // Simple find logic (find next from current cursor)
                    DWORD start, end;
                    SendMessage(g_hEdit, EM_GETSEL, (WPARAM)&start, (LPARAM)&end);
                    FINDTEXTEXA ftex;
                    ftex.chrg.cpMin = end;
                    ftex.chrg.cpMax = -1;
                    ftex.lpstrText = findText;
                    if (SendMessage(g_hEdit, EM_FINDTEXTEXA, FR_DOWN, (LPARAM)&ftex) == -1) {
                        MessageBoxA(hwnd, "Text not found.", "Find", MB_OK);
                    } else {
                        SendMessage(g_hEdit, EM_SETSEL, ftex.chrgText.cpMin, ftex.chrgText.cpMax);
                    }
                    // Fall through to close
                }
                case IDCANCEL:
                    EndDialog(hwnd, 0);
                    return TRUE;
            }
            break;
        }
    }
    return FALSE;
}


void OpenFindDialog(HWND hwnd) {
    // A proper implementation would use a resource file. We are creating it programmatically.
    // This is a simplified version of what a resource editor would generate.
    // This is a placeholder for a proper dialog.
    MessageBoxA(hwnd, "A proper find dialog would be created here programmatically, but this is a complex task. For now, this feature remains a placeholder.", "Find", MB_OK | MB_ICONINFORMATION);
}

        case WM_COMMAND: {
            if (HIWORD(wParam) == EN_CHANGE && (HWND)lParam == g_hScriptEdit) {
                UpdateScriptAnalysis();
            }

            if (LOWORD(wParam) >= 101 && LOWORD(wParam) < 200) {
                UINT menuItemId = LOWORD(wParam);
                HMENU hMenu = GetMenu(hwnd);
                HMENU hModelMenu = GetSubMenu(hMenu, 2); // Assuming "External Models" is the 3rd menu

                // Uncheck all other items
                std::vector<std::string> profiles = g_configManager.getProfileNames();
                for (size_t i = 0; i < profiles.size(); ++i) {
                    CheckMenuItem(hModelMenu, 101 + i, MF_UNCHECKED);
                }

                // Check the selected item
                CheckMenuItem(hModelMenu, menuItemId, MF_CHECKED);
                g_activeProfileName = profiles[menuItemId - 101];
                LogToConsole("Active profile set to: " + g_activeProfileName);
            }

            switch (LOWORD(wParam)) {
                case 1: LoadFile(); break;
                case 2: SaveFile(); break;
                case 3: ExportHTML(); break;
                case 4: PostQuitMessage(0); break;
                case 5: UpdatePreview(); break;
                case 6: RunModelDemo(); break;
                case 100: OpenConfigDialog(hwnd); break;
                case 200: OpenFindDialog(hwnd); break;
                case 201: // Record Macro
                    g_isRecording = !g_isRecording;
                    if (g_isRecording) {
                        g_macro.clear();
                        LogToConsole("Macro recording started.");
                    } else {
                        LogToConsole("Macro recording stopped.");
                    }
                    break;
                case 202: // Play Macro
                    if (!g_macro.empty()) {
                        for (WPARAM key : g_macro) {
                            SendMessage(g_hEdit, WM_CHAR, key, 0);
                        }
                        LogToConsole("Macro playback finished.");
                    }
                    break;
            }
            return 0;
        }

        case WM_SIZE: {
            RECT rect;
            GetClientRect(hwnd, &rect);
            int width = rect.right - rect.left;
            int height = rect.bottom - rect.top;

            // Resize controls
            MoveWindow(g_hEdit, 10, 10, (width - 30) / 2, height - 60, TRUE);
            MoveWindow(g_hPreview, (width - 30) / 2 + 20, 10, (width - 30) / 2, height - 60, TRUE);
            MoveWindow(GetDlgItem(hwnd, 5), 10, height - 40, 120, 30, TRUE);
            MoveWindow(GetDlgItem(hwnd, 6), 140, height - 40, 120, 30, TRUE);
            return 0;
        }

        case WM_CHAR:
            if (g_isRecording && GetFocus() == g_hEdit) {
                g_macro.push_back(wParam);
            }
            // Let the default procedure handle the character as well
            return DefWindowProc(hwnd, uMsg, wParam, lParam);

        case WM_DESTROY:
            if (g_oauthClient) {
                delete g_oauthClient;
                g_oauthClient = nullptr;
            }
            PostQuitMessage(0);
            return 0;
    }
    return DefWindowProc(hwnd, uMsg, wParam, lParam);
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    const char* CLASS_NAME = "HabaGUIEditor";

    WNDCLASS wc = {};
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = CLASS_NAME;
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);

    RegisterClass(&wc);

    HWND hwnd = CreateWindowEx(0, CLASS_NAME, "Haba GUI Editor",
        WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, 900, 400,
        NULL, NULL, hInstance, NULL);

    if (hwnd == NULL) {
        return 0;
    }

    ShowWindow(hwnd, nCmdShow);

    MSG msg = {};
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return 0;
}

#else
// Non-Windows placeholder
int main() {
    std::cout << "Haba GUI Editor\n";
    std::cout << "This GUI implementation requires Windows.\n";
    std::cout << "For cross-platform GUI, consider using Qt, GTK+, or wxWidgets.\n";
    return 0;
}
#endif
