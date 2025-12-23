import os
import sys
import sqlite3
import pytest

# Ensure the App directory is on sys.path so imports work during pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dblite import Database, DBActions


def setup_db(tmp_path, monkeypatch):
    # Run tests in isolated temp dir so the hardcoded AHO_MEMBER.db is created there
    monkeypatch.chdir(tmp_path)
    db = Database(app=None)
    DBActions.set_db_instance(db)
    db.initialize_db()
    return db


def test_member_register_and_exists(tmp_path, monkeypatch):
    db = setup_db(tmp_path, monkeypatch)

    # Register a member
    result = DBActions.member_register('rfid-123', 'M001', 'Alice Smith', 'S001', 'CS', '1')
    assert result == 0

    # Verify member exists
    member = DBActions.member_exists('rfid-123')
    assert member is not None
    assert member['memberid'] == 'M001'
    assert member['name'] == 'Alice Smith'


def test_points_add_get_redeem(tmp_path, monkeypatch):
    db = setup_db(tmp_path, monkeypatch)

    DBActions.member_register('r-1', 'M100', 'Bob', 'S100', 'Eng', '2')

    # Add points
    assert DBActions.add_points('r-1', 25) == 0
    pts = DBActions.get_member_points('r-1')
    assert pts == 25

    # Redeem points
    assert DBActions.redeem_points('r-1', 10) == 0
    pts = DBActions.get_member_points('r-1')
    assert pts == 15


def test_event_table_and_attendance(tmp_path, monkeypatch):
    db = setup_db(tmp_path, monkeypatch)

    # Register a member
    DBActions.member_register('r-ev', 'MEV', 'Carol', 'S200', 'Bio', '3')

    # Create event table and check it exists
    assert DBActions.create_event_table('Test Event') == 0
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Test_Event'")
    assert cur.fetchone() is not None

    # Record attendance
    assert DBActions.attendance_member_event('Test_Event', 'r-ev') == 0
    # Check attendance recorded
    attended = DBActions.member_attended_event('Test_Event', 'r-ev')
    assert attended is True

    # Fetch table data
    rows = DBActions.fetch_table_data('Test_Event')
    assert any(r['memberid'] == 'MEV' for r in rows)


def test_list_tables_filters_members(tmp_path, monkeypatch):
    db = setup_db(tmp_path, monkeypatch)
    # Create an event table
    DBActions.create_event_table('Another')
    tables = DBActions.list_tables()
    # Members should be filtered out; 'Another' should appear
    assert 'Members' not in tables
    assert 'Another' in tables
