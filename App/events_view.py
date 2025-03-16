import customtkinter as CTk
from CTkMessagebox import CTkMessagebox
from dblite import DBActions, Database

class EventsView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        self.header = CTk.CTkLabel(self, text="Events Management", font=CTk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=20)
        
        # Buttons frame
        self.button_frame = CTk.CTkFrame(self)
        self.button_frame.pack(fill="x", padx=20, pady=10)
        
        self.create_event_btn = CTk.CTkButton(
            self.button_frame, 
            text="Create New Event", 
            command=self.app.event_manager.create_event_button_clicked
        )
        self.create_event_btn.pack(side="left", padx=10, pady=10)
        
        self.refresh_btn = CTk.CTkButton(
            self.button_frame,
            text="Refresh",
            command=self.refresh_events
        )
        self.refresh_btn.pack(side="left", padx=10, pady=10)
        
        # Events list frame
        self.events_frame = CTk.CTkFrame(self)
        self.events_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Event list header
        self.list_header = CTk.CTkFrame(self.events_frame)
        self.list_header.pack(fill="x", padx=10, pady=5)
        
        CTk.CTkLabel(self.list_header, text="Event Name", width=200, anchor="w", font=CTk.CTkFont(weight="bold")).pack(side="left", padx=5)
        CTk.CTkLabel(self.list_header, text="Actions", width=200, anchor="w", font=CTk.CTkFont(weight="bold")).pack(side="right", padx=5)
        
        # Scrollable frame for event list
        self.events_scrollable = CTk.CTkScrollableFrame(self.events_frame)
        self.events_scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_events()
        
    def refresh_events(self):
        # Clear existing event items
        for widget in self.events_scrollable.winfo_children():
            widget.destroy()
            
        # Get list of events
        events = self.app.update_tables_dropdown()
        
        if not events:
            no_events_label = CTk.CTkLabel(
                self.events_scrollable,
                text="No events found. Use the 'Create New Event' button to add one.",
                anchor="center"
            )
            no_events_label.pack(pady=50)
            return
            
        # Add each event as a row
        for i, event in enumerate(events):
            event_frame = CTk.CTkFrame(self.events_scrollable)
            event_frame.pack(fill="x", padx=5, pady=5)
            
            CTk.CTkLabel(event_frame, text=event, width=200, anchor="w").pack(side="left", padx=5, pady=10)
            
            actions_frame = CTk.CTkFrame(event_frame, fg_color="transparent")
            actions_frame.pack(side="right", padx=5, pady=5)
            
            CTk.CTkButton(
                actions_frame, 
                text="View Attendance", 
                command=lambda e=event: self.app.table_manager.create_table_window(e)
            ).pack(side="left", padx=5)
            
            CTk.CTkButton(
                actions_frame, 
                text="Delete Event", 
                command=lambda e=event: self.confirm_delete_event(e)
            ).pack(side="left", padx=5)
            
    def confirm_delete_event(self, event_name):
        response = CTkMessagebox(title="Delete Event", message=f"Are you sure you want to delete the event '{event_name}'?", icon="warning", option_1="Yes", option_2="No")
        if response.get() == "Yes":
            self.delete_event(event_name)
            
    def delete_event(self, event_name):
        try:
            with Database().get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"DROP TABLE IF EXISTS `{event_name}`")
                conn.commit()
            CTkMessagebox(title="Delete Event", message=f"Event '{event_name}' deleted successfully.", icon="check")
            self.refresh_events()
        except Exception as e:
            CTkMessagebox(title="Delete Event Error", message=f"Error deleting event: {str(e)}", icon="error")
            
    def open_event(self, event_name):
        self.app.table_manager.create_table_window(event_name)