# Module Index and Summaries

This file contains short summaries for the main modules in the application. Use this as a starting point for a fuller API reference.

- `App/main.py` — Entry point that creates and runs the `MainApp`.
- `App/rfid_app.py` — Implements `MainApp`.
  - UI bootstrap (CustomTkinter) and main layout.
  - Background initialization of the `Database`.
  - Lazy view initialization and navigation for Home, Events, Members, Reports, Settings, Help, About.
- `App/dblite.py` — `DBActions` static helper methods for database operations and `Database` wrapper.
  - Member registration, event table creation, attendance recording, points operations.
  - Contains `Database` which wraps `SQLiteDB` and exposes `get_db_connection` and `initialize_db`.
- `App/sqlite_db.py` — `SQLiteDB` class that handles SQLite file, connections, and schema initialization.
- `App/event_manager.py` — `EventManager` to create events and event windows.
- `App/member_manager.py` — `MemberManager` for registering members and redeeming points.
- `App/table_manager.py` — (TODO) manages table-related UI and interactions.
- `App/home_view.py`, `App/events_view.py`, `App/members_view.py`, `App/reports_view.py`, `App/settings_view.py`, `App/help_view.py`, `App/about_view.py` — UI views for the main sections. (Populate per-file summaries.)
- `App/Menu_BT.py` — Theme and menu utilities.
- `App/cloud_db.py` — (Present but unused when running SQLite-only mode.)

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
