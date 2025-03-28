from tkinter import TclError
import customtkinter as CTk
from dblite import DBActions, Database
from icecream import ic
import threading
import time

from event_manager import EventManager
from member_manager import MemberManager
from table_manager import TableManager
from home_view import HomeView
# Import other views when needed, not all at startup

class MainApp:
    def __init__(self):
        self.root = CTk.CTk()
        self.root.title("Events Attendance System")
        self.root.geometry("1100x650")
        self.root.resizable(True, True)
        
        # Set default appearance mode and theme
        CTk.set_appearance_mode("System")
        CTk.set_default_color_theme("blue")
        
        # Initialize status variables
        self.initialized_views = {}
        self.db_initialized = False
        self.loading_label = None
        self.loading_status = None
        
        # Show login prompt for cloud database credentials
        self.show_login_prompt()

    def show_login_prompt(self):
        self.login_window = CTk.CTkToplevel(self.root)
        self.login_window.title("Cloud Database Login")
        self.login_window.geometry("300x200")
        self.login_window.resizable(False, False)
        self.login_window.transient(self.root)
        self.login_window.grab_set()
        
        CTk.CTkLabel(self.login_window, text="Cloud Database Login", font=CTk.CTkFont(size=16)).pack(pady=10)
        
        CTk.CTkLabel(self.login_window, text="Username:").pack(anchor="w", padx=20, pady=5)
        self.cloud_user_entry = CTk.CTkEntry(self.login_window)
        self.cloud_user_entry.pack(padx=20, pady=5)
        
        CTk.CTkLabel(self.login_window, text="Password:").pack(anchor="w", padx=20, pady=5)
        self.cloud_password_entry = CTk.CTkEntry(self.login_window, show="*")
        self.cloud_password_entry.pack(padx=20, pady=5)
        
        CTk.CTkButton(self.login_window, text="Login", command=self.on_login_entered).pack(pady=10)
        
        self.center_window(self.login_window)

    def on_login_entered(self):
        cloud_user = self.cloud_user_entry.get()
        cloud_password = self.cloud_password_entry.get()
        self.initialize_app(cloud_user=cloud_user, cloud_password=cloud_password)

    def initialize_app(self, cloud_user=None, cloud_password=None):
        if hasattr(self, 'login_window'):
            self.login_window.destroy()
        
        # Create main layout first for better UX
        self.create_basic_layout()
        
        # Show loading information
        self.loading_label = CTk.CTkLabel(self.content_frame, text="Initializing Application...", 
                                         font=CTk.CTkFont(size=16, weight="bold"))
        self.loading_label.pack(pady=(100, 10))
        
        self.loading_status = CTk.CTkLabel(self.content_frame, text="Connecting to database...")
        self.loading_status.pack(pady=5)
        
        # Initialize progress bar with determinate mode
        self.progress_bar = CTk.CTkProgressBar(self.content_frame, mode='determinate', width=400)
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0.1)
        self.root.update()  # Force UI update
        
        # Initialize database in background thread
        self.database = Database(cloud_user=cloud_user, cloud_password=cloud_password, app=self)
        
        # Start initialization thread
        self.init_thread = threading.Thread(target=self.background_initialization, 
                                           args=(cloud_user, cloud_password))
        self.init_thread.daemon = True
        self.init_thread.start()
        
        # Start polling for completion
        self.root.after(100, self.check_initialization_progress)

    def background_initialization(self, cloud_user=None, cloud_password=None):
        """Perform heavy initialization tasks in background thread"""
        try:
            # Set database instance for DBActions
            DBActions.set_db_instance(self.database)
            
            # Initialize database with timeout handling
            self.database.initialize_db(timeout=10)
            
            # Initialize managers
            self.event_manager = EventManager(self)
            self.member_manager = MemberManager(self)
            self.table_manager = TableManager(self)
            
            # Preload only essential data
            self.preload_essential_data()
            
            # Mark initialization as complete
            self.db_initialized = True
        except Exception as e:
            print(f"Error in background initialization: {e}")
            self.initialization_error = str(e)

    def check_initialization_progress(self):
        """Check if background initialization is complete"""
        if hasattr(self, 'initialization_error'):
            # Show error message
            if self.loading_status:
                self.loading_status.configure(text=f"Error: {self.initialization_error}")
            return
            
        if not self.db_initialized:
            # Update progress animation
            self.progress_bar.set(min(self.progress_bar.get() + 0.05, 0.9))
            self.root.after(100, self.check_initialization_progress)
            return
            
        # Initialization complete
        self.progress_bar.set(1.0)
        
        # Complete UI initialization
        self.finalize_ui_initialization()

    def create_basic_layout(self):
        """Create the basic layout structure first"""
        # Create main layout with two frames: sidebar and content area
        self.sidebar_frame = CTk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar_frame.pack_propagate(False)  # Don't shrink

        self.content_frame = CTk.CTkFrame(self.root)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Create application title in sidebar
        self.app_title = CTk.CTkLabel(self.sidebar_frame, text="AHO RFID App", 
                                     font=CTk.CTkFont(size=20, weight="bold"))
        self.app_title.pack(padx=20, pady=(20, 10))
        
        # Add database connection status label
        self.db_status_label = CTk.CTkLabel(self.sidebar_frame, text="Initializing...", 
                                           font=CTk.CTkFont(size=12, weight="bold"))
        self.db_status_label.pack(side="bottom", pady=10)

    def create_nav_button(self, text, command):
        """Create a navigation button with consistent styling"""
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

    def finalize_ui_initialization(self):
        """Complete the UI initialization after database is ready"""
        # Remove loading indicators
        if self.loading_label:
            self.loading_label.pack_forget()
        if self.loading_status:
            self.loading_status.pack_forget()
        if self.progress_bar:
            self.progress_bar.pack_forget()
        
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
        
        # Initialize only the home view
        self.init_view("home")
        self.show_home_view()
        
        # Update database status
        self.update_db_status_label()
        
        # Center the window
        self.center_window(self.root)

    def preload_essential_data(self):
        """Preload only essential data to speed up startup"""
        self.preloaded_data = {'Members': DBActions.fetch_table_data('Members')}
        # Don't load all tables at startup - defer loading until needed
        self.tables_list = DBActions.list_tables()

    def init_view(self, view_name):
        """Lazily initialize a view only when needed"""
        if view_name in self.initialized_views:
            return self.initialized_views[view_name]
            
        # Import views only when needed
        if view_name == "home":
            from home_view import HomeView
            self.initialized_views[view_name] = HomeView(self.content_frame, self)
        elif view_name == "events":
            from events_view import EventsView
            self.initialized_views[view_name] = EventsView(self.content_frame, self)
        elif view_name == "members":
            from members_view import MembersView
            self.initialized_views[view_name] = MembersView(self.content_frame, self)
        elif view_name == "reports":
            from reports_view import ReportsView
            self.initialized_views[view_name] = ReportsView(self.content_frame, self)
        elif view_name == "settings":
            from settings_view import SettingsView
            self.initialized_views[view_name] = SettingsView(self.content_frame, self)
        elif view_name == "help":
            from help_view import HelpView
            self.initialized_views[view_name] = HelpView(self.content_frame, self)
        elif view_name == "about":
            from about_view import AboutView
            self.initialized_views[view_name] = AboutView(self.content_frame, self)
            
        return self.initialized_views[view_name]

    def show_frame(self, frame_name):
        """Show the requested frame/view, initializing it if needed"""
        # First, make sure the view is initialized
        frame = self.init_view(frame_name)
        
        # Hide all frames
        for initialized_frame in self.initialized_views.values():
            initialized_frame.pack_forget()
        
        # Show the selected frame
        frame.pack(fill="both", expand=True)
        
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
        try:
            # Check if window exists and is mapped (visible)
            if not window.winfo_exists():
                return
            
            # Wait for window to be ready
            window.update_idletasks()
            
            window_width = window.winfo_width()
            window_height = window.winfo_height()
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)
            window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        except (TclError, RuntimeError, Exception) as e:
            print(f"Error centering window: {e}")

    def update_tables_dropdown(self):
        """Fetch tables list on demand instead of at startup"""
        if not hasattr(self, 'tables_list') or not self.tables_list:
            self.tables_list = DBActions.list_tables()
        tables = [table for table in self.tables_list if table != 'Members']
        return tables

    def update_db_status_label(self):
        """Update the database connection status label."""
        self.db_status_label.configure(text="Connected to Cloud MySQL")
