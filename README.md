# EVENT ATTENDANCE

This project is a system that handles member registration, event creation, and RFID attendance tracking. It uses an SQLite database to store member details and event attendance data. The project includes a GUI built with `customtkinter` for easy interaction and management.

## Requirements

- Python 3.x
- `customtkinter` for the GUI
- `sqlite3` for database interactions
- `pandas` for handling data
- `icecream` for debugging
- `CTkMessagebox` for showing message boxes

## Project Structure

1. **menu.py** - The main GUI file, handling the user interface for registering members, creating events, and managing tables.
2. **dblite.py** - Contains the database interaction logic for registering members, creating event tables, and recording attendance using SQLite.
3. **rfid_app.py** - Handles the user interface for scanning RFID tags and interacting with the database.

---

## Script Overview

### `menu.py`

This script defines the user interface and manages interactions with the database through `dblite.py`. The primary functions are:

- **list_tables**: Retrieves all tables from the SQLite database, excluding the 'Members' table.
- **confirm_button_clicked**: Handles the selection of a table and opens a new window to display its data.
- **create_table_window**: Creates a new window to display data from a selected table, with functionality for searching, refreshing, and exporting data.
- **rfid_scan_event**: Handles RFID scanning events, verifies if the RFID exists, and records attendance.
- **register_member_button_clicked**: Opens a window to register a new member by entering details like member ID, name, student number, and RFID.
- **create_event_button_clicked**: Opens a window to create a new event.
- **update_tables_dropdown**: Updates the dropdown menu with the available tables from the SQLite database.
- **center_window**: Centers the window on the screen.

### `dblite.py`

This script manages all interactions with the SQLite database, including registering members, creating event tables, and recording attendance.

- **member_register**: Registers a new member in the SQLite database.
- **member_exists**: Checks if a member exists based on the RFID number.
- **list_tables**: Retrieves a list of all tables from the database, excluding the 'Members' table.
- **create_event_table**: Creates a new table for an event, associating it with the 'Members' table.
- **fetch_table_data**: Fetches data from a specified table, either member data or event attendance data.
- **attendance_member_event**: Records attendance for a member at a specific event.

### `rfid_app.py`

This script handles the RFID scanning events and updates the GUI accordingly. It connects to the database through the functions in `dblite.py`.

- **rfid_scan_event**: Handles RFID scans and updates the attendance for the corresponding event.

---

## Usage

1. Clone the repository:

    ```bash
    git clone https://github.com/TriangleBear/ORG-RFID-EVENTS.git
    ```

2. Install the necessary dependencies:

    ```bash
    pip install customtkinter pandas icecream
    ```

3. Set up the SQLite database by creating the required tables for 'Members' and any event-specific tables you need. The database will be created automatically when running the application if it doesn't exist.

4. Run the `menu.py` file to start the application:

    ```bash
    python menu.py
    ```

5. Interact with the GUI to:

    - Register new members.
    - Create events and manage attendance.
    - View and export data from the 'Members' table and other event tables.

---

## Database Setup

The SQLite database is automatically created and initialized if it doesn't already exist. The required tables for 'Members' and event-specific tables are created dynamically.

- **Members Table**: Stores information about each member.
  
  ```sql
  CREATE TABLE IF NOT EXISTS Members (
      rfid TEXT PRIMARY KEY,
      memberid TEXT,
      name TEXT,
      student_num TEXT,
      program TEXT,
      year TEXT,
      date_registered TEXT
  );
  ```

- **Event Tables**: Created dynamically by the application for each event. Example:

  ```sql
  CREATE TABLE IF NOT EXISTS Event1 (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      rfid TEXT,
      memberid TEXT,
      student_num TEXT,
      name TEXT,
      attendance_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (rfid) REFERENCES Members(rfid)
  );
  ```

---

## Troubleshooting

- **Database connection issues**: Ensure the SQLite database file is accessible and not locked by another process.
- **RFID scan not working**: Ensure your RFID reader is properly connected and configured.
- **GUI layout issues**: If the layout is not appearing correctly, ensure your screen resolution is compatible with the window sizes defined.
