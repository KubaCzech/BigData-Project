# BigData-Project
## **Restaurant Reservation System**

This is a simple command-line based restaurant reservation system that allows managing tables, customers, and reservations in a scalable and interactive way. The system is designed to simulate the backend logic of a restaurant’s reservation workflow, including support for multiple tables and customer management.

### Features

* View all reservations
* Filter reservations by date or customer
* View individual reservation details
* Create new reservations (manual or randomly generated)
* Update existing reservations
* Delete reservations
* List all clients and tables

### How it Works

The ReservationSystem class (defined in project.py) manages the internal state of the system, including customers, reservations, and tables. The main.py script offers a text-based menu interface for interacting with the system.

When making a reservation, the system:

1. Assigns one or more available tables to fit the party size
2. Ensures no double-booking of tables
3. Generates unique customer and reservation IDs

### Project Structure

project/
│
├── project.py         # Core logic of the reservation system
├── main.py            # CLI interface to interact with the system
├── README.md          # You're reading this file!
└── (other modules)    # Optional: persistence, stress tests, etc.

### How to Run it

1. Clone the Repository

git clone https://github.com/KubaCzech/BigData-Project.git

cd BigData-Project

2. Install Requirements

3. Run the System
python main.py
You will be presented with a menu:

Follow the prompts to interact with the system.

### Example Use Case

You run main.py
Choose option 7 to make a reservation
Enter customer ID, start time, end time, number of guests
System finds appropriate table(s) and books the reservation

### License
This project is open source and free to use under the MIT License.