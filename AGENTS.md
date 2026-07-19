# AGENTS.md — RFID App (Ev_Ap)

## Quick start

```bash
# From workspace root
pip install -r ORG-RFID-EVENTS/requirements.txt
python ORG-RFID-EVENTS/App/main.py
```

Virtual env: `.venv\Scripts\activate` (Windows).

## Project structure

```
ORG-RFID-EVENTS/
├── .github/workflows/
│   └── build-release.yml   # CI/CD — tests, build, release on merge to main
├── scripts/
│   └── ci_build.py         # Version bump, spec gen, release notes
├── App/
│   ├── main.py              # Entrypoint — imports and runs MainApp
│   ├── rfid_app.py          # MainApp: wires DB, managers, views
│   ├── database/
│   │   ├── dblite.py        # DBActions (static facade) + Database wrapper (dual-backend)
│   │   ├── sqlite_db.py     # Raw SQLite connection / schema
│   │   ├── sheet_db.py      # Google Sheets API client (HTTP → Google Apps Script)
│   │   ├── config.py        # ev_ap_config.json read/write (db_mode, gsheet_api_url)
│   │   └── gsheet_api.gs    # Google Apps Script source — deploy as Web App
│   ├── managers/
│   │   ├── event_manager.py # Event creation flow
│   │   ├── member_manager.py # Member registration flow
│   │   └── table_manager.py # Event table UI, RFID scan, export
│   ├── views/               # Lazy-loaded CustomTkinter views (7 views)
│   └── TEST/                # pytest tests
└── requirements.txt
```

## Key architecture facts

- **Dual-backend DB**: `DBActions` routes each call to either `SQLiteDB` (local) or `SheetDB` (Google Sheets) based on `ev_ap_config.json`'s `db_mode` setting.
- **Google Sheets integration**: Deploy `database/gsheet_api.gs` as a Google Apps Script Web App, paste the URL in Settings → Database → Google Sheets API URL, then switch the mode toggle and Apply.
  - **Main spreadsheet** (configured in ScriptProperties): `Members` sheet + `Events` registry sheet.
  - **Each event** creates its **own separate Google Sheet file** (named `Ev_Ap - <event_name>`) with an `Attendance` sheet.
  - Deleting an event moves its spreadsheet to trash and removes the registry entry.
- **Config file**: `ev_ap_config.json` is auto-created in the working directory. Fields: `db_mode` ("sqlite"\|"gsheet"), `gsheet_api_url`.
- **Views are lazy-loaded**: imported and initialized only on first navigation via `MainApp.init_view()`.
- **Points system**: `DBActions.add_points()`, `get_member_points()`, `redeem_points()` are implemented for both SQLite and SheetDB backends. `SQLiteDB.initialize_db()` adds a `points` column automatically.
- **15-second RFID dedup**: `member_manager.rfid_cache` prevents re-scanning the same tag within 15 seconds.
- **Threaded RFID scan**: `DBActions.scan_attendance()` batches member_exists + check_attended + record into one API call (GS mode) and runs in a background thread with a loading spinner in the UI.

## Tests

```bash
# Run from ORG-RFID-EVENTS/App/ so sys.path appending works
cd ORG-RFID-EVENTS/App
pytest TEST/
# Or from root:
pytest ORG-RFID-EVENTS/App/TEST/
```

- Tests use `tmp_path` + `monkeypatch.chdir(tmp_path)` for DB isolation.
- Tests append `..` to `sys.path` to import from the App package — may need `cd App` first.
- `test_table_manager_pytest.py` uses `DummyApp`/`DummyWindow`/`DummyEntry` mocks.
- 7 tests total across 3 files; all should pass.

## Gotchas

- **Security**: `.vscode/settings.json` contains live MySQL credentials (Aiven Cloud) — do not commit.
- **`.gitignore`** is a standard Python gitignore (not just `*`). New files in `.github/workflows/` and `scripts/` are tracked normally.
- **IceCream debug**: `ic()` calls are used throughout for debugging output.
- **Appearance modes**: Light/Dark/System via `customtkinter`.
- **Export**: CSV/Excel via `pandas` with `filedialog.asksaveasfilename`.
- **CI/CD**: GitHub Actions workflow at `.github/workflows/build-release.yml`. Triggered on push to `main`. Runs tests, bumps version per branch name, builds PyInstaller `.exe`, creates GitHub Release.
- **Version bump rules**: `major/*` → major, `feature/*` or `feat/*` → minor, anything else (`dev/*`, `fix/*`, `patch/*`) → patch.
- **Issue titles** on test failure include the commit SHA to avoid duplicates.
