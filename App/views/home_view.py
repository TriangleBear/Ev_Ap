import customtkinter as CTk
from CTkMessagebox import CTkMessagebox


class Tooltip:
    """Simple tooltip widget for hover text"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        if self.tooltip or not self.text:
            return
        
        # Create tooltip window
        self.tooltip = CTk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        
        # Position tooltip near cursor
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create label in tooltip
        label = CTk.CTkLabel(
            self.tooltip,
            text=self.text,
            bg_color="gray20",
            fg_color="gray20",
            text_color="white",
            padx=10,
            pady=5,
            corner_radius=4
        )
        label.pack()
        
        # Make tooltip stay on top
        self.tooltip.attributes('-topmost', True)
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class HomeView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.event_dropdown = None
        self.create_widgets()

    def create_widgets(self):
        self.header = CTk.CTkLabel(self, text="Dashboard", font=CTk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=20)
        
        # Create grid layout for dashboard cards
        self.grid_frame = CTk.CTkFrame(self)
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Event Attendance Card with Dropdown
        self.card1 = self.create_event_attendance_card()
        self.card1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.card2 = self.create_card(
            "Register Member", 
            "Add new members to the database", 
            "Register Member",
            lambda: self.app.member_manager.register_member_button_clicked()
        )
        self.card2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.card3 = self.create_card(
            "Create Event", 
            "Set up a new event for attendance tracking", 
            "Create Event",
            lambda: self.app.event_manager.create_event_button_clicked()
        )
        self.card3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.card4 = self.create_disabled_redeem_card()
        self.card4.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)
        self.grid_frame.grid_rowconfigure(0, weight=1)
        self.grid_frame.grid_rowconfigure(1, weight=1)
    
    def create_event_attendance_card(self):
        """Create the Event Attendance card with dropdown and Go button"""
        card = CTk.CTkFrame(self.grid_frame)
        
        title_label = CTk.CTkLabel(card, text="Event Attendance", font=CTk.CTkFont(size=18, weight="bold"))
        title_label.pack(padx=20, pady=(20, 10), anchor="w")
        
        desc_label = CTk.CTkLabel(card, text="Scan RFID cards for event attendance", wraplength=250)
        desc_label.pack(padx=20, pady=(0, 20), anchor="w", fill="both", expand=True)
        
        # Dropdown and Button Frame
        control_frame = CTk.CTkFrame(card)
        control_frame.pack(padx=20, pady=(0, 20), fill="x")
        
        # Event Dropdown
        events = self.app.update_tables_dropdown()
        if not events:
            events = ["No events available"]
        
        self.event_dropdown = CTk.CTkComboBox(
            control_frame,
            values=events,
            state="readonly",
            width=150
        )
        self.event_dropdown.pack(side="left", padx=(0, 10), fill="both", expand=True)
        
        if events:
            self.event_dropdown.set(events[0])
        
        # Go Button
        go_button = CTk.CTkButton(
            control_frame,
            text="Go",
            width=60,
            command=self.on_event_selected
        )
        go_button.pack(side="left")
        
        return card
    
    def create_disabled_redeem_card(self):
        """Create the Redeem Points card with disabled state and tooltip"""
        card = CTk.CTkFrame(self.grid_frame)
        
        title_label = CTk.CTkLabel(card, text="Redeem Points", font=CTk.CTkFont(size=18, weight="bold"))
        title_label.pack(padx=20, pady=(20, 10), anchor="w")
        
        desc_label = CTk.CTkLabel(card, text="Process point redemptions for members", wraplength=250)
        desc_label.pack(padx=20, pady=(0, 20), anchor="w", fill="both", expand=True)
        
        # Disabled Button
        redeem_button = CTk.CTkButton(
            card,
            text="Redeem Points",
            state="disabled",
            command=lambda: None
        )
        redeem_button.pack(padx=20, pady=(0, 20), fill="x")
        
        # Add tooltip
        Tooltip(redeem_button, "This feature is temporarily unavailable")
        
        # Apply disabled styling
        disabled_bg = self.app.theme_manager.get_disabled_bg_color()
        disabled_text = self.app.theme_manager.get_disabled_text_color()
        card.configure(fg_color=disabled_bg)
        title_label.configure(text_color=disabled_text)
        desc_label.configure(text_color=disabled_text)
        
        return card
        
    def create_card(self, title, description, button_text, button_command, disabled=False):
        card = CTk.CTkFrame(self.grid_frame)
        
        title_label = CTk.CTkLabel(card, text=title, font=CTk.CTkFont(size=18, weight="bold"))
        title_label.pack(padx=20, pady=(20, 10), anchor="w")
        
        desc_label = CTk.CTkLabel(card, text=description, wraplength=250)
        desc_label.pack(padx=20, pady=(0, 20), anchor="w", fill="both", expand=True)
        
        button = CTk.CTkButton(card, text=button_text, command=button_command, state="normal" if not disabled else "disabled")
        button.pack(padx=20, pady=(0, 20), fill="x")

        if disabled:
            disabled_bg = self.app.theme_manager.get_disabled_bg_color()
            disabled_text = self.app.theme_manager.get_disabled_text_color()
            card.configure(fg_color=disabled_bg)
            title_label.configure(text_color=disabled_text)
            desc_label.configure(text_color=disabled_text)
        
        return card
    
    def on_event_selected(self):
        """Handle event selection from dropdown"""
        if self.event_dropdown is None:
            return
        
        selected_event = self.event_dropdown.get()
        
        if not selected_event or selected_event == "No events available":
            CTkMessagebox(title="Warning", message="No event selected or no events available.")
            return
        
        # Launch the attendance tracking view for the selected event
        self.app.table_manager.create_table_window(selected_event)