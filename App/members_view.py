import customtkinter as CTk
from dblite import DBActions
import sqlite3

class MembersView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        self.header = CTk.CTkLabel(self, text="Members Management", font=CTk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=20)
        
        # Buttons frame
        self.button_frame = CTk.CTkFrame(self)
        self.button_frame.pack(fill="x", padx=20, pady=10)
        
        self.register_member_btn = CTk.CTkButton(
            self.button_frame, 
            text="Register New Member", 
            command=self.app.member_manager.register_member_button_clicked
        )
        self.register_member_btn.pack(side="left", padx=10, pady=10)
        
        self.refresh_btn = CTk.CTkButton(
            self.button_frame,
            text="Refresh",
            command=self.refresh_members
        )
        self.refresh_btn.pack(side="left", padx=10, pady=10)
        
        # Members list frame
        self.members_frame = CTk.CTkFrame(self)
        self.members_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Members list header
        self.list_header = CTk.CTkFrame(self.members_frame)
        self.list_header.pack(fill="x", padx=10, pady=5)
        
        # Add RFID column to the header
        CTk.CTkLabel(self.list_header, text="RFID", width=200, anchor="w", font=CTk.CTkFont(weight="bold")).pack(side="left", padx=5)
        CTk.CTkLabel(self.list_header, text="Member ID", width=200, anchor="w", font=CTk.CTkFont(weight="bold")).pack(side="left", padx=5)
        CTk.CTkLabel(self.list_header, text="Name", width=200, anchor="w", font=CTk.CTkFont(weight="bold")).pack(side="left", padx=5)
        CTk.CTkLabel(self.list_header, text="Student Number", width=200, anchor="w", font=CTk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        # Scrollable frame for members list
        self.members_scrollable = CTk.CTkScrollableFrame(self.members_frame)
        self.members_scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_members()
        
    def refresh_members(self):
        # Clear existing member items
        for widget in self.members_scrollable.winfo_children():
            widget.destroy()
            
        # Get list of members
        members = DBActions.fetch_table_data('Members')
        
        if not members:
            no_members_label = CTk.CTkLabel(
                self.members_scrollable,
                text="No members found. Use the 'Register New Member' button to add one.",
                anchor="center"
            )
            no_members_label.pack(pady=50)
            return
            
        # Add each member as a row
        for i, member in enumerate(members):
            member_frame = CTk.CTkFrame(self.members_scrollable)
            member_frame.pack(fill="x", padx=5, pady=5)
            
            # Handle both tuple and dictionary results
            if isinstance(member, dict) or isinstance(member, sqlite3.Row):
                # Dictionary-like object
                CTk.CTkLabel(member_frame, text=member['rfid'], width=200, anchor="w").pack(side="left", padx=5, pady=10)
                CTk.CTkLabel(member_frame, text=member['memberid'], width=200, anchor="w").pack(side="left", padx=5, pady=10)
                CTk.CTkLabel(member_frame, text=member['name'], width=200, anchor="w").pack(side="left", padx=5, pady=10)
                CTk.CTkLabel(member_frame, text=member['student_num'], width=200, anchor="w").pack(side="left", padx=5, pady=10)
            else:
                # Tuple
                # Assuming order: rfid, memberid, name, student_num, ...
                CTk.CTkLabel(member_frame, text=member[0], width=200, anchor="w").pack(side="left", padx=5, pady=10)  # rfid
                CTk.CTkLabel(member_frame, text=member[1], width=200, anchor="w").pack(side="left", padx=5, pady=10)  # memberid
                CTk.CTkLabel(member_frame, text=member[2], width=200, anchor="w").pack(side="left", padx=5, pady=10)  # name
                CTk.CTkLabel(member_frame, text=member[3], width=200, anchor="w").pack(side="left", padx=5, pady=10)  # student_num

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