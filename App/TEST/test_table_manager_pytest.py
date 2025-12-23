import os
import sys
import time
import sqlite3
import pytest

# Ensure App directory is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dblite import Database, DBActions
import table_manager
from table_manager import TableManager


class DummyEntry:
    def __init__(self, value):
        self._value = value
        self.inserted = []
        self.deleted = []

    def get(self):
        return self._value

    def delete(self, a, b=None):
        self.deleted.append((a, b))

    def insert(self, pos, val):
        self.inserted.append((pos, val))


class DummyWindow:
    def __init__(self):
        self._exists = True
        self.after_calls = []

    def winfo_exists(self):
        return self._exists

    def after(self, ms, func):
        # call immediately for tests
        self.after_calls.append((ms, func))
        func()

    def destroy(self):
        self._exists = False


class DummyApp:
    def __init__(self, db):
        self.root = type('R', (), {'clipboard_clear': lambda self: None, 'clipboard_append': lambda self, t: None, 'update': lambda self: None})()
        self.preloaded_data = {}
        self.member_manager = type('M', (), {'rfid_cache': {}})()
        self.event_manager = type('E', (), {'points_per_event': {}})()
        self.db = db


@pytest.fixture
def setup_db(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    db = Database(app=None)
    DBActions.set_db_instance(db)
    db.initialize_db()
    return db


def test_rfid_scan_event_records_attendance_and_adds_points(setup_db):
    db = setup_db
    app = DummyApp(db)
    tm = TableManager(app)

    # create event table and register member
    table_name = 'Event1'
    DBActions.create_event_table(table_name)
    DBActions.member_register('rf-1', 'ID1', 'Test', 'S1', 'Prog', '1')

    entry = DummyEntry('rf-1')
    window = DummyWindow()

    # ensure event has points mapping
    app.event_manager.points_per_event[table_name] = 5

    # initial attendance check
    assert not DBActions.member_attended_event(table_name, 'rf-1')

    # call scan
    tm.rfid_scan_event(entry, window, table_name, lambda data: None, [])

    # now attendance should be recorded
    assert DBActions.member_attended_event(table_name, 'rf-1') is True

    # points should be added
    pts = DBActions.get_member_points('rf-1')
    assert pts == 5


def test_rfid_scan_event_ignores_quick_rescan(setup_db):
    db = setup_db
    app = DummyApp(db)
    tm = TableManager(app)

    table_name = 'Event2'
    DBActions.create_event_table(table_name)
    DBActions.member_register('rf-2', 'ID2', 'Test2', 'S2', 'Prog', '1')

    entry = DummyEntry('rf-2')
    window = DummyWindow()

    # Simulate recent scan
    app.member_manager.rfid_cache['rf-2'] = time.time()

    # Call scan -- should early-return and not record attendance
    tm.rfid_scan_event(entry, window, table_name, lambda data: None, [])

    assert DBActions.member_attended_event(table_name, 'rf-2') is False
