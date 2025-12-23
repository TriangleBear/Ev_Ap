# Usage & Development Notes

Running locally

1. Create and activate a venv (Windows example):

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r ORG-RFID-EVENTS/requirements.txt
python ORG-RFID-EVENTS/App/main.py
```

Where to start reading code
- `App/rfid_app.py` — application bootstrap and UI flow.
- `App/dblite.py` / `App/sqlite_db.py` — database layer and schema.

Testing
- Run tests under `App/TEST/` with pytest (install pytest first):

```bash
pip install pytest
pytest ORG-RFID-EVENTS/App/TEST
```

Recommendations
- Improve docstrings in each module and class.
- Add inline examples for key public methods (e.g., `DBActions.*`).
- Consider adding Sphinx or MkDocs config to auto-build API docs.
