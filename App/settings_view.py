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
        
        db_label = CTk.CTkLabel(self.options_frame, text="Database Mode:", font=CTk.CTkFont(size=18))
        db_label.pack(anchor="w", padx=10, pady=10)
        
        self.db_mode_menu = CTk.CTkOptionMenu(
            self.options_frame, 
            values=["SQLite", "Cloud"],
            command=self.change_db_mode
        )
        self.db_mode_menu.pack(anchor="w", padx=10, pady=10)
        self.db_mode_menu.set("SQLite")
        
        self.cloud_creds_frame = CTk.CTkFrame(self.options_frame)
        self.cloud_creds_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        cloud_user_label = CTk.CTkLabel(self.cloud_creds_frame, text="Cloud DB User:")
        cloud_user_label.pack(anchor="w", padx=10, pady=5)
        self.cloud_user_entry = CTk.CTkEntry(self.cloud_creds_frame)
        self.cloud_user_entry.pack(anchor="w", padx=10, pady=5)
        
        cloud_password_label = CTk.CTkLabel(self.cloud_creds_frame, text="Cloud DB Password:")
        cloud_password_label.pack(anchor="w", padx=10, pady=5)
        self.cloud_password_entry = CTk.CTkEntry(self.cloud_creds_frame, show="*")
        self.cloud_password_entry.pack(anchor="w", padx=10, pady=5)
        
        self.apply_button = CTk.CTkButton(self.options_frame, text="Apply", command=self.apply_db_settings)
        self.apply_button.pack(anchor="w", padx=10, pady=20)
        
        self.cloud_creds_frame.pack_forget()  # Hide cloud creds frame initially

    def change_db_mode(self, mode):
        if mode == "Cloud":
            self.cloud_creds_frame.pack(fill="both", expand=True, padx=20, pady=20)
        else:
            self.cloud_creds_frame.pack_forget()

    def apply_db_settings(self):
        db_mode = self.db_mode_menu.get()
        
        # Initialize progress bar
        progress_bar = CTk.CTkProgressBar(self, mode='indeterminate')
        progress_bar.pack(side='bottom', pady=20)
        progress_bar.start()
        
        if db_mode == "Cloud":
            # Backup SQLite data to cloud before switching
            sqlite_db = Database(use_cloud=False)
            sqlite_data = sqlite_db.db.fetch_all_data()
            
            cloud_user = self.cloud_user_entry.get()
            cloud_password = self.cloud_password_entry.get()
            try:
                self.app.database = Database(use_cloud=True, cloud_user=cloud_user, cloud_password=cloud_password, app=self.app)
                # Set the database instance for DBActions
                DBActions.set_db_instance(self.app.database)
                for table_name, data in sqlite_data.items():
                    self.app.database.db.insert_data(table_name, data)
            except Exception as e:
                CTkMessagebox(title="Database Connection Error", message=f"Failed to connect to cloud database: {str(e)}")
                progress_bar.stop()
                progress_bar.pack_forget()
                return
        else:
            # Specify additional tables to copy if needed
            # additional_tables = ['Events', 'Attendance']  # Example additional tables
            # self.app.database.backup_cloud_to_sqlite(tables_to_copy=additional_tables)
            self.app.database = Database(use_cloud=False, app=self.app)
            # Set the database instance for DBActions
            DBActions.set_db_instance(self.app.database)
        
        self.app.database.initialize_db()
        self.app.update_db_status_label()  # Update the database status label
        
        # Stop and hide progress bar after switching
        progress_bar.stop()
        progress_bar.pack_forget()
        
        # Show confirmation message that database mode has changed
        CTkMessagebox(
            title="Database Mode Changed",
            message=f"Database mode has been successfully changed to {'Cloud MySQL' if db_mode == 'Cloud' else 'SQLite'}.",
            icon="check"
        )