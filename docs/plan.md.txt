QuantaHaba — Roadmap (playful + pragmatic)
MVP — Springboard (weeks 0–4)

Goal: a colorful single-page editor with an AI sidebar and basic save/load via Node.

Static HTML/CSS editor canvas (drag/drop minimal)

AI Sidebar: prompt box → fetch to local Node LLM proxy (or mock)

Save/Open projects to local JSON files (Node fs)

Export HTML bundle (single-file export)

Basic user onboarding tour

Beta — Habitats (weeks 5–10)

Goal: polish editor UX, add core editable components, and collaborative illusions.

Component library (cards, heroes, lists, forms) editable inline

Undo/Redo, version snapshots, autosave

Template gallery + one-click apply

Theme editor (colors, fonts) → CSS variables

Simple role-based access (local accounts) using Node crypto & file store

v1.0 — Garden Party (weeks 11–20)

Goal: production-ready editor, robust AI assistance, stable export/import.

Full AI sidebar features (suggestions, explain code, accessibility fixes)

Project import/export (zip of HTML/CSS/JS)

User settings, keyboard shortcuts, customizable workspace layout

Testing harness and deployment script (Node static server + nginx config example)

v2.0 — Full Bloom (weeks 21–40)

Goal: collaboration, plugin micro-app system, extensibility API.

Real-time collaboration (CRDT-lite over WebSocket)

Plugin micro-apps via sandboxed HTML imports (no external libs)

Marketplace-ready package format (JSON manifest + assets)

CI/CD deploy scripts, automated visual regression snapshotting

UX sketch: AI Sidebar + Colorful Editor (quick image in words)

Left: Tool Palette (Components, Templates, Themes). Colorful icons, drag handles.

Center: Canvas — WYSIWYG area with soft pastel grid, snap-to guides, editable nodes.

Right: AI Sidebar (QuantaPal) — prompt input at top, suggestions list, Explain/Refactor/Accessibility/Copy-to-clipboard buttons, action buttons that apply changes to canvas.

Bottom: Inspector for selected node (styles, attributes, events).

Hue slider and theme chips in header for instant colorful toggles.

Micro-interactions: seeds sprout on save, subtle confetti on publish.