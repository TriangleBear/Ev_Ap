# Ev_Ap

**Ev_Ap (Event Attendance)** is a desktop application for managing event attendance via RFID scanning. It supports a **dual-backend** architecture — local **SQLite** or cloud **Google Sheets** via a Google Apps Script API.

## Features

- **Member Registration:** Register members with RFID, ID, name, student number, program, and year.
- **Event Management:** Create events — each event gets its own Google Sheet file (in GS mode) or a SQLite table (in local mode).
- **Attendance Tracking:** Scan RFID cards to mark attendance with 15-second dedup protection.
- **Background Scanning:** RFID scans run in a background thread so the UI stays responsive with a loading indicator.
- **Dual Database Backend:** Switch between local SQLite and Google Sheets in Settings.
- **Data Export:** Export attendance data to CSV or Excel.

## Requirements

- Python 3.8+
- CustomTkinter (UI)
- IceCream (debugging)
- pandas (export)
- requests (Google Sheets API)

## Installation

```bash
git clone https://github.com/TriangleBear/Ev_Ap
cd Ev_Ap
pip install -r ORG-RFID-EVENTS/requirements.txt
python ORG-RFID-EVENTS/App/main.py
```

## Usage

### Local Mode (SQLite — default)
Works out of the box with no setup. All data stored locally in `Ev_Ap.db`.

### Google Sheets Mode
1. Open the Google Sheet you want to use → Extensions → Apps Script → paste `App/database/gsheet_api.gs`.
2. Run the **Ev_Ap → Configure Spreadsheet** menu item to set your sheet.
3. Deploy → New deployment → Web App (Execute as: Me, Access: Anyone).
4. Copy the deployment URL.
5. In Ev_Ap → Settings → Database → paste the URL, switch to **Google Sheets**, click Apply.

Each event creates a separate Google Sheet file (`Ev_Ap - <event_name>`) in your Drive.

### Registering a Member
Navigate to Members → Register New Member → fill in details → Submit.

### Creating an Event
Navigate to Events → Create New Event → enter name → Submit.

### Marking Attendance
Open an event → scan RFID card. The scan runs in the background with a loading spinner.

### Exporting Data
Open an event → click Export → choose CSV or Excel.

## CI/CD Pipeline

The project uses **GitHub Actions** for continuous integration and delivery. On every push/merge to `main`, the pipeline automatically:

1. **Runs tests** — if any test fails, a GitHub Issue is created with the failure details and the build is aborted.
2. **Determines the new version** — parses the merged branch name and bumps the version accordingly:
   - `major/*` — bumps major (`v3.3.1` → `v4.0.0`)
   - `feature/*` or `feat/*` — bumps minor (`v3.3.1` → `v3.4.0`)
   - `dev/*`, `fix/*`, `patch/*`, or anything else — bumps patch (`v3.3.1` → `v3.3.2`)
3. **Updates the version** in `App/views/about_view.py` and commits it.
4. **Builds a Windows `.exe`** with PyInstaller.
5. **Creates a git tag** and a **GitHub Release** with the `.exe` attached and release notes auto-generated from commits since the last tag.

> **Note:** Branch names **must** follow the convention above for proper version bumping. The merged source branch is extracted from the merge commit message.

## Project Structure

```
ORG-RFID-EVENTS/App/
├── main.py              # Entrypoint
├── rfid_app.py          # MainApp — wires DB, managers, views
├── database/
│   ├── dblite.py        # DBActions (static facade) + Database wrapper (dual-backend)
│   ├── sqlite_db.py     # Local SQLite connection / schema
│   ├── sheet_db.py      # Google Sheets API client (HTTP → Google Apps Script)
│   ├── config.py        # ev_ap_config.json read/write
│   └── gsheet_api.gs    # Google Apps Script source — deploy as Web App
├── managers/
│   ├── event_manager.py # Event creation flow
│   ├── member_manager.py # Member registration flow
│   └── table_manager.py  # Event table UI, threaded RFID scan, export
├── views/               # Lazy-loaded CustomTkinter views (7 views)
└── TEST/                # pytest tests
```

## License

MIT — see [LICENSE](LICENSE).
