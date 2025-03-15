import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rfid_app import MainApp


class TestRFIDApp(unittest.TestCase):
    @patch('customtkinter.CTk')
    @patch('customtkinter.CTkOptionMenu')
    @patch('customtkinter.CTkButton')
    @patch('CTkMessagebox.CTkMessagebox')
    @patch('customtkinter.StringVar')
    def test_main_app_initialization(self, mock_stringvar, mock_messagebox, mock_button, mock_optionmenu, mock_ctk):
        # Mock the methods and attributes used in MainApp
        mock_root = MagicMock()
        mock_ctk.return_value = mock_root
        mock_optionmenu.return_value = MagicMock()
        mock_button.return_value = MagicMock()
        mock_messagebox.return_value = MagicMock()
        mock_stringvar.return_value = MagicMock()

        # Mock the geometry method to avoid conflicts with center_window
        mock_root.geometry = MagicMock()

        # Initialize the MainApp
        app = MainApp()

        # Check if the main window is created
        mock_ctk.assert_called_once()
        mock_root.title.assert_called_with("Events Attendance")
        mock_root.geometry.assert_any_call("400x350")
        mock_root.resizable.assert_called_with(False, False)

        # Check if the widgets are created
        mock_optionmenu.assert_called_once_with(mock_root, variable=app.table_var, values=[])
        mock_button.assert_any_call(mock_root, text="Confirm", command=unittest.mock.ANY)
        mock_button.assert_any_call(mock_root, text="Create Event", command=unittest.mock.ANY)
        mock_button.assert_any_call(mock_root, text="Show Members", command=unittest.mock.ANY)
        mock_button.assert_any_call(mock_root, text="Register Member", command=unittest.mock.ANY)
        mock_button.assert_any_call(mock_root, text="Redeem Points", command=unittest.mock.ANY)

        # Check if the dropdown is updated
        app.update_tables_dropdown()
        mock_optionmenu.return_value.configure.assert_called()

if __name__ == "__main__":
    unittest.main()
