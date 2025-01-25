from rfid_app import MyApp
import customtkinter as CTk
from CTkMessagebox import CTkMessagebox

class RFIDApp(MyApp):
    def __init__(self):
        super().__init__()

    def run(self):
        super().run()

if __name__ == "__main__":
    app = RFIDApp()
    app.run()