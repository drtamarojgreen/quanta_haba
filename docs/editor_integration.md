# Greenhouse Desktop Editor: Project Plan

## 1. Introduction

This document outlines a development plan for a custom desktop editor designed to streamline the process of building and managing content for the Greenhouse website. The goal is to create a single, powerful tool that combines code editing, content management, and a live preview into one seamless experience. This will empower developers, content creators, and other team members to work more efficiently and consistently.

The core concept is a side-by-side application where changes on the left panel (code/content) are instantly reflected in a visual preview on the right panel (WYSIWYG).

---

## 2. Core Features

This section details the essential features that will form the foundation of the desktop editor.

### 2.1. Side-by-Side Editor and Live Preview

This is the central feature of the application. The main window will be split into two panes:

*   **Editor Pane (Left):** A flexible text and code editor where users can write and modify HTML, CSS, JavaScript, and structured content files (like JSON or Markdown).
*   **WYSIWYG Preview Pane (Right):** A "What You See Is What You Get" panel that renders a live, interactive preview of the website component being edited. This preview will update in real-time as the user types in the editor pane, providing immediate visual feedback.

### 2.2. Web Technologies Support

The editor will have first-class support for core web technologies, including:

*   **HTML:** For structuring the content.
*   **CSS:** For styling the content.
*   **JavaScript:** For adding interactivity.
*   The editor will provide syntax highlighting, auto-completion, and error checking for these languages to improve accuracy and development speed.

### 2.3. Structured Content Management

Beyond just code, the editor will be designed to manage the structured data that populates the website. This means users can easily edit content files (e.g., a JSON file containing a list of team members or a Markdown file for a blog post) and see that content rendered correctly in the preview pane within the website's template.

### 2.4. Live API Integration

The preview pane will be able to connect to our live API endpoints. This allows the editor to fetch real, dynamic data (e.g., from our database) and render it in the preview. This is crucial for accurately testing and visualizing how components will look and behave with live data, rather than just static mockups.

### 2.5. Integrated Documentation Viewer

To serve as an all-in-one tool, the editor will include a built-in documentation browser. This feature will allow users to open and read our developer toolkit guides (like `greenhouse_it_tools.md`) directly within the application, providing convenient access to essential information without needing to switch contexts.

### 2.6. Project and File Management

The application will include a file explorer sidebar, similar to modern code editors. This will allow users to:
*   Open a project folder.
*   View the project's file and directory structure.
*   Create, delete, rename, and manage files directly within the editor.

---

## 3. Proposed Technology Stack

To build this application, we need to choose the right tools for the job. This section proposes a "stack" of technologies that are well-suited for creating a modern, cross-platform desktop editor. We've chosen these tools because they are powerful, widely-used, and allow us to leverage existing web development skills.

### 3.1. Core Framework: Electron.js

*   **What it is:** Electron is a framework that lets you build desktop applications using web technologies (HTML, CSS, and JavaScript). It's like a special, customized web browser that runs as a standalone desktop app.
*   **Analogy:** Think of it as a "bento box" for a web application. It neatly packages our web code so that it can be installed and run just like any other desktop app (like Word or Slack) on Windows, Mac, or Linux.
*   **Why we'd use it:** It's the industry standard for this type of application. Many popular apps like Slack, Discord, and Visual Studio Code are built with Electron. It allows our team to use their existing web development expertise to build a desktop app, which is incredibly efficient.

### 3.2. User Interface (UI): React.js

*   **What it is:** React is a JavaScript library for building user interfaces. It allows us to create complex UIs from small, isolated pieces of code called "components".
*   **Analogy:** React is like using a set of high-quality, pre-fabricated LEGO bricks to build our application's interface. Instead of building every button, menu, and panel from scratch, we can use and reuse these components to construct a complex UI quickly and reliably.
*   **Why we'd use it:** React is extremely popular and powerful for building interactive applications. It will help us manage the complexity of our editor's interface, ensuring it is fast and responsive.

### 3.3. Code Editor Component: Monaco Editor

*   **What it is:** Monaco is the code editor component that powers Visual Studio Code, one of the world's most popular code editors. It is available as a separate component that we can integrate directly into our application.
*   **Analogy:** This is like taking the powerful, high-performance engine from a world-class sports car and putting it directly into our custom-built vehicle. We get all the power and features (like syntax highlighting, auto-completion, and error-checking) without having to build it from scratch.
*   **Why we'd use it:** It provides a professional-grade code editing experience right out of the box. It's highly performant, feature-rich, and familiar to many developers.

### 3.4. WYSIWYG Preview Pane

*   **What it is:** The preview pane will be a controlled web browser environment embedded within our application.
*   **Analogy:** This is like having a secure, sound-proofed "testing room" inside our kitchen. We can prepare a dish (the code) and then immediately see how it looks and tastes in a realistic environment (the preview pane) without affecting the main restaurant.
*   **Why we'd use it:** The most direct way to provide a true-to-life preview of web content is to render it using a web browser engine. We will likely use a standard HTML `<iframe>` element or a similar `WebView` component provided by Electron. This ensures that what the user sees in the preview is exactly what they will see in a real web browser.

---

## 4. Phased Development Roadmap

We will approach the development of the Greenhouse Desktop Editor in a series of phases. This allows us to build and test the application incrementally, ensuring that the core functionality is solid before moving on to more advanced features.

### Phase 1: MVP - Core Editor and Preview

*   **Goal:** To build the fundamental, minimum viable product (MVP).
*   **Key Deliverables:**
    *   A basic desktop application shell using Electron.
    *   A window with two panes: the Monaco editor on the left and a simple preview pane on the right.
    *   The ability to edit local HTML and CSS files and see the changes render in real-time in the preview pane.
    *   A simple file-opening mechanism.
*   **Outcome:** A functional proof-of-concept that validates the core side-by-side editing experience.

### Phase 2: Dynamic Content and API Integration

*   **Goal:** To connect the editor to real data sources.
*   **Key Deliverables:**
    *   Implement the ability to edit structured data files (e.g., JSON).
    *   Create a mechanism for the preview pane to fetch data from our API endpoints.
    *   Develop a templating system so the preview can render the structured data into an HTML template.
    *   Implement the project/file management sidebar.
*   **Outcome:** The editor can now be used to manage real website content that is powered by our backend.

### Phase 3: Advanced Features and Usability

*   **Goal:** To transform the functional tool into a full-featured, user-friendly application.
*   **Key Deliverables:**
    *   Integrate the documentation viewer.
    *   Add support for JavaScript interactivity within the preview pane.
    *   Implement settings and preferences for the editor.
    *   Refine the UI/UX, adding features like tabs, status bars, and improved error handling.
*   **Outcome:** The editor is now a rich and powerful tool that covers all intended use cases.

### Phase 4: Polish, Testing, and Distribution

*   **Goal:** To prepare the application for internal release.
*   **Key Deliverables:**
    *   Conduct thorough testing and bug fixing.
    *   Focus on performance optimization to ensure the app is fast and responsive.
    *   Create application installers for Windows, Mac, and Linux.
    *   Write user documentation on how to install and use the editor.
*   **Outcome:** A stable, reliable, and well-documented application ready for the team to use.
