import customtkinter as CTk
from dblite import DBActions
import sqlite3

class MembersView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.initialized = False
        self.members_cache = []  # Cache for member data
        self.create_widgets()  # Ensure widgets are created during initialization

    def create_widgets(self):
        # Initialize UI components only when the view is shown
        if self.initialized:
            return
        self.initialized = True

        self.header = CTk.CTkLabel(self, text="Members Management", font=CTk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=20)
        
        # Search bar
        self.search_entry = CTk.CTkEntry(self, placeholder_text="Search members...")
        self.search_entry.pack(padx=20, pady=10, fill="x")
        self.search_entry.bind('<KeyRelease>', self.search_members)
        
        # Members list frame
        self.members_frame = CTk.CTkFrame(self)
        self.members_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Members list header
        self.list_header = CTk.CTkFrame(self.members_frame)
        self.list_header.pack(fill="x", padx=10, pady=5)
        
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
            
        # Fetch and cache member data
        try:
            self.members_cache = DBActions.fetch_table_data('Members')
        except Exception as e:
            self.members_cache = []
            print(f"Error fetching members: {e}")
        
        if not self.members_cache:
            no_members_label = CTk.CTkLabel(
                self.members_scrollable,
                text="No members found. Use the 'Register New Member' button to add one.",
                anchor="center"
            )
            no_members_label.pack(pady=50)
            return
            
        # Display all members
        self.display_members(self.members_cache)

    def search_members(self, event):
        query = self.search_entry.get().lower()
        filtered_members = [
            member for member in self.members_cache if any(query in str(value).lower() for value in member.values())
        ]
        self.display_members(filtered_members)

    def display_members(self, members):
        # Clear existing member items
        for widget in self.members_scrollable.winfo_children():
            widget.destroy()
            
        if not members:
            no_members_label = CTk.CTkLabel(
                self.members_scrollable,
                text="No matching members found.",
                anchor="center"
            )
            no_members_label.pack(pady=50)
            return
            
        # Add each member as a row
        for i, member in enumerate(members):
            member_frame = CTk.CTkFrame(self.members_scrollable)
            member_frame.pack(fill="x", padx=5, pady=5)
            
            # Access dictionary keys instead of indices
            CTk.CTkLabel(member_frame, text=member['rfid'], width=200, anchor="w").pack(side="left", padx=5, pady=10)  # rfid
            CTk.CTkLabel(member_frame, text=member['memberid'], width=200, anchor="w").pack(side="left", padx=5, pady=10)  # memberid
            CTk.CTkLabel(member_frame, text=member['name'], width=200, anchor="w").pack(side="left", padx=5, pady=10)  # name
            CTk.CTkLabel(member_frame, text=member['student_num'], width=200, anchor="w").pack(side="left", padx=5, pady=10)  # student_num

    def copy_to_clipboard(self, text):
        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(text)
        self.app.root.update()  # now it stays on the clipboard after the window is closed