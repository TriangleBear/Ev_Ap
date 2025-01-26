# Event Attendance

**Event Attendance** is an application designed for managing event attendance using RFID technology. It allows users to register members, track attendance at events, and manage event-related data efficiently.

## Features

- **Member Registration:** Register members with their RFID cards, ID, name, program, and year.
- **Event Management:** Create new events and track member attendance for each event.
- **Attendance Tracking:** Scan RFID cards to mark attendance for members at events.
- **Data Export:** Export attendance data to CSV or Excel for further analysis.

## Requirements

- Python 3.x
- SQLite (automatically handled by the application)
- CustomTkinter (for the UI)
- IceCream (for debugging)
- pandas (for exporting data)

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/event-attendance.git
    ```

2. Navigate to the project directory:
    ```bash
    cd event-attendance
    ```

3. Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the application:
    ```bash
    python main.py
    ```

## Usage

### Registering a Member

1. Open the "Register Member" window from the main menu.
2. Fill in the member's details (RFID, name, student number, program, year).
3. Click the "Submit" button to register the member.

### Creating an Event

1. Open the "Create Event" window.
2. Enter a name for the new event.
3. Click "Submit" to create the event and start tracking attendance.

### Marking Attendance

1. Select an event from the "Select a table" dropdown menu.
2. Scan the RFID card of a registered member to mark their attendance at the event.

### Exporting Data

1. After viewing the event's attendance data, click "Export" to save the data as a CSV or Excel file.

## Screenshots

![Event Attendance Screenshot](Screenshots\main.png)
![Member List Screenshot](Screenshots\memberList.png)

## Contributing

We welcome contributions! If you would like to help improve the Event Attendance app, follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes.
4. Test your changes thoroughly.
5. Submit a pull request describing your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
