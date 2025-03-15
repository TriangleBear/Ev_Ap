import customtkinter as CTk

class HelpView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        help_text = """
        Welcome to the Events Attendance App!

        This application allows you to manage event attendance and member registrations.

        Features:
        - Register new members
        - Create new events
        - Record attendance using RFID
        - Redeem points for members
        - Export event data to CSV or Excel

        For any assistance, please contact support.
        """
        help_label = CTk.CTkLabel(self, text=help_text, justify=CTk.LEFT)
        help_label.pack(padx=20, pady=20)