# AHO RFID Events

This project is a system that handles member registration, event creation, and RFID attendance tracking. It uses a MySQL database to store member details and event attendance data. The project includes a GUI built with `customtkinter` for easy interaction and management.

## Requirements

- Python 3.x
- `customtkinter` for the GUI
- `pymysql` for database interactions
- `pandas` for handling data
- `icecream` for debugging
- `CTkMessagebox` for showing message boxes
- MySQL server running with necessary privileges and configurations

## Project Structure

1. **menu.py** - The main GUI file, handling the user interface for registering members, creating events, and managing tables.
2. **dbActions.py** - Contains the database interaction logic for registering members, fetching table data, and recording attendance.
3. **dbcloud.py** - Contains database connection logic to interact with the MySQL database.

---

## Script Overview

### `menu.py`

This script defines the user interface and manages interactions with the database through `dbActions`. The primary functions are:

- **list_tables**: Retrieves all tables from the database except the 'Members' table.
- **confirm_button_clicked**: Handles the selection of a table and opens a new window to display its data.
- **create_table_window**: Creates a new window to display data from a selected table, with functionality for searching, refreshing, and exporting data.
- **rfid_scan_event**: Handles RFID scanning events, verifies if the RFID exists, and records attendance.
- **register_member_button_clicked**: Opens a window to register a new member by entering details like member ID, name, student number, and RFID.
- **create_event_button_clicked**: Opens a window to create a new event.
- **update_tables_dropdown**: Updates the dropdown menu with the available tables from the database.
- **center_window**: Centers the window on the screen.

### `dbActions.py`

This script manages all interactions with the database, including registering members, creating event tables, and recording attendance.

- **member_register**: Registers a new member in the database.
- **member_exists**: Checks if a member exists based on the RFID number.
- **list_tables**: Retrieves a list of all tables from the database except the 'Members' table.
- **create_event_table**: Creates a new table for an event, associating it with the 'Members' table.
- **fetch_table_data**: Fetches data from a specified table, either member data or event attendance data.
- **attendance_member_event**: Records attendance for a member at a specific event.

### `dbcloud.py`

This script contains the database connection logic, using MySQL's `pymysql` library to connect to the database. It retrieves credentials from the `creds.py` file.

- **get_db_connection**: Establishes a connection to the MySQL database using credentials stored in `creds.py`.

---

## Usage

1. Clone the repository:

    ```bash
    git clone https://github.com/TriangleBear/ORG-RFID-EVENTS.git
    ```

2. Install the necessary dependencies:

    ```bash
    pip install customtkinter pymysql pandas icecream
    ```

3. Set up the database by creating the required tables for 'Members' and any event-specific tables you need. Modify the `creds.py` file to include your database credentials.

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

Ensure your MySQL database is set up with the following structure:

- **Members Table**: Stores information about each member.
  
  ```sql
  CREATE TABLE Members (
      rfid VARCHAR(50) PRIMARY KEY,
      memberid VARCHAR(50),
      name VARCHAR(255),
      student_num VARCHAR(50),
      program VARCHAR(255),
      year INT,
      date_registered TIMESTAMP
  );
  ```

- **Event Tables**: Created dynamically by the application for each event. Example:

  ```sql
  CREATE TABLE Event1 (
      id INT AUTO_INCREMENT PRIMARY KEY,
      rfid VARCHAR(50),
      memberid VARCHAR(50),
      student_num VARCHAR(50),
      name VARCHAR(255),
      attendance_time TIMESTAMP,
      CONSTRAINT Event1MemberID_FK FOREIGN KEY (rfid) REFERENCES Members(rfid)
  );
  ```

---

## Troubleshooting

- **Database connection issues**: Check your database credentials in `creds.py`.
- **RFID scan not working**: Ensure your RFID reader is properly connected and configured.
- **GUI layout issues**: If the layout is not appearing correctly, ensure your screen resolution is compatible with the window sizes defined.
