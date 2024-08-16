import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

class DatabaseEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Database Editor and Creator")

        # Database folder path
        self.db_folder = "/.DBsavefile"
        # Get the full path of the db_folder
        full_db_folder_path = os.path.abspath(self.db_folder)
        print(f"Full path of db_folder: {full_db_folder_path}")

        # List all .db files in the db_folder
        db_files = [f for f in os.listdir(full_db_folder_path) if f.endswith('.db')]
        print("Databases in the folder:")
        for db_file in db_files:
            print(db_file)

        # Database name dropdown
        self.db_name_label = tk.Label(root, text="Database Name:")
        self.db_name_label.grid(row=0, column=0, padx=10, pady=10)
        self.db_name_combobox = ttk.Combobox(root)
        self.db_name_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.populate_db_dropdown()

        # Table name input
        self.table_name_label = tk.Label(root, text="Table Name:")
        self.table_name_label.grid(row=1, column=0, padx=10, pady=10)
        self.table_name_entry = tk.Entry(root)
        self.table_name_entry.grid(row=1, column=1, padx=10, pady=10)

        # Column name input
        self.column_name_label = tk.Label(root, text="Column Name:")
        self.column_name_label.grid(row=2, column=0, padx=10, pady=10)
        self.column_name_entry = tk.Entry(root)
        self.column_name_entry.grid(row=2, column=1, padx=10, pady=10)

        # Column type dropdown
        self.column_type_label = tk.Label(root, text="Column Type:")
        self.column_type_label.grid(row=3, column=0, padx=10, pady=10)
        self.column_type_combobox = ttk.Combobox(root, values=["TEXT", "INTEGER", "REAL", "BLOB"])
        self.column_type_combobox.grid(row=3, column=1, padx=10, pady=10)
        self.column_type_combobox.current(0)

        # Add column button
        self.add_column_button = tk.Button(root, text="Add Column", command=self.add_column)
        self.add_column_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Execute button
        self.execute_button = tk.Button(root, text="Execute", command=self.create_table)
        self.execute_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Preview text field
        self.preview_label = tk.Label(root, text="SQL Preview:")
        self.preview_label.grid(row=6, column=0, padx=10, pady=10)
        self.preview_text = tk.Text(root, height=5, width=50)
        self.preview_text.grid(row=6, column=1, padx=10, pady=10)

        # List to store columns
        self.columns = []

    def populate_db_dropdown(self):
        db_files = [f for f in os.listdir(self.db_folder) if f.endswith('.db')]
        self.db_name_combobox['values'] = db_files

    def add_column(self):
        column_name = self.column_name_entry.get()
        column_type = self.column_type_combobox.get()

        if not column_name:
            messagebox.showerror("Input Error", "Column name is required.")
            return

        self.columns.append((column_name, column_type))
        messagebox.showinfo("Success", f"Column '{column_name} {column_type}' added.")
        self.column_name_entry.delete(0, tk.END)
        self.update_preview()

    def update_preview(self):
        table_name = self.table_name_entry.get()
        columns_definition = ", ".join([f"{name} {type}" for name, type in self.columns])
        preview_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition});"
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, preview_sql)

    def create_table(self):
        db_name = self.db_name_combobox.get()
        table_name = self.table_name_entry.get()

        if not db_name or not table_name or not self.columns:
            messagebox.showerror("Input Error", "Database name, table name, and at least one column are required.")
            return

        db_path = os.path.join(self.db_folder, db_name)

        if not os.path.exists(db_path):
            create_new = messagebox.askyesno("Database Not Found", f"Database '{db_name}' does not exist. Do you want to create it?")
            if not create_new:
                return

        columns_definition = ", ".join([f"{name} {type}" for name, type in self.columns])

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})")
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Table '{table_name}' created successfully in database '{db_name}'.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseEditor(root)
    root.mainloop()