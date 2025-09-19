"""
Mock data for the hotel management system.
"""

# A mutable dictionary to simulate a database of available rooms.
available_rooms = {
    "Standard": ["101", "102", "103"],
    "Deluxe": ["201", "202"],
    "Suite": [] # Let's start with Suites being booked to test failure cases
}

# A mutable dictionary to simulate a database of confirmed bookings.
# Pre-populate with a booking to test modification and cancellation.
existing_bookings = {
    "BKCDE54321": {
        "booking_id": "BKCDE54321",
        "customer": "John Smith",
        "room_type": "Suite",
        "room_number": "301",
        "check_in": "2025-09-10",
        "nights": 2,
        "status": "Confirmed",
        "total_cost": 800,
        "created_at": "2025-08-25T10:00:00Z"
    }
}


# Mock data for housekeeping and maintenance staff
housekeeping_staff = [
    {'id': 'HS-01', 'name': 'Maria Gomez', 'status': 'Available'},
    {'id': 'HS-02', 'name': 'David Chen', 'status': 'Available'},
    {'id': 'HS-03', 'name': 'Fatima Al-Jamil', 'status': 'On Break'},
]

maintenance_staff = [
    {'id': 'MT-01', 'name': 'Carlos Rivera', 'specialty': 'Plumbing', 'status': 'Available'},
    {'id': 'MT-02', 'name': 'John Smith', 'specialty': 'HVAC', 'status': 'Available'},
]

# Mock data to simulate pre-existing maintenance flags for specific rooms
room_maintenance_flags = {
    '201': 'Leaky faucet in bathroom sink.',
    '301': 'A/C unit is making a rattling noise.',
}