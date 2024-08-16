import os
import customtkinter as CTk
from CTkTable import CTkTable
import pandas as pd
from customtkinter import filedialog
from CTkMessagebox import CTkMessagebox
from icecream import ic
import string
from dbActions import DBActions
from creds import Credentials
import time

def list_tables(selected_table):
    # Check all tables in the database
    tables = DBActions.list_tables(Credentials.db)
    if tables is None:
        return []
    # Extract table names from the list of dictionaries
    return [list(row.values())[0] for row in tables if isinstance(row, dict) and row]

def confirm_button_clicked(table_var):
    ic("confirm_button_clicked")
    selected_table = table_var.get()
    if not selected_table:
        CTkMessagebox(title="Warning", message="No table selected", icon="warning")
    elif selected_table == "Select a table":
        CTkMessagebox(title="Warning", message="Please select a table", icon="warning")
    elif selected_table == "Members":
        CTkMessagebox(title="Warning", message="The 'Members' table cannot be selected", icon="warning")
    else:
        print(f"Selected table: {selected_table}")
        # Create a new window with a table
        create_table_window(selected_table)

def create_table_window(selected_table):
    # Create a new top-level window
    table_window = CTk.CTkToplevel()
    table_window.title(f"Event: {selected_table}")
    table_window.geometry('600x600')  # Set fixed window size

    # Ensure the window is on top
    table_window.attributes('-topmost', True)

    def search_table(event):
        query = search_entry.get()
        if query == "":
            filtered_data = data  # Display all data if the search query is empty
        else:
            filtered_data = [row for row in data if any(query in str(cell) for cell in row.values() if isinstance(row, dict)) or any(query in str(cell) for cell in row)]
        display_data(filtered_data)

    # Create a search text box at the top of the table
    search_entry = CTk.CTkEntry(table_window)
    search_entry.pack(padx=10, pady=10, fill='x')
    search_entry.bind('<KeyRelease>', search_table)

    # Create a scrollable frame
    scrollable_frame = CTk.CTkScrollableFrame(table_window)
    scrollable_frame.pack(fill='both', expand=True)

    # Fetch data from the selected table
    data = DBActions.fetch_table_data(selected_table)
    ic(data)

    # Initialize values to avoid UnboundLocalError
    values = []

    def display_data(filtered_data):
        # Get the existing widgets in the scrollable frame
        existing_widgets = scrollable_frame.winfo_children()

        # Calculate the number of cells needed
        num_cells_needed = len(filtered_data) * len(filtered_data[0]) if filtered_data else 0

        # Create additional widgets if needed
        while len(existing_widgets) < num_cells_needed:
            cell = CTk.CTkLabel(scrollable_frame, text="", corner_radius=0, width=50)
            existing_widgets.append(cell)

        # Update the text of existing widgets and grid them
        widget_index = 0
        for i, row in enumerate(filtered_data):
            if isinstance(row, dict):
                values = list(row.values())
            else:
                values = row
            for j, cell_data in enumerate(values):
                cell = existing_widgets[widget_index]
                cell.configure(text=cell_data)
                cell.grid(row=i, column=j, padx=5, pady=5)
                widget_index += 1

        # Hide any extra widgets
        for k in range(widget_index, len(existing_widgets)):
            existing_widgets[k].grid_forget()

    # Display the initial data
    display_data(data)

    # Create a text field at the bottom of the table to simulate an RFID scanner
    rfid_entry = CTk.CTkEntry(table_window)
    columnspan_value = len(values) if len(values) > 0 else 1
    rfid_entry.pack(padx=10, pady=10, fill='x')

    # Bind the <Return> key event to the rfid_scan_event function
    rfid_entry.bind('<Return>', lambda event: rfid_scan_event(rfid_entry, table_window, selected_table, display_data, data))

    def export_to_file():
        # Ask the user for the file type and location
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if not file_path:
            return

        # Convert the data to a DataFrame

        df = pd.DataFrame(DBActions.fetch_table_data(selected_table))

        # Save the DataFrame to the selected file type
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)

    # Create the export button
    export_button = CTk.CTkButton(table_window, text="Export", command=export_to_file)
    export_button.pack(side='top', anchor='ne', padx=10, pady=10)

rfid_cache = {}

def rfid_scan_event(entry_widget, table_window, selected_table, display_data, data):
    rfid_num = entry_widget.get()
    ic(rfid_num + ' rfid_scan func')

    current_time = time.time()
    # Check if the RFID number is in the cache and if the scan was made within the last 5 seconds
    if rfid_num in rfid_cache:
        last_scan_time = rfid_cache[rfid_num]
        if current_time - last_scan_time < 15:
            messagebox1 = CTkMessagebox(title="RFID Scan", message=f"{rfid_num} was scanned within the last 15 seconds. Ignoring scan...", icon="warning")
            table_window.after(4500, messagebox1.destroy)  # Close the message box after 5 second
            return

    def insert_digit(index):
        if index < len(rfid_num):
            # Check if rfid_num exists in the database using member_exists function
            if not DBActions.member_exists(rfid_num):
                messagebox2 = CTkMessagebox(title="RFID Scan Error", message="RFID number not found", icon="cancel")
                table_window.after(1000, messagebox2.destroy)  # Close the message box after 1 second
                entry_widget.delete(0, CTk.END)
                return
            
            entry_widget.insert(CTk.END, rfid_num[index])
            DBActions.attendance_member_event(selected_table, rfid_num)  # Call the attendance_member_event function
            refresh_data()
            messagebox2 = CTkMessagebox(title="RFID Scan", message="RFID recorded", icon="check")
            table_window.after(1000, messagebox2.destroy)  # Close the message box after 1 second
            entry_widget.delete(0, CTk.END)

    def refresh_data():
        # Fetch the updated data
        updated_data = DBActions.fetch_table_data(selected_table)
        # Update the displayed data
        display_data(updated_data)

    # Update the cache with the current timestamp
    rfid_cache[rfid_num] = current_time

    insert_digit(0)

def rfid_scan_register(entry_widget, name, student_num, program, year, table_window):
    rfid_num = entry_widget.get()
    member_name = name.get()
    member_student_num = student_num.get()
    member_program = program.get()
    member_year = year.get()
    ic(rfid_num, member_name, member_program, member_year)

    # Check if the member already exists
    if DBActions.member_exists(rfid_num):
        CTkMessagebox(title="Member Register", message="Member already exists!", icon="error")
    else:
        # Register the new member
        DBActions.member_register(rfid_num, member_name, member_student_num, member_program, member_year)
        if CTkMessagebox(title="Member Register", message="Member Registered!", icon="check"):
            table_window.after(300, table_window.destroy())

def create_event_button_clicked():
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
            DBActions.create_event_table(event_name)
            ic(f"New event '{event_name}' created successfully!")
            CTkMessagebox(title="Create Event", message=f"New event '{event_name}' created successfully!", icon="check")
            update_tables_dropdown()
        else:
            ic("No event name provided. Exiting...")
            CTkMessagebox(title="Create Event", message="No event name provided.", icon="error")

def register_member_button_clicked():
    ic("register_member_button_clicked")
    # Create a new window with a form to register a new member
    register_window = CTk.CTkToplevel()
    register_window.title("Register New Member")
    register_window.geometry("400x300")
    register_window.attributes('-topmost', True)  # Ensure the window is on top
    register_window.resizable(False, False)  # Disable resizing
    center_window(register_window)

    # Create and place form fields
    name_entry = CTk.CTkEntry(register_window, placeholder_text="Enter name")
    name_entry.pack(pady=5)

    student_num_entry = CTk.CTkEntry(register_window, placeholder_text="Enter student number")
    student_num_entry.pack(pady=5)

    program_entry = CTk.CTkEntry(register_window, placeholder_text="Enter program")
    program_entry.pack(pady=5)

    year_entry = CTk.CTkEntry(register_window, placeholder_text="Enter year")
    year_entry.pack(pady=5)

    rfid_entry = CTk.CTkEntry(register_window, placeholder_text="Scan RFID")
    rfid_entry.pack(pady=5)

    # Bind the "Enter" key to Register
    rfid_entry.bind('<Return>', lambda event: rfid_scan_register(rfid_entry, name_entry, student_num_entry, program_entry, year_entry, register_window))
    # Create and place a button to submit the form
    # submit_button = CTk.CTkButton(register_window, text="Submit", command=lambda: submit_form(name_entry, program_entry, year_entry))
    # submit_button.pack(pady=5)

# Function to update tables dropdown based on the database
def update_tables_dropdown():
    tables = list_tables(Credentials.db)
    table_dropdown.configure(values=tables)

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

root = CTk.CTk()
root.title("AHO RFID Events")
root.geometry("400x350")
root.resizable(False, False)  # Disable resizing
center_window(root)

# Dropdown box for tables
table_var = CTk.StringVar(value="Select a table")  # Set default value
table_dropdown = CTk.CTkOptionMenu(root, variable=table_var, values=[])
table_dropdown.pack(pady=20)

# Initial population of tables dropdown
update_tables_dropdown()

# Create and place buttons
confirm_button = CTk.CTkButton(root, text="Confirm", command=lambda: confirm_button_clicked(table_var))
confirm_button.pack(pady=20)

create_event_button = CTk.CTkButton(root, text="Create Event", command=create_event_button_clicked)
create_event_button.pack(pady=20)

show_memmbers_button = CTk.CTkButton(root, text="Show Members", command=lambda: create_table_window("Members"))
show_memmbers_button.pack(pady=20)

register_member_button = CTk.CTkButton(root, text="Register Member", command=register_member_button_clicked)
register_member_button.pack(pady=20)

# # Create and place refresh button
# refresh_button = CTk.CTkButton(root, text="Refresh", command=lambda: update_tables_dropdown())
# refresh_button.pack(pady=20)

root.mainloop()