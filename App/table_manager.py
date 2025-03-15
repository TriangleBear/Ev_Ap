import customtkinter as CTk
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog
import pandas as pd
import time
from dblite import DBActions
from icecream import ic

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

        if DBActions.member_attended_event(selected_table, rfid_num):
            messagebox2 = CTkMessagebox(title="RFID Scan", message="Member has already attended this event.", icon="warning")
            table_window.after(4500, messagebox2.destroy)
            entry_widget.delete(0, CTk.END)
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