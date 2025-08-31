# QuantaHaba IDE Features and Roadmap

This document provides a comprehensive overview of the features, design, and development roadmap for the QuantaHaba IDE.

## 1. Overview

QuantaHaba is a Velo-integrated, LLM-powered design editor that transforms the way creators build interactive web experiences. It combines a visual design canvas with powerful AI-driven tools to streamline the web development process.

## 2. Development Roadmap

The development of QuantaHaba is planned in several phases:

### MVP — Springboard (weeks 0–4)
**Goal:** A colorful single-page editor with an AI sidebar and basic save/load via Node.
- Static HTML/CSS editor canvas (drag/drop minimal)
- AI Sidebar: prompt box → fetch to local Node LLM proxy (or mock)
- Save/Open projects to local JSON files (Node fs)
- Export HTML bundle (single-file export)
- Basic user onboarding tour

### Beta — Habitats (weeks 5–10)
**Goal:** Polish editor UX, add core editable components, and collaborative illusions.
- Component library (cards, heroes, lists, forms) editable inline
- Undo/Redo, version snapshots, autosave
- Template gallery + one-click apply
- Theme editor (colors, fonts) → CSS variables
- Simple role-based access (local accounts) using Node crypto & file store

### v1.0 — Garden Party (weeks 11–20)
**Goal:** Production-ready editor, robust AI assistance, stable export/import.
- Full AI sidebar features (suggestions, explain code, accessibility fixes)
- Project import/export (zip of HTML/CSS/JS)
- User settings, keyboard shortcuts, customizable workspace layout
- Testing harness and deployment script (Node static server + nginx config example)

### v2.0 — Full Bloom (weeks 21–40)
**Goal:** Collaboration, plugin micro-app system, extensibility API.
- Real-time collaboration (CRDT-lite over WebSocket)
- Plugin micro-apps via sandboxed HTML imports (no external libs)
- Marketplace-ready package format (JSON manifest + assets)
- CI/CD deploy scripts, automated visual regression snapshotting

## 3. Feature Enhancements

Here is a detailed list of planned enhancements for the IDE, grouped by category.

### A. Editor UX & Components
- Canvas with content-editable blocks and drag/drop.
- Snap-to-grid and alignment guides.
- Resizable panels (left/right/inspector).
- Component palette: prebuilt HTML snippets.
- Inline edit toolbar (bold/italic/link).
- Undo/Redo stack.
- Multi-select & group transform.
- Visual CSS variable theme editor.
- One-click theme presets.
- Drag-and-drop image upload.
- Layer panel (z-order management).
- Snap-to-guides & smart positioning.
- Inline code editor for component HTML/CSS.
- Live preview toggle.
- Accessibility overlay.
- Responsive breakpoints preview.
- Component props inspector.
- Paste-as-plain-text option.
- Component duplicate action.
- Template system: save canvas as a template.

### B. AI Sidebar (QuantaPal)
- Prompt box for LLM interaction.
- Suggestion list UI for AI changes.
- “Explain this element” feature.
- “Refactor this HTML” feature.
- “Accessibility fix” generator.
- “Tone & copy” assistant.
- Snippet insertion from prompts.
- History of AI prompts and results.
- Quick actions for AI suggestions.
- Prompt templates for common tasks.
- Inline AI hints as tooltips.
- “Explain CSS rule” feature.
- “Why does my layout break?” diagnostic tool.
- Sandboxed JS runner for AI scripts.
- Privacy toggle for AI features.
- Rate-limiting and progress UI for AI calls.
- AI-assisted theme generator.
- AI-generated alt text tool.
- AI-driven checklist generator (SEO, accessibility).
- AI “undo” rationale log.

### C. Styling, Animations & Visual Tools
- Visual gradient builder.
- CSS variables manager.
- Micro-animation previewer (CSS keyframes).
- SVG icon inspector/editor.
- Drop shadow visualizer.
- Color contrast validator.
- Typography playground.
- CSS transitions builder.
- Simple particle confetti animation.
- Parallax background builder.
- CSS grid visual inspector.
- Image focal-point picker.
- CSS minifier on export.
- Inline SVG sprite generator.
- Theme snapshot visualizer.
- Responsive breakpoint editor.
- Accessible animations toggle.
- Micro-interaction presets.
- CSS utility class generator.
- Export CSS as a single file or inline.

### D. Data, Storage & Export
- Save projects as JSON.
- Autosave with diffing.
- Export project as a single HTML file.
- Export as a zip bundle.
- Import project from JSON.
- Version snapshots.
- Simple project manifest.
- Download assets in a folder.
- Host static export via Node server.
- Export inlined critical CSS.
- Project thumbnail generator.
- Local encrypted backups.
- Export guide with README.
- Project import validation.
- Single-file self-contained HTML export.

### E. Performance & QA
- Lighthouse-style checklist.
- Built-in profiler.
- Asset optimizer.
- CSS usage analyzer.
- Accessibility smoke tests.
- Visual diff tool for snapshots.
- Unit test harness stub.
- CI-friendly export script.
- Error logging UI.
- Performance presets.

### F. Security, Privacy & Admin
- Local account system with salted hash.
- Project-level encryption toggle.
- Permission model (viewer/editor/exporter).
- CSRF-safe export endpoints.
- Audit trail of major actions.
- Content profanity filter.
- Configurable privacy settings.

### G. Developer & Extensibility Tools
- Plugin manifest spec.
- Plugin loader with iframe sandbox.
- Local CLI script to scaffold templates.
- Simple REST API server in Node.
- Dev-mode toggle to show raw code.
- Inline JS sandbox.
- Project linter rules.
- Auto-documentation generator.

## 4. Haba C++ CLI Tool

In addition to the web-based IDE, the project includes a native command-line tool named `haba-converter`.

### Purpose
The `haba-converter` tool converts `.haba` files into standard `.html` files that can be viewed in any web browser.

### Usage
```bash
./haba-converter /path/to/your/file.haba
```

For more details on the file format and generation logic, please refer to the [Haba C++ CLI Tool - Design Specification](../cpp_editor/docs/DESIGN.md).
