import customtkinter as CTk
from database.dblite import Database, DBActions
from database.config import load_config, save_config, get_db_mode, get_gsheet_api_url, set_gsheet_api_url
from CTkMessagebox import CTkMessagebox


class SettingsView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        self.header = CTk.CTkLabel(self, text="Settings", font=CTk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=20)

        self.options_frame = CTk.CTkScrollableFrame(self)
        self.options_frame.pack(fill="both", expand=True, padx=20, pady=20)

        appearance_label = CTk.CTkLabel(self.options_frame, text="Appearance Mode:", font=CTk.CTkFont(size=18))
        appearance_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.appearance_mode_menu = CTk.CTkOptionMenu(
            self.options_frame,
            values=["Light", "Dark", "System"],
            command=self.app.change_appearance_mode
        )
        self.appearance_mode_menu.pack(anchor="w", padx=10, pady=(0, 20))
        self.appearance_mode_menu.set("System")

        db_separator = CTk.CTkFrame(self.options_frame, height=2)
        db_separator.pack(fill="x", padx=10, pady=10)

        db_header = CTk.CTkLabel(self.options_frame, text="Database Configuration", font=CTk.CTkFont(size=18, weight="bold"))
        db_header.pack(anchor="w", padx=10, pady=(10, 5))

        db_desc = CTk.CTkLabel(self.options_frame, text="Choose your database backend. SQLite runs locally. Google Sheets syncs via a web API.", wraplength=500, justify="left")
        db_desc.pack(anchor="w", padx=10, pady=(0, 10))

        db_mode_label = CTk.CTkLabel(self.options_frame, text="Database Mode:", font=CTk.CTkFont(size=14))
        db_mode_label.pack(anchor="w", padx=10, pady=(5, 5))

        current_mode = get_db_mode()
        self.db_mode_var = CTk.StringVar(value="SQLite" if current_mode == 'sqlite' else "Google Sheets")
        self.db_mode_menu = CTk.CTkOptionMenu(
            self.options_frame,
            values=["SQLite", "Google Sheets"],
            variable=self.db_mode_var,
            command=self.on_db_mode_change
        )
        self.db_mode_menu.pack(anchor="w", padx=10, pady=(0, 15))

        self.gs_frame = CTk.CTkFrame(self.options_frame)
        self.gs_frame.pack(fill="x", padx=10, pady=5)

        gs_url_label = CTk.CTkLabel(self.gs_frame, text="Google App Script Web App URL:", font=CTk.CTkFont(size=14))
        gs_url_label.pack(anchor="w", padx=5, pady=(5, 5))

        gs_url_desc = CTk.CTkLabel(
            self.gs_frame,
            text="Paste the deployment URL of your Google Apps Script web app.\nDeploy the script in 'database/gsheet_api.gs' first.",
            wraplength=480,
            justify="left",
            font=CTk.CTkFont(size=11),
            text_color=("gray40", "gray60")
        )
        gs_url_desc.pack(anchor="w", padx=5, pady=(0, 5))

        current_url = get_gsheet_api_url()
        self.gs_url_entry = CTk.CTkEntry(self.gs_frame, placeholder_text="https://script.google.com/macros/s/.../exec", width=480)
        self.gs_url_entry.pack(anchor="w", padx=5, pady=5)
        if current_url:
            self.gs_url_entry.insert(0, current_url)

        btn_row1 = CTk.CTkFrame(self.gs_frame, fg_color="transparent")
        btn_row1.pack(anchor="w", padx=5, pady=(5, 5))

        self.gs_save_btn = CTk.CTkButton(
            btn_row1,
            text="Save API URL",
            command=self.save_gs_url
        )
        self.gs_save_btn.pack(side="left", padx=(0, 10))

        self.gs_test_btn = CTk.CTkButton(
            btn_row1,
            text="Test Connection",
            command=self.test_gs_connection,
            fg_color=("#5bc0de", "#31b0d5"),
            hover_color=("#31b0d5", "#269abc")
        )
        self.gs_test_btn.pack(side="left")

        gs_sheet_label = CTk.CTkLabel(self.gs_frame, text="Google Sheet URL/ID (optional):", font=CTk.CTkFont(size=14))
        gs_sheet_label.pack(anchor="w", padx=5, pady=(10, 5))

        gs_sheet_desc = CTk.CTkLabel(
            self.gs_frame,
            text="Configure which Google Sheet to use. Paste the full Sheet URL or just the ID.\nOr run the Ev_Ap → Configure Spreadsheet menu inside the Apps Script editor.",
            wraplength=480,
            justify="left",
            font=CTk.CTkFont(size=11),
            text_color=("gray40", "gray60")
        )
        gs_sheet_desc.pack(anchor="w", padx=5, pady=(0, 5))

        self.gs_sheet_entry = CTk.CTkEntry(self.gs_frame, placeholder_text="https://docs.google.com/spreadsheets/d/.../edit or Sheet ID", width=480)
        self.gs_sheet_entry.pack(anchor="w", padx=5, pady=5)

        self.gs_sheet_btn = CTk.CTkButton(
            self.gs_frame,
            text="Set Spreadsheet",
            command=self.set_gs_spreadsheet
        )
        self.gs_sheet_btn.pack(anchor="w", padx=5, pady=(5, 10))

        self.apply_frame = CTk.CTkFrame(self.options_frame)
        self.apply_frame.pack(fill="x", padx=10, pady=15)

        self.apply_btn = CTk.CTkButton(
            self.apply_frame,
            text="Apply & Restart Connection",
            command=self.apply_db_settings,
            fg_color=("#d9534f", "#c9302c"),
            hover_color=("#c9302c", "#ac2925"),
            width=250,
            height=40,
            font=CTk.CTkFont(size=14, weight="bold")
        )
        self.apply_btn.pack()

        self.update_gs_frame_visibility()

    def on_db_mode_change(self, choice):
        self.update_gs_frame_visibility()

    def update_gs_frame_visibility(self):
        if self.db_mode_var.get() == "Google Sheets":
            self.gs_frame.pack(fill="x", padx=10, pady=5)
        else:
            self.gs_frame.pack_forget()

    def save_gs_url(self):
        url = self.gs_url_entry.get().strip()
        if url:
            set_gsheet_api_url(url)
            CTkMessagebox(title="Settings", message="Google App Script Web App URL saved.")
        else:
            CTkMessagebox(title="Settings", message="Please enter a valid URL.")

    def test_gs_connection(self):
        url = self.gs_url_entry.get().strip()
        if not url:
            CTkMessagebox(title="Test Connection", message="Please enter the Google App Script Web App URL first.")
            return

        from database.sheet_db import SheetDB
        test_db = SheetDB(api_url=url)
        try:
            config = test_db.get_config()
            if config:
                sid = config.get('spreadsheetId') or '(not set)'
                name = config.get('spreadsheetName') or '(unknown)'
                s_url = config.get('spreadsheetUrl') or ''
                err = config.get('error') or ''
                msg = f"Connected! API URL is valid.\n\nSpreadsheet ID: {sid}\nName: {name}"
                if s_url:
                    msg += f"\nURL: {s_url}"
                if err:
                    msg += f"\n\nWarning: {err}"
                CTkMessagebox(title="Test Connection", message=msg)
            else:
                CTkMessagebox(title="Test Connection", message="Connection failed: no response from API.")
        except Exception as e:
            CTkMessagebox(title="Test Connection", message=f"Connection failed: {str(e)}")

    def set_gs_spreadsheet(self):
        url = self.gs_url_entry.get().strip()
        sheet = self.gs_sheet_entry.get().strip()
        if not url:
            CTkMessagebox(title="Set Spreadsheet", message="Please enter the Google App Script Web App URL first.")
            return
        if not sheet:
            CTkMessagebox(title="Set Spreadsheet", message="Please enter the Google Sheet URL or ID.")
            return

        from database.sheet_db import SheetDB
        test_db = SheetDB(api_url=url)
        try:
            result = test_db.set_spreadsheet(sheet)
            if result:
                CTkMessagebox(title="Set Spreadsheet", message="Spreadsheet configured successfully!")
            else:
                CTkMessagebox(title="Set Spreadsheet", message="Failed to configure spreadsheet. Check the URL/ID.")
        except Exception as e:
            CTkMessagebox(title="Set Spreadsheet", message=f"Error: {str(e)}")

    def apply_db_settings(self):
        mode = 'gsheet' if self.db_mode_var.get() == "Google Sheets" else 'sqlite'
        if mode == 'gsheet':
            url = self.gs_url_entry.get().strip()
            if not url:
                CTkMessagebox(title="Settings", message="Please enter the Google App Script Web App URL first.")
                return
            set_gsheet_api_url(url)

        self.app.database.switch_mode(mode)
        self.app.database.sheet_db.set_api_url(get_gsheet_api_url())

        CTkMessagebox(
            title="Database Mode",
            message=f"Database mode switched to {self.db_mode_var.get()}.\nRestart the app for full re-initialization."
        )
