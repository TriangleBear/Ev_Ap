# Development Guide

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- VS Code, PyCharm, or similar

### Setup

```bash
git clone https://github.com/TriangleBear/Ev_Ap.git
cd Ev_Ap
python -m venv .venv
.venv\Scripts\Activate
pip install -r ORG-RFID-EVENTS/requirements.txt
python ORG-RFID-EVENTS/App/main.py
```

## Architecture Overview

### Dual-Backend Database

The app supports two database backends, switchable from Settings:

1. **SQLite** (default) — local file `Ev_Ap.db`, no setup required.
2. **Google Sheets** — via a Google Apps Script Web API.

The routing happens in `App/database/dblite.py`:
- `DBActions` is a static facade. Each method checks `db_mode` from `ev_ap_config.json`.
- If `"sqlite"`, it uses `SQLiteDB` directly.
- If `"gsheet"`, it delegates to `SheetDB` which makes HTTP requests to the deployed script.

### Adding a New Database Operation

1. Add the method to `SheetDB` in `sheet_db.py` (GS API call).
2. Add the corresponding action to `gsheet_api.gs` (server-side logic).
3. Add the method to `DBActions` in `dblite.py` with the `if db_mode == 'gsheet'` branch.
4. For SQLite, the existing raw-SQL branch works.

### UI Threading

RFID scans run in a background thread (`threading.Thread`) to keep the UI responsive:
- `table_manager.py::rfid_scan_event` starts a daemon thread.
- The thread calls `DBActions.scan_attendance()` (batched single API call in GS mode).
- UI updates happen via `window.after(0, callback)`.

## Testing

```bash
# From App directory
cd ORG-RFID-EVENTS/App
pytest TEST/

# Or from root
pytest ORG-RFID-EVENTS/App/TEST/
```

Tests use `tmp_path` + `monkeypatch.chdir` for isolated DB files.

## CI/CD Pipeline

The repository uses **GitHub Actions** (`.github/workflows/build-release.yml`) for automated builds and releases.

### Workflow trigger

- **Event:** push/merge to `main`
- **Runner:** `windows-latest` (builds native Windows `.exe`)

### What happens

1. **Tests** run via pytest. If they fail, a GitHub Issue is auto-created with JUnit output and the pipeline stops.
2. **Version bump** is determined from the merged branch name:
   - `major/*` → major bump
   - `feature/*` or `feat/*` → minor bump
   - `dev/*`, `fix/*`, `patch/*` → patch bump
3. **PyInstaller** builds `Attendance_App_<version>.exe`.
4. **About view** is updated and committed.
5. **Git tag** and **GitHub Release** are created with the `.exe` asset and auto-generated release notes.

### Helper script

`scripts/ci_build.py` handles version parsing, about_view.py updates, and release note generation. It is called by the workflow but can also be run manually for testing:

```bash
python scripts/ci_build.py "Merge pull request #123 from user/feature/my-feature"
```

## Google Apps Script Development

1. Edit `App/database/gsheet_api.gs`.
2. Open your Google Sheet → Extensions → Apps Script → paste updated code.
3. Deploy → Manage deployments → redeploy.
4. Copy new deployment URL if it changed.

### Testing the API locally

```python
from database.sheet_db import SheetDB
db = SheetDB(api_url='https://script.google.com/.../exec')
config = db.get_config()
print(config)
```

## Code Style

- PEP 8.
- IceCream (`ic()`) for debug output.
- No docstrings required for internal methods (keep code concise).

## Pull Requests

1. Fork → branch → commit → push → PR.
2. Ensure existing tests still pass.
