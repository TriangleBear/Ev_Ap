from rfid_app import MyApp
import customtkinter as CTk
from CTkMessagebox import CTkMessagebox
import os
import sys

class RFIDApp(MyApp):
    def __init__(self):
        super().__init__()

    def run(self):
        super().run()

if __name__ == "__main__":
    # Get the path to the icon file
    if hasattr(sys, '_MEIPASS'):
        icon_path = os.path.join(sys._MEIPASS, 'icon64.ico')
    else:
        icon_path = 'D:/Programming/AHO/RFID App/ORG-RFID-EVENTS/icon64.ico'
    
    root = CTk.CTk()
    root.iconbitmap(icon_path)
    
    app = RFIDApp()
    app.run()