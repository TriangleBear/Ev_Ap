import customtkinter as CTk
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog
import pandas as pd
from dblite import DBActions

class ReportsView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        self.header = CTk.CTkLabel(self, text="Reports", font=CTk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=20)
        
        # Create reports options
        self.options_frame = CTk.CTkFrame(self)
        self.options_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Report types
        report_types = [
            {"title": "Attendance Report", "desc": "Generate a report of attendance for a specific event", "command": self.attendance_report},
            {"title": "Members Summary", "desc": "Generate a summary of all members and their points", "command": self.members_summary},
            {"title": "Points Redemption Report", "desc": "View points redemption history", "command": self.redemption_report},
            {"title": "Export Data", "desc": "Export event or member data to CSV or Excel", "command": self.export_data},
        ]
        
        # Create report option buttons
        for i, report in enumerate(report_types):
            report_frame = CTk.CTkFrame(self.options_frame)
            report_frame.pack(fill="x", padx=10, pady=10)
            
            title_label = CTk.CTkLabel(report_frame, text=report["title"], font=CTk.CTkFont(size=18, weight="bold"))
            title_label.pack(anchor="w", padx=10, pady=5)
            
            desc_label = CTk.CTkLabel(report_frame, text=report["desc"], wraplength=400)
            desc_label.pack(anchor="w", padx=10, pady=5)
            
            button = CTk.CTkButton(report_frame, text="Generate Report", command=report["command"])
            button.pack(anchor="e", padx=10, pady=10)
            
    def attendance_report(self):
        # Generate attendance report for a specific event
        tables = self.app.update_tables_dropdown()
        if not tables:
            CTkMessagebox(title="Warning", message="No events available. Please create an event first.", icon="warning")
            return
            
        selection_dialog = CTk.CTkToplevel(self.app.root)
        selection_dialog.title("Select Event")
        selection_dialog.geometry("400x250")
        selection_dialog.resizable(False, False)
        selection_dialog.transient(self.app.root)
        selection_dialog.grab_set()
        
        # Center the dialog
        self.app.center_window(selection_dialog)
        
        CTk.CTkLabel(selection_dialog, text="Select an event for attendance report:", 
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
                self.generate_attendance_report(selected_table)
            else:
                CTkMessagebox(title="Warning", message="Please select an event", icon="warning")
                
        CTk.CTkButton(selection_dialog, text="Generate Report", command=on_select).pack(padx=20, pady=20)
        
    def generate_attendance_report(self, event_name):
        data = DBActions.fetch_table_data(event_name)
        if not data:
            CTkMessagebox(title="No Data", message="No attendance data found for this event.", icon="info")
            return
        
        df = pd.DataFrame(data)
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if not file_path:
            return
        
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        
        CTkMessagebox(title="Report Generated", message="Attendance report generated successfully.", icon="check")
        
    def members_summary(self):
        data = DBActions.fetch_table_data('Members')
        if not data:
            CTkMessagebox(title="No Data", message="No member data found.", icon="info")
            return
        
        df = pd.DataFrame(data)
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if not file_path:
            return
        
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        
        CTkMessagebox(title="Report Generated", message="Members summary report generated successfully.", icon="check")
        
    def redemption_report(self):
        # Implement points redemption report generation
        data = DBActions.fetch_point_data('Members')
        if not data:
            CTkMessagebox(title="No Data", message="No member data found.", icon="info")
            return
        
        df = pd.DataFrame(data)
        df = df[['rfid', 'memberid', 'name', 'points']]  # Select relevant columns
        
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if not file_path:
            return
        
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        
        CTkMessagebox(title="Report Generated", message="Points redemption report generated successfully.", icon="check")
        
    def export_data(self):
        # Export event or member data to CSV or Excel
        tables = self.app.update_tables_dropdown()
        tables.append('Members')
        if not tables:
            CTkMessagebox(title="Warning", message="No data available to export.", icon="warning")
            return
            
        selection_dialog = CTk.CTkToplevel(self.app.root)
        selection_dialog.title("Select Data to Export")
        selection_dialog.geometry("400x250")
        selection_dialog.resizable(False, False)
        selection_dialog.transient(self.app.root)
        selection_dialog.grab_set()
        
        # Center the dialog
        self.app.center_window(selection_dialog)
        
        CTk.CTkLabel(selection_dialog, text="Select data to export:", 
                     font=CTk.CTkFont(size=16)).pack(padx=20, pady=(20, 10))
        
        data_var = CTk.StringVar()
        data_option = CTk.CTkOptionMenu(
            selection_dialog,
            variable=data_var,
            values=tables,
            width=300
        )
        data_option.pack(padx=20, pady=20)
        
        if tables:
            data_var.set(tables[0])
        
        def on_select():
            selected_table = data_var.get()
            if selected_table:
                selection_dialog.destroy()
                self.export_selected_data(selected_table)
            else:
                CTkMessagebox(title="Warning", message="Please select data to export", icon="warning")
                
        CTk.CTkButton(selection_dialog, text="Export Data", command=on_select).pack(padx=20, pady=20)
        
    def export_selected_data(self, table_name):
        data = DBActions.fetch_table_data(table_name)
        if not data:
            CTkMessagebox(title="No Data", message=f"No data found for {table_name}.", icon="info")
            return
        
        df = pd.DataFrame(data)
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if not file_path:
            return
        
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        
        CTkMessagebox(title="Data Exported", message=f"{table_name} data exported successfully.", icon="check")