import os
import sys
import sqlite3
import pytest

# Ensure the App directory is on sys.path so imports work during pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlite_db import SQLiteDB


def test_initialize_db_creates_file_and_members_table(tmp_path, monkeypatch):
    # Run in isolated temporary directory so tests don't touch real DB
    monkeypatch.chdir(tmp_path)

    db = SQLiteDB()
    # Should create the AHO_MEMBER.db file and Members table
    db.initialize_db()

    db_file = tmp_path / 'AHO_MEMBER.db'
    assert db_file.exists(), "Database file was not created"

    # Verify Members table exists
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Members'")
    assert cursor.fetchone() is not None, "Members table not found in database"

    # fetch_all_data should return at least the Members table
    data = db.fetch_all_data()
    assert 'Members' in data, "fetch_all_data did not include 'Members' table"

    conn.close()
