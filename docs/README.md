# Ev_Ap — Documentation

Desktop attendance application with **dual-backend** database: local **SQLite** or cloud **Google Sheets** via a Google Apps Script Web API.

## Purpose

- Track event attendance using RFID tags.
- Manage members, create events, and generate reports.
- Switch between local (SQLite) and cloud (Google Sheets) database backends from Settings.

## Contents

- `../App/` — application source code and UI views.
- `../App/database/` — database layer: `dblite.py` (facade), `sqlite_db.py` (local), `sheet_db.py` (Google Sheets), `config.py`, `gsheet_api.gs` (deployable script).
- `../App/managers/` — event, member, and table management logic.
- `../App/views/` — CustomTkinter UI views (lazy-loaded).
- `../App/TEST/` — unit tests.
- `./MODULES.md` — module index and summaries.
- `./USAGE.md` — setup and development notes.

## Quick Start

```bash
pip install -r ORG-RFID-EVENTS/requirements.txt
python ORG-RFID-EVENTS/App/main.py
```

See `USAGE.md` for Google Sheets setup instructions.
