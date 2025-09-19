"""
Housekeeping Agent: Manages room preparation and maintenance with enhanced logic.
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from src.models.state import HotelState
from src.utils.mocks import (
    housekeeping_staff,
    room_maintenance_flags,
    maintenance_staff
)

def _assign_staff(staff_pool: list) -> dict:
    """Helper function for staff assignment logic."""
    print("Helper function for staff assignment logic")
    for staff in staff_pool:
        if staff['status'] == 'Available':
            staff['status'] = 'Assigned'  # Simulate making the staff member busy
            return {'id': staff['id'], 'name': staff['name']}
    return {'id': 'N/A', 'name': 'No staff available'}

def _optimize_schedule(check_in_date: datetime) -> tuple[str, str]:
    """Helper function for cleaning schedule optimization."""
    print("Helper function for cleaning schedule optimization.")
    days_until_check_in = (check_in_date - datetime.now()).days
    if days_until_check_in > 7:
        return "Queued", f"Cleaning scheduled to occur closer to check-in date (in {days_until_check_in - 5} days)."
    else:
        return "Scheduled for Cleaning", "Immediate cleaning scheduled."

def _generate_inspection_checklist() -> dict:
    """Helper function to add a room inspection checklist."""
    print("Helper function to add a room inspection checklist.")
    return {
        "Bathroom Cleaned": "Pending",
        "Bed Linens Changed": "Pending",
        "Mini-bar Restocked": "Pending",
        "Surfaces Dusted": "Pending",
        "Vacuuming Complete": "Pending",
    }

def _handle_maintenance_request(room_number: str) -> dict | None:
    """Helper function to add maintenance request handling."""
    print("Helper function to add maintenance request handling.")
    issue = room_maintenance_flags.get(room_number)
    if issue:
        assigned_technician = _assign_staff(maintenance_staff)
        return {
            "issue_reported": issue,
            "status": "Logged, Technician Assigned",
            "technician": assigned_technician
        }
    return None

def housekeeping_agent(state: HotelState) -> HotelState:
    """
    Prepares the room for the guest with enhanced logic, including checklists,
    optimized scheduling, staff assignment, and maintenance handling.
    """
    print("---")
    print("🧹 Housekeeping Agent: Managing room preparation...")

    try:
        booking_info = state['booking']
        print(f"booking_info.  --------{booking_info}")
        # --- NEW: Get options from the request state, with a default of False ---
        options = state.get('request', {}).get('housekeeping_options', {})
        
        print(f"options ..... {options}")

        if booking_info.get("status") != "Confirmed":
            state['errors'].append("Housekeeping called for a non-confirmed booking.")
            print("⚠️ Housekeeping agent skipped: Booking not confirmed.")
            return state

        room_number = booking_info.get("room_number")
        check_in_date = datetime.strptime(booking_info.get("check_in"), "%Y-%m-%d")
        
        # Initialize default values
        assigned_cleaner = {'id': 'N/A', 'name': 'Not Assigned'}
        schedule_status, schedule_notes = "Scheduled for Cleaning", "Standard cleaning scheduled."
        checklist = None
        maintenance_request = None

        
        if options.get("assign_staff"):
            assigned_cleaner = _assign_staff(housekeeping_staff)
            print(f"- Staff Assignment Enabled: {assigned_cleaner['name']} assigned to room {room_number}.")
        
        if options.get("optimize_schedule"):
            schedule_status, schedule_notes = _optimize_schedule(check_in_date)
            print(f"- Schedule Optimization Enabled: Status set to '{schedule_status}'.")
            
        if options.get("with_checklist"):
            checklist = _generate_inspection_checklist()
            print("- Inspection Checklist Enabled: Standard checklist generated.")

        if options.get("handle_maintenance"):
            maintenance_request = _handle_maintenance_request(str(room_number))
            if maintenance_request:
                print(f"- Maintenance Handling Enabled: Issue found for room {room_number}. Request logged.")
            else:
                print("- Maintenance Handling Enabled: No pre-existing issues found for this room.")
        # --- END NEW ---

        # Update the state with all the new, detailed information
        state['housekeeping'] = {
            "room_number": room_number,
            "status": schedule_status,
            "notes": schedule_notes,
            "ready_by": (check_in_date - timedelta(hours=3)).isoformat(),
            "assigned_staff": assigned_cleaner,
            "checklist": checklist,
            "maintenance_request": maintenance_request
        }

    except Exception as e:
        error_message = f"Housekeeping agent encountered an error: {str(e)}"
        state['errors'].append(error_message)
        print(f"❌ {error_message}")
   
    return state