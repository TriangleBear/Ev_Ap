import customtkinter as CTk
from CTkMessagebox import CTkMessagebox

class HomeView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        self.header = CTk.CTkLabel(self, text="Dashboard", font=CTk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=20)
        
        # Create grid layout for dashboard cards
        self.grid_frame = CTk.CTkFrame(self)
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Quick access buttons
        self.card1 = self.create_card(
            "Event Attendance", 
            "Scan RFID cards for event attendance", 
            "Track Attendance",
            lambda: self.show_event_selection()
        )
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
        
        self.card4 = self.create_card(
            "Redeem Points", 
            "Process point redemptions for members", 
            "Redeem Points",
            lambda: self.app.member_manager.redeem_points_button_clicked()
        )
        self.card4.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)
        self.grid_frame.grid_rowconfigure(0, weight=1)
        self.grid_frame.grid_rowconfigure(1, weight=1)
        
    def create_card(self, title, description, button_text, button_command):
        card = CTk.CTkFrame(self.grid_frame)
        
        title_label = CTk.CTkLabel(card, text=title, font=CTk.CTkFont(size=18, weight="bold"))
        title_label.pack(padx=20, pady=(20, 10), anchor="w")
        
        desc_label = CTk.CTkLabel(card, text=description, wraplength=250)
        desc_label.pack(padx=20, pady=(0, 20), anchor="w", fill="both", expand=True)
        
        button = CTk.CTkButton(card, text=button_text, command=button_command)
        button.pack(padx=20, pady=(0, 20), fill="x")
        
        return card
        
    def show_event_selection(self):
        # Similar to the original confirm_button_clicked but with improved UI
        tables = self.app.update_tables_dropdown()
        if not tables:
            CTkMessagebox(title="Warning", message="No events available. Please create an event first.")
            return
            
        selection_dialog = CTk.CTkToplevel(self.app.root)
        selection_dialog.title("Select Event")
        selection_dialog.geometry("400x250")
        selection_dialog.resizable(False, False)
        selection_dialog.transient(self.app.root)
        selection_dialog.grab_set()
        
        # Center the dialog
        self.app.center_window(selection_dialog)
        
        CTk.CTkLabel(selection_dialog, text="Select an event for attendance tracking:", 
                     font=CTk.CTkFont(size=16)).pack(padx=20, pady=(20, 10))
        
        event_var = CTk.StringVar()
        event_option = CTk.CTkOptionMenu(
            selection_dialog,
            variable=event_var,
            values=tables,
            width=300
        )
        event_option.pack(padx=20, pady=20)
        
        if tables:
            event_var.set(tables[0])
        
        def on_select():
            selected_table = event_var.get()
            if selected_table:
                selection_dialog.destroy()
                self.app.table_manager.create_table_window(selected_table)
            else:
                CTkMessagebox(title="Warning", message="Please select an event")
                
        CTk.CTkButton(selection_dialog, text="Track Attendance", command=on_select).pack(padx=20, pady=20)