# Usage & Development Notes

## Running Locally

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r ORG-RFID-EVENTS/requirements.txt
python ORG-RFID-EVENTS/App/main.py
```

## Database Backends

### SQLite (Default)
Runs out of the box. Database file: `Ev_Ap.db` in the working directory.

### Google Sheets
The app can use Google Sheets as its database via a Google Apps Script Web API.

**Setup steps:**
1. Open your target Google Sheet → Extensions → Apps Script.
2. Paste the contents of `App/database/gsheet_api.gs` → save.
3. Run the **Ev_Ap → Configure Spreadsheet** menu item to link the sheet.
4. Deploy → New deployment → Web App (Execute as: Me, Access: Anyone).
5. Copy the deployment URL.
6. In Ev_Ap → Settings → Database, paste the URL, switch to "Google Sheets", click Apply.

**Architecture:**
- The main spreadsheet stores `Members` and `Events` (registry) sheets.
- Each event creates its **own separate Google Sheet file** (`Ev_Ap - <event_name>`).
- Deleting an event moves its spreadsheet to Drive trash and removes the registry entry.

## Code Structure

- `App/rfid_app.py` — application bootstrap and UI flow.
- `App/database/dblite.py` — `DBActions` facade routes calls to SQLite or Google Sheets.
- `App/database/sqlite_db.py` — local SQLite schema and connections.
- `App/database/sheet_db.py` — HTTP client for the Google Apps Script API.
- `App/database/config.py` — reads/writes `ev_ap_config.json` (db_mode, gsheet_api_url).
- `App/database/gsheet_api.gs` — deployable Apps Script (CRUD + event spreadsheets).
- `App/managers/` — event, member, and table management logic.
- `App/views/` — CustomTkinter UI views (lazy-loaded).

## Testing

```bash
pip install pytest
pytest ORG-RFID-EVENTS/App/TEST
```

Tests use `tmp_path` + `monkeypatch.chdir` for DB isolation.
