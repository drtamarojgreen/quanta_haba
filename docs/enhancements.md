# QuantaHaba Enhancements Backlog

This document tracks realistic, implementation-ready enhancements based on the code currently in this repository.

## 1) Current Baseline (What exists now)

- Python desktop editor (`src/p/editor.py`) with parsing, model workflow, and UI panels.
- Parser + HTML export stack (`src/p/haba_parser.py`, `src/p/html_exporter.py`).
- Script execution utilities for JavaScript and Python (`src/p/script_runner.py`).
- CLI runner for executing `.haba` script content (`src/p/cli_runner.py`).
- OAuth/config plumbing (`src/p/oauth_client.py`, `src/p/config_manager.py`).
- C++ parser and converter/test assets (`src/c/`, `tests/c/`, `tests/sorrel/sdd/`).

## 2) Priority Enhancements (Next 30–60 days)

### P1 — Reliability and Guardrails
1. Add explicit dependency preflight checks for Selenium/Firefox/geckodriver and emit actionable startup diagnostics.
2. Improve parser diagnostics (line/column + section context) for malformed `.haba` files.
3. Add structured error types in script runner (`timeout`, `driver_missing`, `runtime_error`) instead of generic strings.
4. Validate OAuth profile fields before saving configs and include schema versioning.
5. Add graceful fallback when Tkinter messagebox cannot render (headless CI).

### P1 — Test Coverage Expansion
6. Add negative tests for malformed nested tags and unterminated blocks in Haba parser.
7. Add deterministic tests for log parsing when console output contains JSON, quotes, and multiline strings.
8. Add tests for concurrent temp-file operations in script runner.
9. Add coverage for CLI behavior when file encoding is invalid.
10. Add cross-platform path handling tests (spaces, unicode, relative traversal).

### P2 — Developer Experience
11. Create `make test-py`, `make test-cpp`, and `make test-sdd` wrappers at repo root.
12. Add a single `docs/testing.md` quick-start matrix by environment (Linux/macOS/CI/headless).
13. Standardize structured logging format for editor + runner subsystems.
14. Add fixtures directory for canonical `.haba` samples and expected HTML outputs.

## 3) Medium-Term Enhancements (60–120 days)

### Editor Workflow
- Inline diff view between source text and exported HTML.
- Auto-save snapshots and manual version labels.
- Search/replace with regex mode and preview.

### AI Workflow
- Per-task provenance metadata (model source, latency, token counts if available).
- Retry policy with exponential backoff for external model calls.
- User-configurable “offline-only” mode that hard-disables external calls.

### C++/Python Parity
- Align parser behavior contracts between C++ and Python implementations.
- Add a shared compatibility test corpus used by both language implementations.

## 4) Known Technical Risks

- Script execution depends on browser automation availability in the runtime environment.
- GUI code paths can fail in headless CI unless properly mocked.
- External model integrations can return inconsistent payload formats.
- Parser behavior drift risk exists between C++ and Python implementations.

## 5) Definition of Done for Enhancements

Each enhancement should include:
1. Tests for success and failure paths.
2. Documentation updates (README + relevant docs).
3. Clear error messaging (user-facing and developer-facing).
4. No regressions in existing `tests/p`, `tests/c`, and `tests/sorrel/sdd` flows.
