import os
import customtkinter as CTk
from CTkTable import CTkTable
from CTkMessagebox import CTkMessagebox as messagebox
from icecream import ic
import string

DATABASE_FOLDER = '.DBsavefile'  # Update this path to your database folder

def list_databases(folder):
    return [f for f in os.listdir(folder) if f.endswith('.db')]

def confirm_button_clicked():
    ic("confirm_button_clicked")
    selected_db = db_var.get()
    if selected_db:
        print(f"Selected database: {selected_db}")
        # Create a new window with a table
        create_table_window(selected_db)
    else:
        print("No database selected")

def create_table_window(selected_db):
    # Create a new top-level window
    table_window = CTk.CTkToplevel()
    table_window.title(f"Database: {selected_db}")
    
    # Ensure the window is on top
    table_window.attributes('-topmost', True)

    data = [
        ["Column 1", "Column 2"],
        ["Row1-Col1", "Row1-Col2"],
        ["Row2-Col1", "Row2-Col2"]
    ]

    # Calculate the number of rows
    num_rows = len(data)

    # Calculate the number of columns (assuming all rows have the same number of columns)
    num_columns = len(data[0]) if num_rows > 0 else 0

    # Create a CTkTable widget
    tree = CTkTable(table_window, row=num_rows, column=num_columns, values=data)

    # Pack the CTkTable widget
    tree.pack(expand=True, fill='both')
    
    # Create a text field at the bottom of the table to simulate an RFID scanner
    rfid_entry = CTk.CTkEntry(table_window, placeholder_text="Scan RFID here")
    rfid_entry.pack(side='bottom', fill='x', padx=10, pady=10)

    # Bind the "F1" key to start the animation
    rfid_entry.bind('<Return>', lambda event: rfid_scan(rfid_entry, table_window))

def rfid_scan(entry_widget, table_window):
    rfid_num = entry_widget.get()
    ic(rfid_num + ' rfid_scan func')

    def insert_digit(index):
        if index < len(rfid_num):
            entry_widget.insert(CTk.END, rfid_num[index])
            if messagebox(title="RFID Scan", message="RFID scan complete", icon="check"):
                table_window.destroy()

    insert_digit(0)

def create_event_button_clicked():
    ic("create_event_button_clicked")
    response = messagebox(title="Create Database", message="Do you want to create another database?",
                          icon="info", option_1="Yes", option_2="No")
    if response:
        #create_database()
        # Refresh the dropdown list
        databases = list_databases(DATABASE_FOLDER)
        db_dropdown.configure(values=databases)
        db_var.set(databases[0] if databases else "")

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