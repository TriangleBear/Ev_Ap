import customtkinter as CTk
import webbrowser as wb

class AboutView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        about_label = CTk.CTkLabel(self, text="About This Application")
        about_label.pack(pady=10)

        description_label = CTk.CTkLabel(self, text="This application is designed to manage event attendance and members managment.")
        description_label.pack(pady=10)

        creator_lable = CTk.CTkLabel(self, text="Created by")
        creator_lable.pack(pady=10)
        
        creator_link = CTk.CTkLabel(
            text="TriangleBear",
            text_color="BLUE",
            cursor="hand2"
        )
        creator_link.pack(pady=10)
        creator_link.bind(<Button-1>, open_link)

        version_label = CTk.CTkLabel(self, text="Version: dev_3.3.2")
        version_label.pack(pady=10)

        close_button = CTk.CTkButton(self, text="Close", command=self.close)
        close_button.pack(pady=10)
        
    def link_creator(event):
        wb.open_new("https://github.com/TriangleBear")

    def close(self):
        self.pack_forget()