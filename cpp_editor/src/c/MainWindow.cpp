#include "MainWindow.h"

// Qt includes
#include <QPlainTextEdit>
#include <QWebEngineView>
#include <QSplitter>
#include <QTabWidget>
#include <QMenuBar>
#include <QMenu>
#include <QFileDialog>
#include <QMessageBox>
#include <QFile>
#include <QTextStream>
#include <QVBoxLayout>

#include <string>
#include <sstream>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent), currentFilePath("") {
    setupUI();
    setupMenuBar();
    connectSignals();

    // Set an initial empty state
    updatePreview();
}

MainWindow::~MainWindow() {
    // Qt handles child widget deletion
}

void MainWindow::setupUI() {
    // Main splitter
    mainSplitter = new QSplitter(Qt::Horizontal, this);
    setCentralWidget(mainSplitter);

    // Left side: Tabbed editors
    editorTabs = new QTabWidget();
    habaView = new QPlainTextEdit();
    cssView = new QPlainTextEdit();
    jsView = new QPlainTextEdit();

    // Set fonts for editors
    QFont monoFont("Monospace");
    monoFont.setStyleHint(QFont::TypeWriter);
    habaView->setFont(monoFont);
    cssView->setFont(monoFont);
    jsView->setFont(monoFont);

    editorTabs->addTab(habaView, "Haba");
    editorTabs->addTab(cssView, "CSS");
    editorTabs->addTab(jsView, "JS");

    // Right side: Web preview
    previewView = new QWebEngineView();

    // Add widgets to splitter
    mainSplitter->addWidget(editorTabs);
    mainSplitter->addWidget(previewView);
    mainSplitter->setSizes({400, 600}); // Initial sizes

    setWindowTitle("Haba C++ Editor");
    resize(1024, 768);
}

void MainWindow::setupMenuBar() {
    QMenu *fileMenu = menuBar()->addMenu("&File");

    QAction *openAction = new QAction("&Open...", this);
    connect(openAction, &QAction::triggered, this, &MainWindow::openFile);
    fileMenu->addAction(openAction);

    QAction *saveAction = new QAction("&Save", this);
    connect(saveAction, &QAction::triggered, this, &MainWindow::saveFile);
    fileMenu->addAction(saveAction);

    QAction *saveAsAction = new QAction("Save &As...", this);
    connect(saveAsAction, &QAction::triggered, this, &MainWindow::saveFileAs);
    fileMenu->addAction(saveAsAction);

    fileMenu->addSeparator();

    QAction *exitAction = new QAction("E&xit", this);
    connect(exitAction, &QAction::triggered, this, &QWidget::close);
    fileMenu->addAction(exitAction);

    QMenu *helpMenu = menuBar()->addMenu("&Help");
    QAction *aboutAction = new QAction("&About", this);
    connect(aboutAction, &QAction::triggered, this, &MainWindow::about);
    helpMenu->addAction(aboutAction);
}

void MainWindow::connectSignals() {
    // When text changes, update the preview
    connect(habaView, &QPlainTextEdit::textChanged, this, &MainWindow::onTextChanged);
    connect(cssView, &QPlainTextEdit::textChanged, this, &MainWindow::onTextChanged);
    connect(jsView, &QPlainTextEdit::textChanged, this, &MainWindow::onTextChanged);
}

void MainWindow::onTextChanged() {
    // Avoid recursive signals by temporarily blocking them
    habaView->blockSignals(true);
    cssView->blockSignals(true);
    jsView->blockSignals(true);

    QWidget* currentWidget = editorTabs->currentWidget();

    if (currentWidget == habaView) {
        // If the main Haba view is edited, re-parse everything
        currentHabaData = habaParser.parse(habaView->toPlainText().toStdString());
        loadDataToViews(); // This will update CSS and JS tabs
    } else {
        // If CSS or JS view is edited, update the data object
        loadViewsToData();
        // and then update the main Haba view
        std::string built_text = habaParser.build(currentHabaData);
        habaView->setPlainText(QString::fromStdString(built_text));
    }

    updatePreview();

    // Unblock signals
    habaView->blockSignals(false);
    cssView->blockSignals(false);
    jsView->blockSignals(false);
}

void MainWindow::updatePreview() {
    std::stringstream html;
    html << "<html><head><style>";

    // Combine all styles into one block
    for(const auto& item : currentHabaData.presentation_items) {
        html << item.first << " " << item.second << "\n";
    }

    html << "</style></head><body>";
    html << currentHabaData.content;
    html << "</body>";

    if (!currentHabaData.script.empty()) {
        html << "<script>" << currentHabaData.script << "</script>";
    }
    html << "</html>";

    previewView->setHtml(QString::fromStdString(html.str()));
}

void MainWindow::loadDataToViews() {
    // This function loads data from currentHabaData into the CSS and JS views.
    // The habaView is considered the source of truth, so we don't set it here.

    std::stringstream css;
    for(const auto& item : currentHabaData.presentation_items) {
        css << item.second << "\n";
    }
    cssView->setPlainText(QString::fromStdString(css.str()));

    jsView->setPlainText(QString::fromStdString(currentHabaData.script));
}

void MainWindow::loadViewsToData() {
    // This function updates currentHabaData from the individual CSS and JS views.

    // Update styles
    QStringList cssLines = cssView->toPlainText().split('\n');
    for(int i = 0; i < cssLines.size(); ++i) {
        if (i < currentHabaData.presentation_items.size()) {
            currentHabaData.presentation_items[i].second = cssLines[i].toStdString();
        }
    }

    // Update script
    currentHabaData.script = jsView->toPlainText().toStdString();
}


void MainWindow::openFile() {
    QString filePath = QFileDialog::getOpenFileName(this, "Open Haba File", "", "Haba Files (*.haba);;All Files (*)");
    if (filePath.isEmpty()) {
        return;
    }

    QFile file(filePath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        QMessageBox::warning(this, "Error", "Could not open file.");
        return;
    }

    QTextStream in(&file);
    std::string fileContent = in.readAll().toStdString();
    file.close();

    currentFilePath = filePath;
    currentHabaData = habaParser.parse(fileContent);

    // Block signals while programmatically setting text
    habaView->blockSignals(true);
    cssView->blockSignals(true);
    jsView->blockSignals(true);

    habaView->setPlainText(QString::fromStdString(fileContent));
    loadDataToViews();
    updatePreview();

    habaView->blockSignals(false);
    cssView->blockSignals(false);
    jsView->blockSignals(false);

    setWindowTitle("Haba C++ Editor - " + currentFilePath);
}

void MainWindow::saveFile() {
    if (currentFilePath.isEmpty()) {
        saveFileAs();
        return;
    }

    QFile file(currentFilePath);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        QMessageBox::warning(this, "Error", "Could not save file.");
        return;
    }

    loadViewsToData();
    std::string built_text = habaParser.build(currentHabaData);

    QTextStream out(&file);
    out << QString::fromStdString(built_text);
    file.close();
}

void MainWindow::saveFileAs() {
    QString filePath = QFileDialog::getSaveFileName(this, "Save Haba File", "", "Haba Files (*.haba);;All Files (*)");
    if (filePath.isEmpty()) {
        return;
    }
    currentFilePath = filePath;
    setWindowTitle("Haba C++ Editor - " + currentFilePath);
    saveFile();
}

void MainWindow::about() {
    QMessageBox::about(this, "About Haba C++ Editor",
        "A C++ editor for the .haba file format.\n\n"
        "Built with Qt.");
}
