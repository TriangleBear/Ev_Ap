import customtkinter as CTk
from dblite import DBActions
import sqlite3

class MembersView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        self.search_entry = CTk.CTkEntry(self, placeholder_text="Search Members")
        self.search_entry.pack(padx=10, pady=10, fill='x')
        self.search_entry.bind('<KeyRelease>', self.search_members)

        self.scrollable_frame = CTk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(fill='both', expand=True)

        self.refresh_button = CTk.CTkButton(self, text="Refresh", command=self.refresh_members)
        self.refresh_button.pack(pady=10)

        self.refresh_members()

    def refresh_members(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        members = DBActions.fetch_table_data('Members')
        for i, member in enumerate(members):
            values = list(dict(member).values()) if isinstance(member, sqlite3.Row) else member
            for j, cell_data in enumerate(values):
                cell = CTk.CTkLabel(self.scrollable_frame, text=cell_data, corner_radius=0, width=100, anchor='w')
                cell.grid(row=i, column=j, padx=5, pady=5, sticky='w')
                cell.bind("<Button-3>", lambda e, text=cell_data: self.copy_to_clipboard(text))

    def search_members(self, event):
        query = self.search_entry.get().lower()
        filtered_members = [
            member for member in DBActions.fetch_table_data('Members') if any(query in str(cell).lower() for cell in member)
        ]
        self.display_members(filtered_members)

    def display_members(self, members):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for i, member in enumerate(members):
            values = list(dict(member).values()) if isinstance(member, sqlite3.Row) else member
            for j, cell_data in enumerate(values):
                cell = CTk.CTkLabel(self.scrollable_frame, text=cell_data, corner_radius=0, width=100, anchor='w')
                cell.grid(row=i, column=j, padx=5, pady=5, sticky='w')
                cell.bind("<Button-3>", lambda e, text=cell_data: self.copy_to_clipboard(text))

    def copy_to_clipboard(self, text):
        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(text)
        self.app.root.update()  # now it stays on the clipboard after the window is closed