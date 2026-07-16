import customtkinter as CTk
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog
import pandas as pd
import time
import threading
from database.dblite import DBActions
from icecream import ic
import sqlite3


class TableManager:
    def __init__(self, app):
        self.app = app

    def create_table_window(self, selected_table):
        table_window = CTk.CTkToplevel(self.app.root)
        table_window.title(f"Event: {selected_table}")
        table_window.geometry('1000x700')
        table_window.attributes('-topmost', True)
        table_window.resizable(True, True)

        # Top section with search and label
        top_frame = CTk.CTkFrame(table_window)
        top_frame.pack(padx=15, pady=(15, 10), fill='x')
        
        search_label = CTk.CTkLabel(top_frame, text="Search Members:", font=CTk.CTkFont(size=12, weight="bold"))
        search_label.pack(anchor='w', pady=(0, 5))
        
        search_entry = CTk.CTkEntry(top_frame, placeholder_text="Type to search by name, ID, or student number...")
        search_entry.pack(fill='x')

        def search_table(event):
            query = search_entry.get().lower()
            filtered_data = [
                row for row in data if any(query in str(cell).lower() for cell in row)
            ]
            display_data(filtered_data)

        search_entry.bind('<KeyRelease>', search_table)

        scrollable_frame = CTk.CTkScrollableFrame(table_window)
        scrollable_frame.pack(fill='both', expand=True, padx=15, pady=10)

        data = DBActions.fetch_table_data(selected_table)

        def display_data(filtered_data):
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            if not filtered_data:
                return

            first_row = filtered_data[0]
            if isinstance(first_row, sqlite3.Row):
                column_names = list(first_row.keys())
            elif isinstance(first_row, dict):
                column_names = list(first_row.keys())
            else:
                column_names = [f"Column {j+1}" for j in range(len(first_row))]

            column_widths = self.calculate_column_widths(filtered_data, column_names)

            header_frame = CTk.CTkFrame(scrollable_frame, fg_color=("gray75", "gray20"))
            header_frame.pack(fill='x', padx=0, pady=(0, 5))

            for j, column_name in enumerate(column_names):
                header = CTk.CTkLabel(
                    header_frame,
                    text=column_name,
                    corner_radius=0,
                    width=column_widths[j],
                    anchor='w',
                    font=CTk.CTkFont(size=12, weight="bold"),
                    fg_color=("gray75", "gray20"),
                    text_color=("black", "white"),
                    padx=12,
                    pady=10
                )
                header.pack(side='left', fill='both', expand=True)

            for i, row in enumerate(filtered_data):
                if isinstance(row, sqlite3.Row):
                    values = list(dict(row).values())
                elif isinstance(row, dict):
                    values = list(row.values())
                else:
                    values = list(row)
                row_bg = ("gray90", "gray25") if i % 2 == 0 else ("gray80", "gray35")
                row_frame = CTk.CTkFrame(scrollable_frame, fg_color=row_bg)
                row_frame.pack(fill='x', padx=0, pady=2)

                for j, cell_data in enumerate(values):
                    cell = CTk.CTkLabel(
                        row_frame,
                        text=str(cell_data),
                        corner_radius=0,
                        width=column_widths[j],
                        anchor='w',
                        fg_color=row_bg,
                        padx=12,
                        pady=8,
                        font=CTk.CTkFont(size=11)
                    )
                    cell.pack(side='left', fill='both', expand=True)
                    cell.bind("<Button-3>", lambda e, text=cell_data: self.copy_to_clipboard(text))

        display_data(data)

        # RFID entry section
        rfid_frame = CTk.CTkFrame(table_window)
        rfid_frame.pack(padx=15, pady=(10, 5), fill='x')
        
        rfid_label = CTk.CTkLabel(rfid_frame, text="Scan RFID Card:", font=CTk.CTkFont(size=12, weight="bold"))
        rfid_label.pack(anchor='w', pady=(0, 5))
        
        rfid_entry = CTk.CTkEntry(rfid_frame, placeholder_text="Place RFID card here to record attendance...")
        rfid_entry.pack(fill='x')
        rfid_entry.bind('<Return>', lambda event: self.rfid_scan_event(rfid_entry, table_window, selected_table, display_data, data))

        # Loading indicator (hidden by default)
        loading_frame = CTk.CTkFrame(table_window)
        loading_frame.pack(padx=15, pady=(0, 5), fill='x')
        loading_spinner = CTk.CTkProgressBar(loading_frame, mode='indeterminate', width=400)
        loading_spinner.pack(pady=(10, 2))
        loading_status = CTk.CTkLabel(loading_frame, text="Processing...", font=CTk.CTkFont(size=11))
        loading_status.pack(pady=(0, 10))
        loading_frame.pack_forget()

        # Store loading widgets on the window for access from rfid_scan_event
        table_window._loading_frame = loading_frame
        table_window._loading_spinner = loading_spinner
        table_window._loading_status = loading_status

        def export_to_file():
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
            if not file_path:
                return
            df = pd.DataFrame(data)
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)

        button_frame = CTk.CTkFrame(table_window)
        button_frame.pack(padx=15, pady=(5, 15), fill='x')

        refresh_button = CTk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            command=lambda: display_data(DBActions.fetch_table_data(selected_table)),
            width=120
        )
        refresh_button.pack(side='left', padx=5)

        export_button = CTk.CTkButton(
            button_frame,
            text="💾 Export",
            command=export_to_file,
            width=120
        )
        export_button.pack(side='left', padx=5)

    def calculate_column_widths(self, data, column_names):
        column_widths = [len(str(col)) * 8 for col in column_names]
        for row in data:
            values = list(dict(row).values()) if isinstance(row, sqlite3.Row) else list(row.values()) if isinstance(row, dict) else list(row)
            for j, value in enumerate(values):
                value_width = len(str(value)) * 7 + 20
                column_widths[j] = max(column_widths[j], value_width)
        column_widths = [max(100, min(400, width)) for width in column_widths]
        return column_widths

    def _show_loading(self, window, message="Processing..."):
        if hasattr(window, '_loading_frame') and window._loading_frame:
            window._loading_status.configure(text=message)
            window._loading_spinner.start()
            window._loading_frame.pack(padx=15, pady=(0, 5), fill='x')
            window.update_idletasks()

    def _hide_loading(self, window):
        if hasattr(window, '_loading_frame') and window._loading_frame:
            window._loading_spinner.stop()
            window._loading_frame.pack_forget()
            window.update_idletasks()

    def rfid_scan_event(self, entry_widget, table_window, selected_table, display_data, data):
        rfid_num = entry_widget.get()

        current_time = time.time()
        if rfid_num in self.app.member_manager.rfid_cache:
            last_scan_time = self.app.member_manager.rfid_cache[rfid_num]
            if current_time - last_scan_time < 15:
                CTkMessagebox(title="RFID Scan", message=f"{rfid_num} was scanned within the last 15 seconds. Ignoring scan...")
                return

        self._show_loading(table_window, "Checking member and recording attendance...")
        entry_widget.configure(state='disabled')

        def scan_worker():
            try:
                result = DBActions.scan_attendance(selected_table, rfid_num)
                table_window.after(0, lambda: self._on_scan_complete(
                    table_window, entry_widget, display_data, selected_table,
                    rfid_num, current_time, result, data
                ))
            except Exception as e:
                table_window.after(0, lambda: self._on_scan_error(table_window, entry_widget, str(e)))

        threading.Thread(target=scan_worker, daemon=True).start()

    def _on_scan_complete(self, table_window, entry_widget, display_data, selected_table, rfid_num, scan_time, result, data):
        self._hide_loading(table_window)
        entry_widget.configure(state='normal')

        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            CTkMessagebox(title="RFID Scan Error", message=error_msg)
            entry_widget.delete(0, CTk.END)
            return

        if result.get('attended'):
            CTkMessagebox(title="RFID Scan", message="Member has already attended this event.")
            entry_widget.delete(0, CTk.END)
            return

        # Successful attendance
        self.app.member_manager.rfid_cache[rfid_num] = scan_time
        CTkMessagebox(title="RFID Scan", message="RFID recorded")
        entry_widget.delete(0, CTk.END)

        # Refresh table data
        updated_data = DBActions.fetch_table_data(selected_table)
        self.app.preloaded_data[selected_table] = updated_data
        display_data(updated_data)

    def _on_scan_error(self, table_window, entry_widget, error_msg):
        self._hide_loading(table_window)
        entry_widget.configure(state='normal')
        CTkMessagebox(title="RFID Scan Error", message=f"Error: {error_msg}")

    def safely_destroy_messagebox(self, messagebox):
        try:
            if messagebox.winfo_exists():
                messagebox.destroy()
        except Exception as e:
            print(f"Error destroying messagebox: {e}")

    def copy_to_clipboard(self, text):
        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(text)
        self.app.root.update()
