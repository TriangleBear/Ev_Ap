RFID App — SQLite migration and usage
=========================================

Summary
-------
This repository is an events attendance system (RFID App). It has been migrated to use SQLite exclusively; all cloud/MySQL support was removed to simplify deployment and maintenance.

Directory structure (key parts)
------------------------------
- App/: main application code
  - dblite.py — database abstraction now backed by `SQLiteDB`
  - sqlite_db.py — SQLite database helper (creates `MEMBER.db`)
  - rfid_app.py — main GUI application (starts directly with SQLite)
  - TEST/: pytest suites
- ORG-RFID-EVENTS/README.md — original project README (unchanged)

What changed
------------
- Removed cloud/MySQL branches and UI options.
- `Database` always uses `SQLiteDB` now.
- `SettingsView` and startup flow simplified to SQLite-only.
- Added pytest tests covering DB layer and `TableManager` attendance logic.

Quick start (Windows, cmd)
--------------------------
From the workspace root (where this file lives), run:

1) Open Command Prompt and change to project folder:

```bat
cd "RFID App"
```

2) Activate the virtual environment:

```bat
.venv\Scripts\activate
```

3) Install dependencies (if needed):

```bat
pip install -r App\requirements.txt
```

4) Start the application GUI:

```bat
python App\main.py
```

Notes about the database
------------------------
- The app uses a local SQLite database file named `MEMBER.db` created in the working directory where you run the app.
- `sqlite_db.py` will create the file and the `Members` table (adds `points` column if needed).
- All event tables are created dynamically with names using underscores (spaces converted to `_`).

Running tests (pytest)
----------------------
Tests are under `App/TEST/`. Example commands:

Run all tests:
```bat
pytest -q
```

Run a single test file:
```bat
pytest App/TEST/test_db_full_pytest.py -q
```

Run a single test function:
```bat
pytest App/TEST/test_db_full_pytest.py::test_member_register -q
```

Test notes:
- Tests add the `App` folder to `sys.path` so they can import project modules when executed from the repository root.
- Tests run in temporary directories (where applicable) so they don't modify your real DB file.

Troubleshooting
---------------
- Module import errors during pytest? Ensure you're running `pytest` from the project root and that `.venv` is activated so packages (pytest) are available.
- If `MEMBER.db` isn't created, ensure your working directory is writable.

Next steps / optional improvements
---------------------------------
- Remove the unused `cloud_db.py` and any cloud credentials stored in `creds.py` if you do not plan to reintroduce cloud support.
- Add unit tests for the GUI view classes using a GUI test helper or mock objects.
- Add a contribution section to `ORG-RFID-EVENTS/README.md` describing development workflow.

If you want, I can:
- Run the test suite and fix any failures.
- Create a consolidated `README.md` in the repo root summarizing usage.
- Remove the leftover `cloud_db.py` and `creds` entries.

