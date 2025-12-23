import customtkinter as CTk
from dblite import Database, DBActions
from CTkMessagebox import CTkMessagebox

class SettingsView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        self.header = CTk.CTkLabel(self, text="Settings", font=CTk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=20)
        
        self.options_frame = CTk.CTkFrame(self)
        self.options_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        appearance_label = CTk.CTkLabel(self.options_frame, text="Appearance Mode:", font=CTk.CTkFont(size=18))
        appearance_label.pack(anchor="w", padx=10, pady=10)
        
        self.appearance_mode_menu = CTk.CTkOptionMenu(
            self.options_frame, 
            values=["Light", "Dark", "System"],
            command=self.app.change_appearance_mode
        )
        self.appearance_mode_menu.pack(anchor="w", padx=10, pady=10)
        self.appearance_mode_menu.set("System")
        
        db_label = CTk.CTkLabel(self.options_frame, text="Database Mode:", font=CTk.CTkFont(size=18))
        db_label.pack(anchor="w", padx=10, pady=10)

        self.db_mode_menu = CTk.CTkOptionMenu(
            self.options_frame,
            values=["SQLite"],
            command=lambda m: None
        )
        self.db_mode_menu.pack(anchor="w", padx=10, pady=10)
        self.db_mode_menu.set("SQLite")
        
        self.apply_button = CTk.CTkButton(self.options_frame, text="Apply", command=self.apply_db_settings)
        self.apply_button.pack(anchor="w", padx=10, pady=20)
        
        self.cloud_creds_frame.pack_forget()  # Hide cloud creds frame initially

    def change_db_mode(self, mode):
        # Only SQLite supported now; nothing to toggle
        return

    def apply_db_settings(self):
        # Ensure the app uses SQLite-only Database
        self.app.database = Database(app=self.app)
        DBActions.set_db_instance(self.app.database)
        self.app.database.initialize_db()
        self.app.update_db_status_label()
        CTkMessagebox(
            title="Database Mode",
            message="Database mode set to SQLite.",
            icon="check"
        )