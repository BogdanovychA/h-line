# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run as desktop app
uv run flet run

# Run as web app
uv run flet run --web

# Run all tests
pytest

# Run a single test
pytest tests/test_localization.py::test_ui_localization

# Format code
black . && isort .

# Docker: rebuild and start
docker-compose up -d --build

# Docker: start with existing image
docker-compose up -d
```

## Architecture

The app follows an `abstract → core/models → ui` layered flow.

**`src/abstract/`** — interfaces only. `BaseTemplateManager` (document generation), `BaseGenerator`, `SMTPSenderBase`, `BaseSender`, `BaseSaver`, `BaseNameCreator`. These define contracts; no logic here.

**`src/core/`** — concrete implementations. `DocManager`/`TxtManager` implement `BaseTemplateManager`. `SMTPSenderTLS`/`SMTPSenderSSL` implement `SMTPSenderBase`. `EmailManager` is the registry for SMTP protocols.

**`src/models/`** — `AppealRequest` (Pydantic, core data model for a citizen appeal), `FileType` / `SMTPProtokol` enums, custom errors.

**`src/config/`** — pydantic-settings classes with env-var prefixes: `APP__*`, `SERVER__*`, `EMAIL_SENDER__*`, `EMAIL_RECIPIENT__*`, `GOOGLE_ANALYTICS__*`. Source: `src/assets/.env`.

**`src/ui/main.py`** — the wiring point. Registers generators and SMTP protocols into their registries, initializes `FluentManager`, builds `PandorasBox` (the DI container passed to every view), and handles routing via a `match page.route` block.

**`src/ui/routes/`** — one file per page: `root`, `application`, `settings`, `about`, `author`, `error404`. Each exports a `ROUTE` constant and a `build_view()` function.

**`PandorasBox`** (in `src/ui/utils/models.py`) — a dataclass holding all shared services: `storage` (FletStorage), `generator` (GlobalGenerator), `fluent` (FluentManager), `ga` (MeasurementAPI), `name_creator`, optional `saver`, optional `sender`. Passed as `box` into every view builder.

## Key Conventions

**Localization first** — never hardcode UI strings. Add a key to the appropriate `.ftl` file in `src/assets/locales/<locale>/` (`ui.ftl`, `mail.ftl`, or `logs.ftl`) and retrieve it with `box.fluent.get("key")` or `box.fluent.get("key", param=value)`.

**Registry pattern** — to add a new document format, subclass `BaseTemplateManager` in `src/core/`, then register it in `src/ui/main.py`:
```python
GlobalGenerator.register(FileType.PDF, MyPdfManager)
```
Same pattern for SMTP protocols via `EmailManager.register(SMTPProtokol.X, MyClass)`.

**Docker versioning** — `APP_VERSION` in the root `.env` tags the image. `pull_policy: missing` means the image is never auto-pulled or rebuilt if it already exists locally; use `--build` explicitly when you want a new build.

**No database** — persistence is client-side only via `FletStorage` (SharedPreferences wrapper). Stored keys: `client_id`, `officer_name`, `officer_position`, `officer_email`.
