import customtkinter as CTk
from CTkMessagebox import CTkMessagebox
from database.dblite import DBActions
from icecream import ic

class EventManager:
    def __init__(self, app):
        self.app = app
        # self.points_per_event = {}

    def create_event_button_clicked(self):
        ic("create_event_button_clicked")
        response = CTkMessagebox(title="Create Event", message="Are you sure you want to create a new event?", icon="question", option_1="Yes", option_2="No")
        if response.get() == "No":
            ic("User cancelled event creation")
            return
        elif response.get() == "Yes":
            dialog = CTk.CTkToplevel(self.app.root)
            dialog.title("Create Event Name")
            dialog.geometry("400x130")
            dialog.attributes('-topmost', False)
            dialog.resizable(False, False)
            self.app.center_window(dialog)

            label = CTk.CTkLabel(dialog, text="Enter the name for the new event:")
            label.pack(pady=(12, 6))

            entry = CTk.CTkEntry(dialog, width=300)
            entry.pack(pady=(0, 12))

            def on_submit():
                event_name = entry.get().strip()
                if event_name:
                    dialog.destroy()
                    self.create_event_window(event_name)
                else:
                    CTkMessagebox(title="Create Event", message="No event name provided.", icon="error")

            def on_cancel():
                dialog.destroy()

            btn_frame = CTk.CTkFrame(dialog)
            btn_frame.pack(pady=(0,12))

            submit_btn = CTk.CTkButton(btn_frame, text="Submit", command=on_submit)
            submit_btn.pack(side="left", padx=8)
            cancel_btn = CTk.CTkButton(btn_frame, text="Cancel", command=on_cancel)
            cancel_btn.pack(side="left", padx=8)

            dialog.transient(self.app.root)
            dialog.grab_set()
            self.app.root.wait_window(dialog)

    def create_event_window(self, event_name):
        event_window = CTk.CTkToplevel(self.app.root)
        event_window.title("Create Event")
        event_window.geometry("300x100")
        event_window.attributes('-topmost', True)
        event_window.resizable(False, False)
        self.app.center_window(event_window)

        event_name_label = CTk.CTkLabel(event_window, text=f"Event Name: {event_name}")
        event_name_label.pack(pady=5)

        def event_create():
            # points = 0.10
            try:
                DBActions.create_event_table(event_name)
                # self.points_per_event[event_name] = points
                CTkMessagebox(title="Event Creation", message="Event Created!", icon="check")
                self.app.update_tables_dropdown()
                event_window.destroy()
            except Exception as e:
                CTkMessagebox(title="Event Creation Error", message=f"Error creating event: {str(e)}", icon="error")

        submit_button = CTk.CTkButton(event_window, text="Submit", command=event_create)
        submit_button.pack(pady=5)