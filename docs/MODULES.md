# Module Index and Summaries

This file contains short summaries for the main modules in the application. Use this as a starting point for a fuller API reference.

- `App/main.py` — Entry point that creates and runs the `MainApp`.
- `App/rfid_app.py` — Implements `MainApp`.
  - UI bootstrap (CustomTkinter) and main layout.
  - Background initialization of the `Database`.
  - Lazy view initialization and navigation for Home, Events, Members, Reports, Settings, Help, About.
- `App/database/dblite.py` — `DBActions` static helper methods for database operations and `Database` wrapper.
  - Member registration, event table creation, attendance recording.
  - Contains `Database` which wraps `SQLiteDB` and exposes `get_db_connection` and `initialize_db`.
- `App/database/sqlite_db.py` — `SQLiteDB` class that handles SQLite file, connections, and schema initialization.
- `App/managers/event_manager.py` — `EventManager` to create events and event windows.
- `App/managers/member_manager.py` — `MemberManager` for registering members.
- `App/managers/table_manager.py` — Manages table-related UI and interactions.
- `App/theme/theme_manager.py` — Theme configuration and utilities.
- `App/views/home_view.py`, `App/views/events_view.py`, `App/views/members_view.py`, `App/views/reports_view.py`, `App/views/settings_view.py`, `App/views/help_view.py`, `App/views/about_view.py` — UI views for the main sections.

Tests
- `App/TEST/` contains unit tests; expand to cover critical DB operations and managers.

How to contribute module docs
1. Open the target module (e.g. `App/events_view.py`).
2. Add/complete the module docstring describing responsibilities and public API (classes/functions).
3. Add a short section here summarizing the public classes and important methods.

Example entry (add to this file):

```
App/events_view.py
- `EventsView` — Displays event listings and controls for marking attendance.
- Public methods:
  - `refresh()` — reloads event data from DB.
  - `mark_attendance(rfid)` — record attendance for an RFID string.
```
