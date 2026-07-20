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
│   ├── build-release.yml   # CI/CD — tests, build, release on merge to main
│   └── pr-check.yml        # CI/CD — tests on PR to latest/*
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

## Branch hierarchy

```
lower:  patch/* , fix/* , feature/*   (deleted once merged to mid)
mid:    dev/* , latest/*               (version lives in dev/* branch name)
high:   main                           (triggers build + release on merge)
```

- **Lower** branches (`patch/*`, `fix/*`, `feature/*`) are temporary — deleted once merged into `dev/*` or `latest/*`.
- **Mid** branches (`dev/*`, `latest/*`) hold the version number in the branch name (e.g. `dev/1.2.3`). `latest/*` is the staging/pre-release branch.
- **High** (`main`) is production. When `latest/*` is approved and merged to `main`, the full build + release pipeline runs.

## CI/CD Workflows

### pr-check.yml — PR validation (dev/* → latest/*)

Triggered on **pull requests targeting `latest/*`**. Runs tests only:
- If tests pass, the PR status check passes (no auto-merge).
- If tests fail, a GitHub Issue is created with the JUnit output.

### build-release.yml — Release (push to main)

Triggered on **push to `main`** (typically from merging `latest/*`). Runs tests, builds, and releases.

**Version detection** (in `scripts/ci_build.py`), in priority order:
1. **PR title in the merge commit body** — e.g. merging a PR titled `Release v1.0.1` → extracts `1.0.1`
2. **Branch name version** — e.g. `dev/1.0.1` in the merge branch line → extracts `1.0.1`
3. **Latest git tag** — fallback if neither is found

**Bump rules** (applied after selecting the base version):
- `major/*` → **major** bump (1.0.0 → 2.0.0)
- `feature/*` or `feat/*` → **minor** bump (1.0.0 → 1.1.0)
- `dev/*`, `fix/*`, `patch/*`, `latest`, or anything else → **patch** bump (1.0.0 → 1.0.1)

**Atomic release**: Tag is created by `ncipollo/release-action` (via `commit: ${{ github.sha }}`) at the same time as the release. No separate `git tag`/`git push origin <tag>` step. This avoids orphan tags when the release step fails — re-running the workflow will produce the **same version** (since no tag was pushed), and the release creation will succeed.
