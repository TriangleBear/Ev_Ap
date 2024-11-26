import customtkinter as CTk
from CTkMessagebox import CTkMessagebox
from dbActions import DBActions
from creds import Credentials
import time
import pandas as pd
from customtkinter import filedialog
from dbActions import DBActions
from icecream import ic

def list_tables(selected_table):
    # Check all tables in the database
    tables = DBActions.list_tables(Credentials.db)
    if tables is None:
        return []
    return [list(row.values())[0] for row in tables if isinstance(row, dict) and row]

def confirm_button_clicked(table_var):
    selected_table = table_var.get()
    if not selected_table:
        CTkMessagebox(title="Warning", message="No table selected", icon="warning")
    elif selected_table == "Select a table":
        CTkMessagebox(title="Warning", message="Please select a table", icon="warning")
    elif selected_table == "Members":
        CTkMessagebox(title="Warning", message="The 'Members' table cannot be selected", icon="warning")
    else:
        create_table_window(selected_table)

def create_table_window(selected_table):
    table_window = CTk.CTkToplevel()
    table_window.title(f"Event: {selected_table}")
    table_window.geometry('600x600')  # Set fixed window size
    table_window.attributes('-topmost', True)

    def search_table(event):
        query = search_entry.get()
        filtered_data = [row for row in data if any(query in str(cell) for cell in row.values() if isinstance(row, dict)) or any(query in str(cell) for cell in row)]
        display_data(filtered_data)

    search_entry = CTk.CTkEntry(table_window)
    search_entry.pack(padx=10, pady=10, fill='x')
    search_entry.bind('<KeyRelease>', search_table)

    scrollable_frame = CTk.CTkScrollableFrame(table_window)
    scrollable_frame.pack(fill='both', expand=True)

    data = DBActions.fetch_table_data(selected_table)

    def display_data(filtered_data):
        existing_widgets = scrollable_frame.winfo_children()
        num_cells_needed = len(filtered_data) * len(filtered_data[0]) if filtered_data else 0

        while len(existing_widgets) < num_cells_needed:
            cell = CTk.CTkLabel(scrollable_frame, text="", corner_radius=0, width=50)
            existing_widgets.append(cell)

        widget_index = 0
        for i, row in enumerate(filtered_data):
            values = list(row.values()) if isinstance(row, dict) else row
            for j, cell_data in enumerate(values):
                cell = existing_widgets[widget_index]
                cell.configure(text=cell_data)
                cell.grid(row=i, column=j, padx=5, pady=5)
                widget_index += 1

        for k in range(widget_index, len(existing_widgets)):
            existing_widgets[k].grid_forget()

    display_data(data)

    rfid_entry = CTk.CTkEntry(table_window)
    rfid_entry.pack(padx=10, pady=10, fill='x')
    rfid_entry.bind('<Return>', lambda event: rfid_scan_event(rfid_entry, table_window, selected_table, display_data, data))

    def export_to_file():
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if not file_path:
            return
        df = pd.DataFrame(DBActions.fetch_table_data(selected_table))
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)

    # Create a frame to contain both buttons
    button_frame = CTk.CTkFrame(table_window)
    button_frame.pack(side='top', anchor='ne', padx=10, pady=10)

    # Add the refresh button to the frame
    refresh_button = CTk.CTkButton(button_frame, text="Refresh", command=lambda: display_data(DBActions.fetch_table_data(selected_table)))
    refresh_button.pack(side='left', padx=5)

    # Add the export button to the frame
    export_button = CTk.CTkButton(button_frame, text="Export", command=export_to_file)
    export_button.pack(side='left', padx=5)

rfid_cache = {}

def rfid_scan_event(entry_widget, table_window, selected_table, display_data, data):
    rfid_num = entry_widget.get()

    current_time = time.time()
    if rfid_num in rfid_cache:
        last_scan_time = rfid_cache[rfid_num]
        if current_time - last_scan_time < 15:
            messagebox1 = CTkMessagebox(title="RFID Scan", message=f"{rfid_num} was scanned within the last 15 seconds. Ignoring scan...", icon="warning")
            table_window.after(4500, messagebox1.destroy)  # Close the message box after 5 second
            return

    def insert_digit(index):
        if index < len(rfid_num):
            if not DBActions.member_exists(rfid_num):
                messagebox2 = CTkMessagebox(title="RFID Scan Error", message="RFID number not found", icon="cancel")
                table_window.after(1000, messagebox2.destroy)  # Close the message box after 1 second
                entry_widget.delete(0, CTk.END)
                return

            entry_widget.insert(CTk.END, rfid_num[index])
            DBActions.attendance_member_event(selected_table, rfid_num)
            refresh_data()
            messagebox2 = CTkMessagebox(title="RFID Scan", message="RFID recorded", icon="check")
            table_window.after(1000, messagebox2.destroy)  # Close the message box after 1 second
            entry_widget.delete(0, CTk.END)

    def refresh_data():
        updated_data = DBActions.fetch_table_data(selected_table)
        display_data(updated_data)

    rfid_cache[rfid_num] = current_time
    insert_digit(0)

def rfid_scan_register(entries, table_window):
    rfid_num = entries['rfid_entry'].get()
    member_name = entries['name_entry'].get()
    member_student_num = entries['student_num_entry'].get()
    member_program = entries['program_entry'].get()
    member_year = entries['year_entry'].get()
    ic(rfid_num, member_name, member_program, member_year)

    # Check if the member already exists
    if DBActions.member_exists(rfid_num):
        CTkMessagebox(title="Member Register", message="Member already exists!", icon="error")
    else:
        # Register the new member
        DBActions.member_register(rfid_num, member_name, member_student_num, member_program, member_year)
        if CTkMessagebox(title="Member Register", message="Member Registered!", icon="check"):
            for entry in entries.values():
                entry.delete(0, CTk.END)
            table_window.after(300)

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
    memberid_entry = CTk.CTkEntry(register_window, placeholder_text="Enter member ID")
    memberid_entry.pack(pady=5)

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

    # Define the member_register function to handle the form submission
    def member_register():
        rfid_num = rfid_entry.get()
        member_id = memberid_entry.get()
        member_name = name_entry.get()
        student_num = student_num_entry.get()
        program = program_entry.get()
        year = year_entry.get()
        print(f"RFID: {rfid_num}")
        print(f"Member ID: {member_id}")
        print(f"Name: {member_name}")
        print(f"Student Number: {student_num}")
        print(f"Program: {program}")
        print(f"Year: {year}")

        # Check if the member already exists
        if DBActions.member_exists(rfid_num):
            ic("Member already exists!")
            CTkMessagebox(title="Member Registration", message="Member already exists!", icon="error")
            register_window.after(300, register_window.destroy)
        else:
            # Register the new member
            ic("Registering new member...")
            DBActions.member_register(rfid_num, member_id, member_name, student_num, program, year)
            CTkMessagebox(title="Member Registration", message="Member Registered!", icon="check")
            register_window.after(300, register_window.destroy)

    submit_button = CTk.CTkButton(register_window, text="Submit", command=member_register)
    submit_button.pack(pady=5)


def create_event_button_clicked():
    # Create a new window with a form to create a new event
    event_window = CTk.CTkToplevel()
    event_window.title("Create Event")
    event_window.geometry("400x300")
    event_window.attributes('-topmost', True)  # Ensure the window is on top
    event_window.resizable(False, False)  # Disable resizing
    center_window(event_window)

    # Create and place form fields
    event_name_entry = CTk.CTkEntry(event_window, placeholder_text="Enter event name")
    event_name_entry.pack(pady=5)

    # Function to create event and show confirmation
    def event_create():
        event_name = event_name_entry.get()
        DBActions.create_event_table(event_name)
        CTkMessagebox(title="Event Creation", message="Event Created!", icon="check")
        event_window.after(300, event_window.destroy)

    submit_button = CTk.CTkButton(event_window, text="Submit", command=event_create)
    submit_button.pack(pady=5)


def update_tables_dropdown():
    tables = list_tables(Credentials.db)
    table_dropdown.configure(values=tables)

def center_window(window):
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Get the screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the x and y coordinates to center the window
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Set the position of the window
    window.geometry(f'{window_width}x{window_height}+{x}+{y}')



root = CTk.CTk()
root.title("AHO RFID Events")
root.geometry("400x350")
root.resizable(False, False)

center_window(root)

table_var = CTk.StringVar(value="Select a table")
table_dropdown = CTk.CTkOptionMenu(root, variable=table_var, values=[])
table_dropdown.pack(pady=20)

update_tables_dropdown()

confirm_button = CTk.CTkButton(root, text="Confirm", command=lambda: confirm_button_clicked(table_var))
confirm_button.pack(pady=20)

create_event_button = CTk.CTkButton(root, text="Create Event", command=create_event_button_clicked)
create_event_button.pack(pady=20)

show_memmbers_button = CTk.CTkButton(root, text="Show Members", command=lambda: create_table_window("Members"))
show_memmbers_button.pack(pady=20)

register_member_button = CTk.CTkButton(root, text="Register Member", command=register_member_button_clicked)
register_member_button.pack(pady=20)

root.mainloop()
