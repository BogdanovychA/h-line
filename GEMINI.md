# Gemini CLI Context: H-Line (Hotline App)

This file provides essential context for Gemini agents working on the **H-Line** project. H-Line is a cross-platform application (Desktop/Web) designed for the Ukrainian public sector to automate the processing and submission of citizen appeals via email.

## 🚀 Project Overview
- **Purpose**: Rapidly capture and send citizen appeals via SMTP with automated document generation.
- **Owner**: Andrii Bogdanovych.
- **License**: EUPL-1.2.
- **Target Audience**: Government sector, specifically for handling citizen appeals.

## 🛠 Tech Stack
- **Language**: Python 3.12+
- **UI Framework**: [Flet](https://flet.dev/) (Flutter-based Python framework).
- **Package Manager**: [uv](https://github.com/astral-sh/uv).
- **Localization**: [Project Fluent](https://projectfluent.org/) via `fluent-manager`.
- **Validation/Settings**: Pydantic v2 & `pydantic-settings`.
- **Doc Generation**: `docxtpl` (DOCX), `jinja2` (HTML/MD).
- **Communication**: SMTP (SSL/TLS support).
- **Analytics**: Google Analytics (via Measurement API).

## 🏗 Architecture & Patterns
The project adheres to **SOLID** and **DRY** principles.
- **Registry Pattern**: Used for document generators (`GlobalGenerator`) and email senders (`EmailManager`).
- **State Management**: Centralized in `PandorasBox` (a dataclass containing services like storage, generator, fluent manager, etc.).
- **Persistence**: `flet-storage` (wrapper for SharedPreferences).
- **Modularity**: New file types or email protocols can be added by implementing base classes and registering them in `src/ui/main.py`.

## 📂 Key Directory Structure
- `src/main.py`: Main entry point.
- `src/ui/`: UI components and routing.
    - `main.py`: UI initialization and Registry setup.
    - `routes/`: Individual page views.
    - `utils/`: UI styling, elements, and models.
- `src/core/`: Business logic implementations (SMTP, document managers).
- `src/abstract/`: Base classes and interfaces for modular components.
- `src/models/`: Pydantic models and Enums.
- `src/assets/`: Images, icons, and localization files (`.ftl`).
- `docker_data/`: Volume mounts for Docker deployment (locales, output, templates).

## 🌍 Localization (Fluent)
Translations are stored in `src/assets/locales/` (e.g., `uk/`, `en/`).
Files:
- `ui.ftl`: Interface text.
- `mail.ftl`: Email subjects and bodies.
- `logs.ftl`: Logging messages.

## 🧪 Testing
- **Framework**: `pytest`.
- **Location**: `tests/`.
- **Coverage**: Focuses on localization and core logic.

## 📜 Development Mandates
1. **Surgical Updates**: Prefer `replace` for targeted edits. Maintain stylistic consistency (Black/isort).
2. **Registry Awareness**: When adding new functionality (e.g., a new document format), ensure it is registered in `src/ui/main.py`.
3. **Localization First**: NEVER hardcode strings in the UI. Always add a key to `ui.ftl` and use `box.fluent.get("key")`.
4. **Validation**: Use Pydantic models for data validation, especially for form inputs.
5. **Security**: Do not leak SMTP credentials. Use `.env` via `pydantic-settings`.
6. **Project Structure**: Follow the existing `abstract` -> `core`/`models` -> `ui` flow.

## 🛠 Useful Commands
- `uv run flet run`: Run as desktop app.
- `uv run flet run --web`: Run as web app.
- `pytest`: Run tests.
- `black . && isort .`: Format code.
