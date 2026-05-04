![QuantaHaba Logo](docs/images/logo.jpg)

QuantaHaba 🌱

QuantaHaba is a Velo-integrated, LLM-powered design editor that blends structured authoring with practical developer tooling. This repository currently ships a Python editor stack, C++ parser/converter utilities, and test suites across C++, Python, and SDD-style (Sorrel: Standardizing of Resilient and Reliable Equipment Learning) flows.

## Demo Video

[![Watch the video](https://img.youtube.com/vi/3Mglddunz5s/0.jpg)](https://www.youtube.com/watch?v=3Mglddunz5s)

## Current Available Features

### Core Editing & Parsing
- Haba document parsing for structured content, styles, and script blocks.
- Python Tkinter editor with preview-oriented workflow.
- Symbol outline and TODO explorer side panels.
- HTML export pipeline for parsed Haba content.

### Script Execution & Task Extraction
- JavaScript execution from `.haba` scripts through a headless browser runner.
- Console log capture and extraction of actionable TODO/FIXME items.
- JavaScript error capture with stack traces surfaced as tasks.
- Python script execution helper with timeout and stderr-based failure reporting.

### AI / Model Workflow
- Local model integration path for Quanta Tissu (when package + weights are available).
- External model client fallback path when authenticated.
- Stubbed-response fallback mode when no model backend is available.
- Prompt/task loop that converts `TODO:` items to `DONE:` while logging work products.

### Configuration & OAuth Support
- OAuth client integration hooks in the editor stack.
- Local profile/config persistence in `~/.quanta_haba/oauth_configs.json`.
- Save/load/delete configuration profiles through a dedicated config manager.

### Developer Tooling
- C++ `haba-converter` command-line workflow for `.haba` → `.html` conversion.
- C++ parser/config/script-analyzer test binaries under `tests/c/`.
- Python unit-style tests for parser, editor, script runner, CLI runner, linter, and components.
- SDD card/fact test harness under `tests/sorrel/sdd/`.

## GitHub Workflow Features

QuantaHaba is organized for GitHub-native collaboration and delivery:
- Pull-request based development with reviewable docs/code changes.
- Multi-language test structure (`tests/p`, `tests/c`, and `tests/sorrel/sdd`) suitable for CI matrix jobs.
- Documentation-first architecture decisions in `docs/` for issue/PR traceability.
- Modular source layout (`src/p`, `src/c`) that supports incremental feature branches and milestone planning.

## Developer Tools

### Haba C++ CLI Tool

The `haba-converter` is a command-line utility for converting `.haba` files into standard `.html` files.

**Usage:**
```bash
./haba-converter /path/to/your/file.haba
```

### Building and Testing the C++ Editor

```bash
cd src/c
mkdir -p build
cd build
cmake ..
cmake --build .
ctest
```

### Running the Python Editor

```bash
python3 src/p/editor.py
```

### Running Python Tests

```bash
python3 -m unittest discover -s tests/p
```

## Philosophy

QuantaHaba is built on a simple belief: creativity grows fastest when people feel safe to explore.

A greenhouse does not force growth—it creates the conditions for growth. QuantaHaba follows the same model for builders:
- **Safe experimentation**: You can iterate rapidly without losing structure.
- **Clear thinking over chaos**: Ideas move from rough sparks to intentional systems.
- **Human + AI partnership**: AI accelerates drafts; humans keep purpose, taste, and judgment.
- **Practical shipping mindset**: Inspiration is only complete when it becomes something real and usable.

We do not want tooling that is merely impressive—we want tooling that helps people make meaningful things, repeatedly, with confidence.

If design tools are usually a canvas, QuantaHaba aims to be a habitat: alive, adaptive, and focused on helping your best ideas take root.

## Future Enhancements

### Product Vision
- LLM-driven layout generation from natural-language prompts.
- Rich interactive plugin integrations (quiz, journaling, events, and community widgets).
- Collaborative editing with shared workspaces.
- Import/export bridges across Wix, Figma, and GitHub.

### UX and Design System Ideas
- “Bloom Mode” to generate theme palettes and typography from a single concept word.
- Guided “Haba Quests” for progressive learning and onboarding.
- Expanded component/template gallery with one-click insertion.

### Platform and Ecosystem
- Plugin marketplace for sharing and remixing QuantaHaba creations.
- Stronger CI automation and release packaging workflows.
- Deeper test hardening around parser contracts and SDD failure modes.

## Quick Start

1. Build C++ components if needed (`src/c`).
2. Launch the Python editor (`python3 src/p/editor.py`).
3. Use test suites under `tests/` to validate parser, runner, and editor behavior.
