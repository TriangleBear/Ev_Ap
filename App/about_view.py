import customtkinter as CTk

class AboutView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        about_label = CTk.CTkLabel(self, text="About This Application")
        about_label.pack(pady=10)

        description_label = CTk.CTkLabel(self, text="This application is designed to manage event attendance and member points.")
        description_label.pack(pady=10)

        version_label = CTk.CTkLabel(self, text="Version: 1.0.0")
        version_label.pack(pady=10)

        close_button = CTk.CTkButton(self, text="Close", command=self.close)
        close_button.pack(pady=10)

    def close(self):
        self.pack_forget()