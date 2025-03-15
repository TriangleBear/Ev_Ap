import customtkinter as CTk

class SettingsView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        self.header = CTk.CTkLabel(self, text="Settings", font=CTk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=20)
        
        # Settings options
        self.options_frame = CTk.CTkFrame(self)
        self.options_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Appearance mode setting
        appearance_label = CTk.CTkLabel(self.options_frame, text="Appearance Mode:", font=CTk.CTkFont(size=18))
        appearance_label.pack(anchor="w", padx=10, pady=10)
        
        self.appearance_mode_menu = CTk.CTkOptionMenu(
            self.options_frame, 
            values=["Light", "Dark", "System"],
            command=self.app.change_appearance_mode
        )
        self.appearance_mode_menu.pack(anchor="w", padx=10, pady=10)
        self.appearance_mode_menu.set("System")
        
        # Add more settings options as needed