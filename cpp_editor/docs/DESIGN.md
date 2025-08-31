# Haba C++ CLI Tool - Design Specification

This document outlines the design for the C++ Haba command-line tool.

## 1. Application Overview

The application is a native command-line tool named `haba-converter`. Its purpose is to convert `.haba` files into standard `.html` files that can be viewed in any web browser. It is built with standard C++ and has no external GUI framework dependencies.

## 2. Usage

The tool is run from the terminal. It takes a single argument: the path to the input `.haba` file.

### Command-Line Syntax:
```bash
./haba-converter /path/to/your/file.haba
```

### Behavior:
- Upon successful conversion, it will create a new file with the same name but with an `.html` extension in the same directory as the input file.
- It will print a success message to standard output.
- In case of errors (e.g., file not found, incorrect arguments), it will print an error message to standard error.

## 3. Extended `.haba` File Format

To support JavaScript editing, the `.haba` format is extended to include a `<script_layer>`. The `HabaParser` parses and builds this new layer.

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

## 4. HTML Generation Logic

The conversion from `.haba` to `.html` follows these rules:

1.  **HTML Structure**: A basic HTML5 document structure (`<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`) is generated.
2.  **Styles**: The styles from the `<styles>` section are converted into CSS rules inside a `<style>` tag in the HTML `<head>`. Each container is assigned a unique class (`.haba-container-0`, `.haba-container-1`, etc.) to which the corresponding style is applied.
3.  **Content**: The text from the `<content_layer>` is wrapped, in a nested fashion, by the tags from the `<containers>` section. The unique class is added to each container tag to link it to its style.
4.  **Script**: The content of the `<script_layer>` is placed inside a `<script>` tag at the end of the `<body>`.
