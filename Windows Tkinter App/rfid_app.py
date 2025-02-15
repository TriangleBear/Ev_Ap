import customtkinter as CTk
from CTkMessagebox import CTkMessagebox
from tkinter import PhotoImage
from dblite import DBActions, Database
import time
import pandas as pd
from customtkinter import filedialog
from icecream import ic
import os
import sys

class RFIDApp:
    def __init__(self):
        self.rfid_cache = {}
        self.root = CTk.CTk()
        self.root.title("Events Attendance")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        self.table_var = CTk.StringVar(value="Select a table")
        self.table_dropdown = CTk.CTkOptionMenu(self.root, variable=self.table_var, values=[])
        self.table_dropdown.pack(pady=20)
        self.update_tables_dropdown()
        self.create_widgets()
        self.center_window(self.root)
        self.points_per_event = {}

    def create_widgets(self):
        confirm_button = CTk.CTkButton(self.root, text="Confirm", command=lambda: self.confirm_button_clicked(self.table_var))
        confirm_button.pack(pady=20)

        create_event_button = CTk.CTkButton(self.root, text="Create Event", command=self.create_event_button_clicked)
        create_event_button.pack(pady=20)

        show_memmbers_button = CTk.CTkButton(self.root, text="Show Members", command=lambda: self.create_table_window("Members"))
        show_memmbers_button.pack(pady=20)

        register_member_button = CTk.CTkButton(self.root, text="Register Member", command=self.register_member_button_clicked)
        register_member_button.pack(pady=20)

        redeem_points_button = CTk.CTkButton(self.root, text="Redeem Points", command=self.redeem_points_button_clicked)
        redeem_points_button.pack(pady=20)

    def run(self):
        self.root.mainloop()

    def list_tables(self, selected_table):
        tables = DBActions.list_tables(Credentials.db)
        if tables is None:
            return []
        return [table for table in tables if table != 'Members']

    def confirm_button_clicked(self, table_var):
        selected_table = table_var.get()
        if not selected_table:
            CTkMessagebox(title="Warning", message="No table selected", icon="warning")
        elif selected_table == "Select a table":
            CTkMessagebox(title="Warning", message="Please select a table", icon="warning")
        elif selected_table == "Members":
            CTkMessagebox(title="Warning", message="The 'Members' table cannot be selected", icon="warning")
        else:
            self.create_table_window(selected_table)

    def create_table_window(self, selected_table):
        table_window = CTk.CTkToplevel()
        table_window.title(f"Event: {selected_table}")
        table_window.geometry('600x600')  # Set fixed window size
        table_window.attributes('-topmost', False)

        def search_table(event):
            query = search_entry.get().lower()  # Convert the query to lowercase
            filtered_data = [
                row for row in data if any(query in str(cell).lower() for cell in row.values() if isinstance(row, dict)) or any(query in str(cell).lower() for cell in row)
            ]
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

            points = self.points_per_event.get(selected_table, 0)
            DBActions.add_points(rfid_num, points)

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
            # Register the new member
            DBActions.member_register(rfid_num, member_name, member_student_num, member_program, member_year)
            if CTkMessagebox(title="Member Register", message="Member Registered!", icon="check"):
                for entry in entries.values():
                    entry.delete(0, CTk.END)
                table_window.after(300)

    def create_event_button_clicked(self):
        # Create a new window with a form to create a new event
        event_window = CTk.CTkToplevel()
        event_window.title("Create Event")
        event_window.geometry("400x300")
        event_window.attributes('-topmost', False)  # Ensure the window is not always on top
        event_window.resizable(False, False)  # Disable resizing
        self.center_window(event_window)

        # Create and place form fields
        event_name_entry = CTk.CTkEntry(event_window, placeholder_text="Enter event name")
        event_name_entry.pack(pady=5)

        points_entry = CTk.CTkEntry(event_window, placeholder_text="Enter points for this event")
        points_entry.pack(pady=5)

        # Function to create the event and show confirmation
        def event_create():
            event_name = event_name_entry.get().strip()  # Get the event name and remove extra spaces
            points = points_entry.get().strip()

            if not event_name or not points:  # Check if the event name or points are empty
                CTkMessagebox(title="Event Creation", message="Event name and points cannot be empty!", icon="error")
                return

            try:
                points = float(points)
                # Create the event table
                DBActions.create_event_table(event_name)
                self.points_per_event[event_name] = points
                CTkMessagebox(title="Event Creation", message="Event Created!", icon="check")

                # Refresh the dropdown to include the new table
                self.update_tables_dropdown()

                # Close the event window
                event_window.destroy()
            except Exception as e:
                # Handle any errors during table creation
                CTkMessagebox(title="Event Creation Error", message=f"Error creating event: {str(e)}", icon="error")

        # Add the submit button to the form
        submit_button = CTk.CTkButton(event_window, text="Submit", command=event_create)
        submit_button.pack(pady=5)

    def register_member_button_clicked(self):
        ic("register_member_button_clicked")
        # Create a new window with a form to register a new member
        register_window = CTk.CTkToplevel()
        register_window.title("Register New Member")
        register_window.geometry("400x300")
        register_window.attributes('-topmost', False)  # Ensure the window is on top
        register_window.resizable(False, False)  # Disable resizing
        self.center_window(register_window)

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

    def redeem_points_button_clicked(self):
        redeem_window = CTk.CTkToplevel()
        redeem_window.title("Redeem Points")
        redeem_window.geometry("400x300")
        redeem_window.attributes('-topmost', False)
        self.center_window(redeem_window)

        rfid_entry = CTk.CTkEntry(redeem_window, placeholder_text="Enter RFID")
        rfid_entry.pack(pady=5)

        points_entry = CTk.CTkEntry(event_window, placeholder_text="Enter points for this event")
        points_entry.pack(pady=5)

        # Function to create the event and show confirmation
        def event_create():
            event_name = event_name_entry.get().strip()  # Get the event name and remove extra spaces
            points = points_entry.get().strip()

            if not event_name or not points:  # Check if the event name or points are empty
                CTkMessagebox(title="Event Creation", message="Event name and points cannot be empty!", icon="error")
        def redeem_points():
            rfid_num = rfid_entry.get().strip()
            if not rfid_num:
                CTkMessagebox(title="Redeem Points", message="RFID cannot be empty!", icon="error")
                return
            points = DBActions.get_member_points(rfid_num)
            if points is None:
                CTkMessagebox(title="Redeem Points", message="Member not found!", icon="error")
                return
            discount_20 = points * 0.20
            discount_50 = points * 0.50
            response = CTkMessagebox(title="Redeem Points", message=f"Points: {points}\n20% Discount: {discount_20}\n50% Discount: {discount_50}", icon="question", option_1="20%", option_2="50%")
            if response.get() == "20%":
                DBActions.redeem_points(rfid_num, discount_20)
            elif response.get() == "50%":
                DBActions.redeem_points(rfid_num, discount_50)
            CTkMessagebox(title="Redeem Points", message="Points redeemed successfully!", icon="check")
            redeem_window.destroy()

            try:
                points = float(points)
                # Create the event table
                DBActions.create_event_table(event_name)
                self.points_per_event[event_name] = points
                CTkMessagebox(title="Event Creation", message="Event Created!", icon="check")

                # Refresh the dropdown to include the new table
                self.update_tables_dropdown()

                # Close the event window
                event_window.destroy()
            except Exception as e:
                # Handle any errors during table creation
                CTkMessagebox(title="Event Creation Error", message=f"Error creating event: {str(e)}", icon="error")

        # Add the submit button to the form
        submit_button = CTk.CTkButton(event_window, text="Submit", command=event_create)
        submit_button.pack(pady=5)
        redeem_button = CTk.CTkButton(redeem_window, text="Redeem", command=redeem_points)
        redeem_button.pack(pady=5)

def register_member_button_clicked():
    ic("register_member_button_clicked")
    # Create a new window with a form to register a new member
    register_window = CTk.CTkToplevel()
    register_window.title("Register New Member")
    register_window.geometry("400x300")
    register_window.attributes('-topmost', False)  # Ensure the window is on top
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

    def redeem_points_button_clicked(self):
        redeem_window = CTk.CTkToplevel()
        redeem_window.title("Redeem Points")
        redeem_window.geometry("400x300")
        redeem_window.attributes('-topmost', False)
        self.center_window(redeem_window)

        rfid_entry = CTk.CTkEntry(redeem_window, placeholder_text="Enter RFID")
        rfid_entry.pack(pady=5)

        def redeem_points():
            rfid_num = rfid_entry.get().strip()
            if not rfid_num:
                CTkMessagebox(title="Redeem Points", message="RFID cannot be empty!", icon="error")
                return
            points = DBActions.get_member_points(rfid_num)
            if points is None:
                CTkMessagebox(title="Redeem Points", message="Member not found!", icon="error")
                return
            discount_20 = points * 0.20
            discount_50 = points * 0.50
            response = CTkMessagebox(title="Redeem Points", message=f"Points: {points}\n20% Discount: {discount_20}\n50% Discount: {discount_50}", icon="question", option_1="20%", option_2="50%")
            if response.get() == "20%":
                DBActions.redeem_points(rfid_num, discount_20)
            elif response.get() == "50%":
                DBActions.redeem_points(rfid_num, discount_50)
            CTkMessagebox(title="Redeem Points", message="Points redeemed successfully!", icon="check")
            redeem_window.destroy()

        redeem_button = CTk.CTkButton(redeem_window, text="Redeem", command=redeem_points)
        redeem_button.pack(pady=5)

    def update_tables_dropdown(self):
        # Check if the database exists or needs to be created
        if not Database.db_exists():
            # If the database doesn't exist, initialize it
            Database.initialize_db()  # This creates the database and tables

    # Fetch the list of tables, excluding the restricted 'Members' table
    tables = DBActions.list_tables()
    tables = [table for table in tables if table != 'Members']  # Exclude 'Members' table

    # Debugging: Check the list of tables
    ic(tables)  # This will print the list of tables for debugging

    # Update the dropdown with the fetched tables
    if tables:
        self.table_dropdown.configure(values=tables)
        if "Select a table" not in tables:
            self.table_dropdown.set("Select a table")  # Set a default option
    else:
        # Handle the case where no tables are found
        self.table_dropdown.configure(values=["No tables available"])
        self.table_dropdown.set("No tables available")

    def center_window(self, window):
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

if __name__ == "__main__":
    app = RFIDApp()
    app.run()
