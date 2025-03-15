import customtkinter as CTk
from CTkMessagebox import CTkMessagebox
from dblite import DBActions
from icecream import ic

class EventManager:
    def __init__(self, app):
        self.app = app
        self.points_per_event = {}

    def create_event_button_clicked(self):
        ic("create_event_button_clicked")
        response = CTkMessagebox(title="Create Event", message="Are you sure you want to create a new event?", icon="question", option_1="Yes", option_2="No")
        if response.get() == "No":
            ic("User cancelled event creation")
            return
        elif response.get() == "Yes":
            dialog = CTk.CTkInputDialog(title="Create Event Name", text="Enter the name for the new event:")
            event_name = dialog.get_input()
            if event_name:
                ic(f"Creating new event '{event_name}'...")
                self.create_event_window(event_name)
            else:
                ic("No event name provided. Exiting...")
                CTkMessagebox(title="Create Event", message="No event name provided.", icon="error")

    def create_event_window(self, event_name):
        event_window = CTk.CTkToplevel()
        event_window.title("Create Event")
        event_window.geometry("400x300")
        event_window.attributes('-topmost', False)
        event_window.resizable(False, False)
        self.app.center_window(event_window)

        event_name_label = CTk.CTkLabel(event_window, text=f"Event Name: {event_name}")
        event_name_label.pack(pady=5)

        def event_create():
            points = 0.10
            try:
                DBActions.create_event_table(event_name)
                self.points_per_event[event_name] = points
                CTkMessagebox(title="Event Creation", message="Event Created!", icon="check")
                self.app.update_tables_dropdown()
                event_window.destroy()
            except Exception as e:
                CTkMessagebox(title="Event Creation Error", message=f"Error creating event: {str(e)}", icon="error")

        submit_button = CTk.CTkButton(event_window, text="Submit", command=event_create)
        submit_button.pack(pady=5)