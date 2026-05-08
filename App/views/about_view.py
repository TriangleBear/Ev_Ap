import customtkinter as CTk
import webbrowser as wb
import tkinter.font as tkfont


class AboutView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        about_label = CTk.CTkLabel(self, text="About This Application")
        about_label.pack(pady=10)

        description_label = CTk.CTkLabel(self, text="This application is designed to manage event attendance and member registration.")
        description_label.pack(pady=10)

        creator_label = CTk.CTkLabel(self, text="Created by:")
        creator_label.pack(pady=10)

        link_font = CTk.CTkFont(family="Helvetica", size=12, underline=True)
        creator_name_label = CTk.CTkLabel(self, text="TriangleBear", text_color="blue", font=link_font, cursor="hand2")
        creator_name_label.pack(pady=3)
        creator_name_label.bind("<Button-1>", lambda e: self.open_url("https://github.com/TriangleBear"))

        version_label = CTk.CTkLabel(self, text="Version: dev_3.3.2")
        version_label.pack(pady=10)

        close_button = CTk.CTkButton(self, text="Close", command=self.close)
        close_button.pack(pady=10)

    def close(self):
        self.pack_forget()

    def open_url(self, url):
        wb.open(url)