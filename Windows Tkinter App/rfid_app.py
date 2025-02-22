import customtkinter as CTk
from CTkMessagebox import CTkMessagebox
from tkinter import PhotoImage
from dblite import DBActions, Database
import time
import pandas as pd
from customtkinter import filedialog
import openpyxl
from icecream import ic
import os
import sys
import sqlite3

class MainApp:
    def __init__(self):
        self.root = CTk.CTk()
        self.root.title("Events Attendance")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        self.table_var = CTk.StringVar(value="Select a table")
        self.table_dropdown = CTk.CTkOptionMenu(self.root, variable=self.table_var, values=[])
        self.table_dropdown.pack(pady=20)
        self.event_manager = EventManager(self)
        self.member_manager = MemberManager(self)
        self.table_manager = TableManager(self)
        self.preload_data()
        self.create_widgets()
        self.update_tables_dropdown()
        self.center_window(self.root)

    def preload_data(self):
        self.preloaded_data = {}
        tables = DBActions.list_tables()
        for table in tables:
            self.preloaded_data[table] = DBActions.fetch_table_data(table)
        self.preloaded_data['Members'] = DBActions.fetch_table_data('Members')
        ic(self.preloaded_data)

    def create_widgets(self):
        confirm_button = CTk.CTkButton(self.root, text="Confirm", command=lambda: self.confirm_button_clicked(self.table_var))
        confirm_button.pack(pady=20)

        create_event_button = CTk.CTkButton(self.root, text="Create Event", command=self.event_manager.create_event_button_clicked)
        create_event_button.pack(pady=20)

        show_memmbers_button = CTk.CTkButton(self.root, text="Show Members", command=lambda: self.table_manager.create_table_window("Members"))
        show_memmbers_button.pack(pady=20)

        register_member_button = CTk.CTkButton(self.root, text="Register Member", command=self.member_manager.register_member_button_clicked)
        register_member_button.pack(pady=20)

        redeem_points_button = CTk.CTkButton(self.root, text="Redeem Points", command=self.member_manager.redeem_points_button_clicked)
        redeem_points_button.pack(pady=20)

    def run(self):
        self.root.mainloop()

    def confirm_button_clicked(self, table_var):
        selected_table = table_var.get()
        if not selected_table:
            CTkMessagebox(title="Warning", message="No table selected", icon="warning")
        elif selected_table == "Select a table":
            CTkMessagebox(title="Warning", message="Please select a table", icon="warning")
        elif selected_table == "Members":
            CTkMessagebox(title="Warning", message="The 'Members' table cannot be selected", icon="warning")
        else:
            self.table_manager.create_table_window(selected_table)

    def update_tables_dropdown(self):
        if not Database.db_exists():
            Database.initialize_db()
        tables = DBActions.list_tables()
        tables = [table for table in tables if table != 'Members']
        ic(tables)
        if tables:
            self.table_dropdown.configure(values=tables)
            if "Select a table" not in tables:
                self.table_dropdown.set("Select a table")
        else:
            self.table_dropdown.configure(values=["No tables available"])
            self.table_dropdown.set("No tables available")

    def center_window(self, window):
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        window.geometry(f'{window_width}x{window_height}+{x}+{y}')

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

class MemberManager:
    def __init__(self, app):
        self.app = app
        self.rfid_cache = {}

    def register_member_button_clicked(self):
        ic("register_member_button_clicked")
        register_window = CTk.CTkToplevel()
        register_window.title("Register New Member")
        register_window.geometry("400x300")
        register_window.attributes('-topmost', False)
        register_window.resizable(False, False)
        self.app.center_window(register_window)

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

            if DBActions.member_exists(rfid_num):
                ic("Member already exists!")
                CTkMessagebox(title="Member Registration", message="Member already exists!", icon="error")
                register_window.after(300, register_window.destroy)
            else:
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
        self.app.center_window(redeem_window)

        rfid_entry = CTk.CTkEntry(redeem_window, placeholder_text="Enter RFID")
        rfid_entry.pack(pady=5)

        points_entry = CTk.CTkEntry(redeem_window, placeholder_text="Enter points to redeem")
        points_entry.pack(pady=5)

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

class TableManager:
    def __init__(self, app):
        self.app = app

    def create_table_window(self, selected_table):
        table_window = CTk.CTkToplevel()
        table_window.title(f"Event: {selected_table}")
        table_window.geometry('800x600')
        table_window.attributes('-topmost', False)
        table_window.resizable(True, True)

        def search_table(event):
            query = search_entry.get().lower()
            filtered_data = [
                row for row in data if any(query in str(cell).lower() for cell in row)
            ]
            display_data(filtered_data)

        search_entry = CTk.CTkEntry(table_window)
        search_entry.pack(padx=10, pady=10, fill='x')
        search_entry.bind('<KeyRelease>', search_table)

        scrollable_frame = CTk.CTkScrollableFrame(table_window)
        scrollable_frame.pack(fill='both', expand=True)

        data = self.app.preloaded_data.get(selected_table, [])

        def display_data(filtered_data):
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            for i, row in enumerate(filtered_data):
                values = list(dict(row).values()) if isinstance(row, sqlite3.Row) else row
                for j, cell_data in enumerate(values):
                    cell = CTk.CTkLabel(scrollable_frame, text=cell_data, corner_radius=0, width=100, anchor='w')
                    cell.grid(row=i, column=j, padx=5, pady=5, sticky='w')
                    cell.bind("<Button-3>", lambda e, text=cell_data: self.copy_to_clipboard(text))

        display_data(data)

        rfid_entry = CTk.CTkEntry(table_window)
        rfid_entry.pack(padx=10, pady=10, fill='x')
        rfid_entry.bind('<Return>', lambda event: self.rfid_scan_event(rfid_entry, table_window, selected_table, display_data, data))

        def export_to_file():
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
            if not file_path:
                return
            df = pd.DataFrame(self.app.preloaded_data.get(selected_table, []))
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)

        button_frame = CTk.CTkFrame(table_window)
        button_frame.pack(side='top', anchor='ne', padx=10, pady=10)

        refresh_button = CTk.CTkButton(button_frame, text="Refresh", command=lambda: display_data(self.app.preloaded_data.get(selected_table, [])))
        refresh_button.pack(side='left', padx=5)

        export_button = CTk.CTkButton(button_frame, text="Export", command=export_to_file)
        export_button.pack(side='left', padx=5)

    def rfid_scan_event(self, entry_widget, table_window, selected_table, display_data, data):
        rfid_num = entry_widget.get()

        current_time = time.time()
        if rfid_num in self.app.member_manager.rfid_cache:
            last_scan_time = self.app.member_manager.rfid_cache[rfid_num]
            if current_time - last_scan_time < 15:
                messagebox1 = CTkMessagebox(title="RFID Scan", message=f"{rfid_num} was scanned within the last 15 seconds. Ignoring scan...", icon="warning")
                table_window.after(4500, messagebox1.destroy)
                return

        def insert_digit(index):
            if index < len(rfid_num):
                member = DBActions.member_exists(rfid_num)
                if not member:
                    messagebox2 = CTkMessagebox(title="RFID Scan Error", message="RFID number not found", icon="cancel")
                    table_window.after(1000, messagebox2.destroy)
                    entry_widget.delete(0, CTk.END)
                    return

                entry_widget.insert(CTk.END, rfid_num[index])
                DBActions.attendance_member_event(selected_table, rfid_num)
                refresh_data()
                messagebox2 = CTkMessagebox(title="RFID Scan", message="RFID recorded", icon="check")
                table_window.after(1000, messagebox2.destroy)
                entry_widget.delete(0, CTk.END)

                points = self.app.event_manager.points_per_event.get(selected_table, 0.10)
                ic(f"Adding {points} points to RFID {rfid_num} for event {selected_table}")
                DBActions.add_points(rfid_num, points)

        def refresh_data():
            updated_data = DBActions.fetch_table_data(selected_table)
            self.app.preloaded_data[selected_table] = updated_data
            display_data(updated_data)

        self.app.member_manager.rfid_cache[rfid_num] = current_time
        insert_digit(0)

    def copy_to_clipboard(self, text):
        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(text)
        self.app.root.update()  # now it stays on the clipboard after the window is closed

if __name__ == "__main__":
    app = MainApp()
    app.run()
