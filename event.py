# event.py
import os
import sqlite3
import customtkinter as CTk
from icecream import ic

def create_database():
    # Specify the folder where the databases are located
    folder_path = '.DBsavefile'

    # Ensure the folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Get a list of all the database files in the folder
    database_files = [file for file in os.listdir(folder_path) if file.endswith('.db')]

    if len(database_files) == 0:
        # If no database files exist, prompt the user to create a new database
        database_name_dialog = CTk.CTkInputDialog(title="Input", text="Enter the name for the new database:")
        database_name = database_name_dialog.get_input()
        if database_name:
            ic(f"Creating new database '{database_name}.db'...")
            database_path = os.path.join(folder_path, f"{database_name}.db")
            conn = sqlite3.connect(database_path)
            ic(f"New database '{database_name}.db' created successfully!")
        else:
            ic("No database name provided. Exiting...")
            return
    elif len(database_files) == 1:
        # If only one database file exists, use it
        database_path = os.path.join(folder_path, database_files[0])
        conn = sqlite3.connect(database_path)
        ic(f"Using existing database '{database_files[0]}'")
    else:
        # If multiple database files exist, prompt the user to select one
        ic("Multiple databases found. Please select one:")
        for i, database_file in enumerate(database_files):
            ic(f"{i+1}. {database_file}")
        selection_dialog = CTk.CTkInputDialog(title="Input", text="Enter the number of the database to use:")
        selection_dialog.wait_window()  # Wait for the dialog to close
        selection = selection_dialog.get_input()
        if selection.isdigit() and 0 < int(selection) <= len(database_files):
            database_path = os.path.join(folder_path, database_files[int(selection)-1])
            conn = sqlite3.connect(database_path)
            ic(f"Using selected database '{database_files[int(selection)-1]}'")
        else:
            ic("Invalid selection. Exiting...")
            return

    # Perform database operations here

    # Close the database connection
    conn.close()