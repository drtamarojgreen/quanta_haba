#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include "HabaParser.h"

// Forward declarations for Qt classes to reduce header dependencies
class QPlainTextEdit;
class QWebEngineView;
class QTabWidget;
class QSplitter;

/**
 * @class MainWindow
 * @brief The main window for the Haba C++ Editor application.
 */
class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    // Slot to handle text changes in any of the editor views
    void onTextChanged();

    // Slots for file menu actions
    void openFile();
    void saveFile();
    void saveFileAs();
    void about();

private:
    // --- UI Elements ---
    QSplitter *mainSplitter;
    QTabWidget *editorTabs;
    QPlainTextEdit *habaView;
    QPlainTextEdit *cssView;
    QPlainTextEdit *jsView;
    QWebEngineView *previewView;

    // --- Core Logic ---
    HabaParser habaParser;
    HabaData currentHabaData;
    QString currentFilePath;

    // --- Helper Methods ---
    void setupUI();
    void setupMenuBar();
    void connectSignals();
    void updatePreview();
    void loadDataToViews();
    void loadViewsToData();
};

#endif // MAINWINDOW_H
