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

from event_manager import EventManager
from member_manager import MemberManager
from table_manager import TableManager
from home_view import HomeView
from events_view import EventsView
from members_view import MembersView
from reports_view import ReportsView
from settings_view import SettingsView
from help_view import HelpView
from about_view import AboutView

class MainApp:
    def __init__(self):
        self.root = CTk.CTk()
        self.root.title("Events Attendance System")
        self.root.geometry("1100x650")
        self.root.resizable(True, True)
        
        # Set default appearance mode and theme
        CTk.set_appearance_mode("System")  # "System", "Dark", "Light"
        CTk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
        
        # Initialize managers before creating UI
        self.event_manager = EventManager(self)
        self.member_manager = MemberManager(self)
        self.table_manager = TableManager(self)
        
        # Create the main layout with navigation and content areas
        self.create_layout()
        
        # Preload data
        self.preload_data()
        
        # Center the window
        self.center_window(self.root)

    def create_layout(self):
        # Create main layout with two frames: sidebar and content area
        self.sidebar_frame = CTk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar_frame.pack_propagate(False)  # Don't shrink

        self.content_frame = CTk.CTkFrame(self.root)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Create application title in sidebar
        self.app_title = CTk.CTkLabel(self.sidebar_frame, text="AHO RFID App", font=CTk.CTkFont(size=20, weight="bold"))
        self.app_title.pack(padx=20, pady=(20, 10))
        
        # Create sidebar divider
        self.sidebar_divider1 = CTk.CTkFrame(self.sidebar_frame, height=1, width=160)
        self.sidebar_divider1.pack(pady=(5, 10))
        
        # Create navigation buttons
        self.nav_buttons = {}
        
        self.nav_buttons["home"] = self.create_nav_button("Home", self.show_home_view)
        self.nav_buttons["events"] = self.create_nav_button("Events", self.show_events_view)
        self.nav_buttons["members"] = self.create_nav_button("Members", self.show_members_view)
        self.nav_buttons["reports"] = self.create_nav_button("Reports", self.show_reports_view)
        
        # Create sidebar divider
        self.sidebar_divider2 = CTk.CTkFrame(self.sidebar_frame, height=1, width=160)
        self.sidebar_divider2.pack(pady=10)
        
        self.nav_buttons["settings"] = self.create_nav_button("Settings", self.show_settings_view)
        self.nav_buttons["help"] = self.create_nav_button("Help", self.show_help_view)
        self.nav_buttons["about"] = self.create_nav_button("About", self.show_about_view)
        
        # Create appearance mode toggle
        self.appearance_mode_label = CTk.CTkLabel(self.sidebar_frame, text="Appearance Mode:")
        self.appearance_mode_label.pack(padx=20, pady=(20, 0))
        
        self.appearance_mode_menu = CTk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode
        )
        self.appearance_mode_menu.pack(padx=20, pady=10)
        self.appearance_mode_menu.set("System")
        
        # Create all view frames but show only home initially
        self.create_view_frames()
        self.show_home_view()

    def create_nav_button(self, text, command):
        button = CTk.CTkButton(
            self.sidebar_frame, 
            text=text, 
            fg_color="transparent", 
            anchor="w",
            command=command,
            font=CTk.CTkFont(size=14),
            hover_color=("gray75", "gray25"),
            height=40
        )
        button.pack(padx=20, pady=5, fill="x")
        return button
        
    def create_view_frames(self):
        # Create frames for each view
        self.home_frame = HomeView(self.content_frame, self)
        self.events_frame = EventsView(self.content_frame, self)
        self.members_frame = MembersView(self.content_frame, self)
        self.reports_frame = ReportsView(self.content_frame, self)
        self.settings_frame = SettingsView(self.content_frame, self)
        self.help_frame = HelpView(self.content_frame, self)
        self.about_frame = AboutView(self.content_frame, self)
        
        self.frames = {
            "home": self.home_frame,
            "events": self.events_frame,
            "members": self.members_frame,
            "reports": self.reports_frame,
            "settings": self.settings_frame,
            "help": self.help_frame,
            "about": self.about_frame
        }

    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Show the selected frame
        self.frames[frame_name].pack(fill="both", expand=True)
        
        # Update active button styling
        for name, button in self.nav_buttons.items():
            if name == frame_name:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color="transparent")

    def show_home_view(self):
        self.show_frame("home")
        
    def show_events_view(self):
        self.show_frame("events")
        
    def show_members_view(self):
        self.show_frame("members")
        
    def show_reports_view(self):
        self.show_frame("reports")
        
    def show_settings_view(self):
        self.show_frame("settings")
        
    def show_help_view(self):
        self.show_frame("help")
        
    def show_about_view(self):
        self.show_frame("about")
        
    def change_appearance_mode(self, new_appearance_mode):
        CTk.set_appearance_mode(new_appearance_mode)

    def preload_data(self):
        self.preloaded_data = {}
        tables = DBActions.list_tables()
        for table in tables:
            self.preloaded_data[table] = DBActions.fetch_table_data(table)
        self.preloaded_data['Members'] = DBActions.fetch_table_data('Members')
        ic(self.preloaded_data)

    def run(self):
        self.root.mainloop()

    def center_window(self, window):
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
    def update_tables_dropdown(self):
        if not Database.db_exists():
            Database.initialize_db()
        tables = DBActions.list_tables()
        tables = [table for table in tables if table != 'Members']
        ic(tables)
        return tables
