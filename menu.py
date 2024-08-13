import os
import customtkinter as CTk
from event import create_database
from icecream import ic

DATABASE_FOLDER = '.DBsavefile'  # Update this path to your database folder

def list_databases(folder):
    return [f for f in os.listdir(folder) if f.endswith('.db')]

def confirm_button_clicked():
    ic("confirm_button_clicked")
    selected_db = db_var.get()
    if selected_db:
        print(f"Selected database: {selected_db}")
        # Add your code here to use the selected database
    else:
        print("No database selected")

def create_event_button_clicked():
    ic("create_event_button_clicked")
    response = custom_message_box("Create Database", "Do you want to create another database?")
    if response:
        create_database()
        # Refresh the dropdown list
        databases = list_databases(DATABASE_FOLDER)
        db_dropdown.configure(values=databases)
        db_var.set(databases[0] if databases else "")

def custom_message_box(title, message):
    def on_yes():
        nonlocal response
        response = True
        msg_box.destroy()

    def on_no():
        nonlocal response
        response = False
        msg_box.destroy()

    response = None
    msg_box = CTk.CTkToplevel()
    msg_box.title(title)
    msg_box.geometry("300x150")
    msg_box.resizable(False, False)  # Disable resizing

    label = CTk.CTkLabel(msg_box, text=message)
    label.pack(pady=20)

    button_frame = CTk.CTkFrame(msg_box)
    button_frame.pack(pady=10)

    yes_button = CTk.CTkButton(button_frame, text="Yes", command=on_yes)
    yes_button.pack(side="left", padx=10)

    no_button = CTk.CTkButton(button_frame, text="No", command=on_no)
    no_button.pack(side="right", padx=10)

    msg_box.wait_window()
    return response

def run():
    root = CTk.CTk()
    root.title("AHO RFID Events")
    root.geometry("400x300")
    root.resizable(False, False)  # Disable resizing

    # Dropdown box for databases
    databases = list_databases(DATABASE_FOLDER)
    global db_var
    db_var = CTk.StringVar(value=databases[0] if databases else "")
    global db_dropdown
    db_dropdown = CTk.CTkOptionMenu(root, variable=db_var, values=databases)
    db_dropdown.pack(pady=20)

    # Create and place buttons
    confirm_button = CTk.CTkButton(root, text="Confirm", command=confirm_button_clicked)
    confirm_button.pack(pady=20)

    create_event_button = CTk.CTkButton(root, text="Create Event", command=create_event_button_clicked)
    create_event_button.pack(pady=20)

    root.mainloop()