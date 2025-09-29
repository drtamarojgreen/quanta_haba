#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include "HabaParser.h"
#include "HabaData.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <commdlg.h>
#include <shellapi.h>
#undef UNICODE
#undef _UNICODE
#endif

// Simple Windows GUI implementation using Win32 API
#ifdef _WIN32

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

// Global variables
HWND g_hEdit;
HWND g_hPreview;
HabaParser g_parser;
std::string g_currentFile;

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

void RunModelDemo() {
    int textLength = GetWindowTextLength(g_hEdit);
    if (textLength == 0) {
        MessageBoxA(NULL, "Editor is empty. Nothing to process.", "Model Demo", MB_OK | MB_ICONINFORMATION);
        return;
    }

    char* buffer = new char[textLength + 1];
    GetWindowTextA(g_hEdit, buffer, textLength + 1);

    std::string content(buffer);
    delete[] buffer;

    std::stringstream ss(content);
    std::string line;
    std::stringstream new_content;
    bool changed = false;

    while (std::getline(ss, line, '\n')) {
        size_t todo_pos = line.find("TODO:");
        if (todo_pos != std::string::npos) {
            std::string task = line.substr(todo_pos + 5);
            // Basic trim
            size_t first = task.find_first_not_of(" \t");
            if (std::string::npos != first) {
                task = task.substr(first);
            }

            line.replace(todo_pos, 5, "DONE:");
            line += " // Model processed: " + task;
            changed = true;
        }
        new_content << line << "\n";
    }

    if (changed) {
        // Remove the final newline character before setting the text
        std::string final_text = new_content.str();
        if (!final_text.empty()) {
            final_text.pop_back();
        }
        SetWindowTextA(g_hEdit, final_text.c_str());
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
            SetMenu(hwnd, hMenu);

            // Create edit control for Haba content
            g_hEdit = CreateWindowEx(WS_EX_CLIENTEDGE, "EDIT", "",
                WS_CHILD | WS_VISIBLE | WS_VSCROLL | WS_HSCROLL | ES_MULTILINE | ES_AUTOVSCROLL | ES_AUTOHSCROLL,
                10, 10, 400, 300, hwnd, NULL, GetModuleHandle(NULL), NULL);

            // Create preview control
            g_hPreview = CreateWindowEx(WS_EX_CLIENTEDGE, "EDIT", "",
                WS_CHILD | WS_VISIBLE | WS_VSCROLL | WS_HSCROLL | ES_MULTILINE | ES_AUTOVSCROLL | ES_AUTOHSCROLL | ES_READONLY,
                420, 10, 400, 300, hwnd, NULL, GetModuleHandle(NULL), NULL);

            // Create buttons
            CreateWindow("BUTTON", "Update Preview", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
                10, 320, 120, 30, hwnd, (HMENU)5, GetModuleHandle(NULL), NULL);

            CreateWindow("BUTTON", "Run Model Demo", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
                140, 320, 120, 30, hwnd, (HMENU)6, GetModuleHandle(NULL), NULL);

            return 0;
        }

        case WM_COMMAND: {
            switch (LOWORD(wParam)) {
                case 1: LoadFile(); break;
                case 2: SaveFile(); break;
                case 3: ExportHTML(); break;
                case 4: PostQuitMessage(0); break;
                case 5: UpdatePreview(); break;
                case 6: RunModelDemo(); break;
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

        case WM_DESTROY:
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
