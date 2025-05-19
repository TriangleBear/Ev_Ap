import customtkinter as CTk
from creds import CLOUD_DB_HOST, CLOUD_DB_PORT, CLOUD_DB_NAME
from dblite import Database, DBActions  # Add DBActions to the import
from CTkMessagebox import CTkMessagebox  # Add this import for message box

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
        
        cloud_user_label = CTk.CTkLabel(self.options_frame, text="Cloud DB User:")
        cloud_user_label.pack(anchor="w", padx=10, pady=5)
        self.cloud_user_entry = CTk.CTkEntry(self.options_frame)
        self.cloud_user_entry.pack(anchor="w", padx=10, pady=5)
        
        cloud_password_label = CTk.CTkLabel(self.options_frame, text="Cloud DB Password:")
        cloud_password_label.pack(anchor="w", padx=10, pady=5)
        self.cloud_password_entry = CTk.CTkEntry(self.options_frame, show="*")
        self.cloud_password_entry.pack(anchor="w", padx=10, pady=5)
        
        self.apply_button = CTk.CTkButton(self.options_frame, text="Apply", command=self.apply_db_settings)
        self.apply_button.pack(anchor="w", padx=10, pady=20)

    def apply_db_settings(self):
        cloud_user = self.cloud_user_entry.get()
        cloud_password = self.cloud_password_entry.get()
        try:
            self.app.database = Database(cloud_user=cloud_user, cloud_password=cloud_password, app=self.app)
            DBActions.set_db_instance(self.app.database)
            self.app.database.initialize_db()
            self.app.update_db_status_label()
            CTkMessagebox(title="Database Settings", message="Cloud database settings applied successfully.", icon="check")
        except Exception as e:
            CTkMessagebox(title="Database Error", message=f"Failed to connect to cloud database: {str(e)}", icon="error")