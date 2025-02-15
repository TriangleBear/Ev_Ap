import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dblite import DBActions, Database


class TestDBActions(unittest.TestCase):
    @patch('dblite.Database.get_db_connection')
    def test_member_register(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = DBActions.member_register('123456', 'M001', 'John Doe', 'S123', 'CS', '2023')
        self.assertEqual(result, 0)
        mock_cursor.execute.assert_called_once()
        args, kwargs = mock_cursor.execute.call_args
        self.assertIn('INSERT INTO Members (rfid, memberid, name, student_num, program, year, date_registered)', args[0])
        self.assertEqual(args[1], ('123456', 'M001', 'John Doe', 'S123', 'CS', '2023', unittest.mock.ANY))

    @patch('dblite.Database.get_db_connection')
    def test_member_exists(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'memberid': 'M001', 'name': 'John Doe', 'student_num': 'S123'}

        result = DBActions.member_exists('123456')
        self.assertIsNotNone(result)
        self.assertEqual(result['memberid'], 'M001')
        mock_cursor.execute.assert_called_once_with("SELECT memberid, name, student_num FROM Members WHERE rfid = ?", ('123456',))

    @patch('dblite.Database.get_db_connection')
    def test_add_points(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = DBActions.add_points('123456', 10)
        self.assertEqual(result, 0)
        mock_cursor.execute.assert_called_once_with("UPDATE Members SET points = points + ? WHERE rfid = ?", (10, '123456'))
        mock_conn.commit.assert_called_once()

    @patch('dblite.Database.get_db_connection')
    def test_get_member_points(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'points': 50}

        result = DBActions.get_member_points('123456')
        self.assertEqual(result, 50)
        mock_cursor.execute.assert_called_once_with("SELECT points FROM Members WHERE rfid = ?", ('123456',))

    @patch('dblite.Database.get_db_connection')
    def test_redeem_points(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = DBActions.redeem_points('123456', 20)
        self.assertEqual(result, 0)
        mock_cursor.execute.assert_called_once_with("UPDATE Members SET points = points - ? WHERE rfid = ?", (20, '123456'))
        mock_conn.commit.assert_called_once()

if __name__ == "__main__":
    unittest.main()
