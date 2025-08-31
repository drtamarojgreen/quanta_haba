# Haba C++ Editor - Design Specification

This document outlines the design for the C++ Haba Editor.

## 1. Extended `.haba` File Format

To support JavaScript editing as per the requirements, the `.haba` format will be extended to include a `<script_layer>`. The `HabaParser` will be updated to parse and build this new layer.

### Format Structure:

```xml
<content_layer>
    <!-- HTML content -->
</content_layer>

<presentation_layer>
    <containers>
        <!-- HTML container tags, one per line -->
    </containers>
    <styles>
        <!-- CSS styles, one per line, matched to containers -->
    </styles>
</presentation_layer>

<script_layer>
    /* All JavaScript code will be placed here */
</script_layer>
```

The `HabaData` class will be extended to include a `std::string script;` member.

## 2. GUI Design (Qt Framework)

The application will be built using the Qt 6 framework. The main window will be organized into a multi-panel layout to facilitate simultaneous editing and previewing.

### Main Window Components:

*   **Main Window**: A `QMainWindow` will serve as the top-level container.
*   **Central Widget**: A `QSplitter` will divide the main window into two resizable panels: a left panel for text editing and a right panel for the WYSIWYG preview.
*   **Menu Bar**: A standard `QMenuBar` with:
    *   `File`: Open, Save, Save As, Exit.
    *   `Help`: About.

### Left Panel: Text Editors

The left panel will contain a `QTabWidget` with three tabs:

1.  **Haba View**: A `QPlainTextEdit` widget displaying the entire, raw content of the `.haba` file.
2.  **CSS View**: A `QPlainTextEdit` widget for editing only the `<styles>` content.
3.  **JS View**: A `QPlainTextEdit` widget for editing only the `<script_layer>` content.

### Right Panel: WYSIWYG Preview

The right panel will consist of a `QWebEngineView` widget from the Qt WebEngine module. This widget will render the HTML generated from the `.haba` data.

## 3. Application Workflow

1.  **Loading**: When a `.haba` file is opened, the `HabaParser` reads the content. The full text is loaded into the "Haba View". The extracted styles are loaded into the "CSS View", and the script content into the "JS View".
2.  **HTML Generation**: The application will then generate an HTML document.
    *   The content from `<content_layer>` will be placed inside the nested structure of the `<containers>`.
    *   The `style` attributes will be applied to the containers.
    *   The content of `<script_layer>` will be placed in a `<script>` tag in the HTML's `<head>` or at the end of the `<body>`.
    *   **Example**:
        *   Container: `<p>`
        *   Style: `{ font-size: 16px; }`
        *   Content: `Hello`
        *   Becomes: `<p style="{ font-size: 16px; }">Hello</p>`
3.  **Live Preview**: The generated HTML string will be set as the content of the `QWebEngineView`.
4.  **Editing**:
    *   Editing the "CSS View" or "JS View" will update the corresponding parts of the internal `HabaData` object. The "Haba View" will be updated with the new rebuilt `.haba` text.
    *   Editing the "Haba View" directly will trigger a re-parse of the entire file. The "CSS View" and "JS View" will be updated with the newly parsed content.
    *   Any change will trigger a regeneration of the HTML and update the `QWebEngineView` preview.
5.  **Saving**: The `HabaParser::build` method will be used to generate the final `.haba` file content from the current `HabaData` object, which is then written to a file.
