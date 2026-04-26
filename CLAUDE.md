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

## Testing

The project has 38 tests covering core functionality:

**`tests/test_appeal_request.py`** — 7 tests for the `AppealRequest` Pydantic model:
- Required field validation
- Optional field defaults
- Automatic `created_at` timestamp
- `get_context()` method with date formatting

**`tests/test_email_manager.py`** — 4 tests for the `EmailManager` registry:
- Protocol registration and retrieval
- Error handling for unregistered protocols
- Overwrite behavior
- Delegation to protocol implementations

**`tests/test_files_utils.py`** — 12 tests for file utilities in `src/utils/files.py`:
- MIME type detection (`get_mime`)
- Unique filename generation (`create_file_name`)
- File-to-buffer conversion (`file_to_buffer`)
- Buffer-to-file saving (`save`)
- Date-based directory creation (`create_path_dir`)

**`tests/test_localization.py`** — 5 tests for `FluentManager`:
- UI, mail, and logs localization
- Fallback mechanism
- Locale directory validation

**`tests/test_message_factory.py`** — 10 tests for `AppealMessageFactory`:
- Email headers (From, To, Subject, Cc, Bcc)
- Attachment handling
- Multiple recipient support

**Test coverage:** 445 lines of test code, 38 tests total. Run with `pytest` or `uv run pytest`.

## Modules Not Yet Covered by Tests

The following modules are currently untested and would benefit from test coverage:

**`src/core/`** — Document generation and SMTP implementations:
- `doc_manager.py` — `DocManager` for DOCX file generation
- `txt_manager.py` — `TxtManager` for text file generation
- `smtp_implementations.py` — `SMTPSenderTLS` and `SMTPSenderSSL` classes

**`src/abstract/`** — Base classes and their implementations:
- `application_generator.py` — `BaseTemplateManager` and `GlobalGenerator` registry
- `application_name_creator.py` — `BaseNameCreator` and `NameCreator`
- `application_sender.py` — `BaseSender` and `EmailSender`
- `application_saver.py` — `BaseSaver` and `FileSaver`

**`src/models/`** — Enums and custom errors:
- `email_errors.py` — `EmailFileNotFoundError` and `EmailSendError`
- `smtp.py` — `SMTPProtokol` enum
- `file_type.py` — `FileType` enum
- `logging.py` — `LoggingLevel` enum

**`src/config/`** — Pydantic settings classes:
- `app.py` — Main application settings
- `email_sender.py` — Email sender configuration
- `email_recipient.py` — Email recipient configuration
- `google_analytics.py` — Google Analytics settings
- `server.py` — Server settings

**`src/utils/`** — Utility functions:
- `emails.py` — `add_attachment_from_buffer` and `add_attachment_from_file`
- `measurement_api.py` — `MeasurementAPI` for Google Analytics integration

**`src/ui/`** — UI components and routing (lower priority, requires Flet mocking):
- `main.py` — Route handling and app initialization
- `routes/application.py` — Application form page
- `routes/settings.py` — Settings page
- `routes/about.py` — About page
- `routes/author.py` — Author page
- `routes/error404.py` — 404 error page
- `routes/root.py` — Root page
- `utils/models.py` — `PandorasBox` and `Officer` dataclasses
- `utils/elements.py` — UI element factories (`back_button`, `app_bar`, `link`)
- `utils/style.py` — Style settings

**Priority for testing:** Core business logic (`src/core/`, `src/abstract/`, `src/utils/`) should be tested first, followed by configuration (`src/config/`). UI components (`src/ui/`) are lower priority as they require extensive mocking of Flet framework.
