# Module Index and Summaries

## Entry Point

- **`App/main.py`** — Creates and runs `MainApp`.

## Core

- **`App/rfid_app.py`** — `MainApp` class. UI bootstrap (CustomTkinter), background DB initialization, lazy view loading, navigation.

## Database Layer

- **`App/database/dblite.py`**
  - `DBActions` — static facade. Each method checks `db_mode` and routes to either `SQLiteDB` or `SheetDB`.
  - `Database` — wrapper that holds either backend, provides `initialize_db()`, `get_db_connection()`, `switch_mode()`.
  - Key methods: `member_register`, `member_exists`, `create_event_table`, `attendance_member_event`, `scan_attendance` (batched), `fetch_table_data`, `delete_event_table`.

- **`App/database/sqlite_db.py`**
  - `SQLiteDB` — raw SQLite connections, schema init (`Members` table), `Ev_Ap.db`.

- **`App/database/sheet_db.py`**
  - `SheetDB` — HTTP client for Google Apps Script Web API.
  - All methods mirror `DBActions` but talk to the GS API via `requests`.
  - Batched `scan_attendance()` reduces 3 round-trips to 1.

- **`App/database/config.py`**
  - Reads/writes `ev_ap_config.json`.
  - Fields: `db_mode` ("sqlite" | "gsheet"), `gsheet_api_url`.

- **`App/database/gsheet_api.gs`**
  - Google Apps Script source. Deploy as Web App.
  - Handles: members CRUD, event spreadsheet creation, attendance recording.
  - Each event creates a separate Google Sheet file in Drive.

## Managers

- **`App/managers/event_manager.py`** — `EventManager`: create event dialog and submission.
- **`App/managers/member_manager.py`** — `MemberManager`: member registration with RFID cache (15s dedup).
- **`App/managers/table_manager.py`** — `TableManager`: event table window, threaded RFID scan with loading spinner, search/filter, export.

## Views (lazy-loaded)

- `App/views/home_view.py` — Dashboard.
- `App/views/events_view.py` — Event list, create/delete.
- `App/views/members_view.py` — Member list.
- `App/views/reports_view.py` — Attendance reports, export.
- `App/views/settings_view.py` — Appearance mode, database mode toggle, GS API URL config, test connection, set spreadsheet.
- `App/views/help_view.py` — Help page.
- `App/views/about_view.py` — About page.

## Theme

- **`App/theme/theme_manager.py`** — Theme configuration and utilities.

## Tests

- **`App/TEST/`** — pytest unit tests for DB operations and managers.
