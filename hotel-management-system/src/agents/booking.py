"""
Booking Agent: Handles creation, modification, and cancellation of reservations.
"""
import uuid
from datetime import datetime
from typing import Dict, Any
from src.models.state import HotelState
from src.utils.mocks import available_rooms, existing_bookings

def _simulate_payment_processing(payment_details: dict, amount: float) -> dict:
    """Helper to simulate a payment gateway."""
    print(f"  💳 Simulating payment of ${amount}...")
    if payment_details.get("status") == "valid":
        return {"status": "Success", "transaction_id": f"TXN{uuid.uuid4().hex[:10].upper()}"}
    else:
        return {"status": "Failed", "reason": "Credit card declined."}

def _handle_create_booking(state: HotelState):
    """Handles logic for new bookings. Modifies state in-place."""
    print("  -> Executing 'create' booking logic...")
    req = state['request']
    room_type = req.get("room_type")
    
    if room_type in available_rooms and available_rooms[room_type]:
        room_number = available_rooms[room_type].pop(0)
        print(f"  ✅ Room {room_number} is available. Proceeding to payment.")
        cost = (150 if room_type == "Standard" else 250 if room_type == "Deluxe" else 400) * req.get("nights", 1)
        payment_result = _simulate_payment_processing(req.get("payment_details", {}), cost)

        if payment_result["status"] == "Success":
            booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
            new_booking = {
                "booking_id": booking_id, "customer": req.get("customer"), "room_type": room_type,
                "room_number": room_number, "check_in": req.get("check_in"), "nights": req.get("nights"),
                "status": "Confirmed", "total_cost": cost, "created_at": datetime.now().isoformat(), "customer": req.get('customer')
            }
            existing_bookings[booking_id] = new_booking
            state['booking'] = new_booking
            print(f"  ✅ Payment successful. Booking {booking_id} confirmed.")
        else:
            available_rooms[room_type].append(room_number)
            state['booking'] = {"status": "Failed", "reason": payment_result["reason"], "customer": req.get('customer')}
            state['errors'].append(f"Payment failed: {payment_result['reason']}")
            print(f"  ❌ Payment failed. Room {room_number} released.")
    else:
        state['booking'] = {"status": "Failed", "reason": f"No {room_type} rooms available.", "customer": req.get('customer'), "hotel_name" : "Westin"}
        state['errors'].append(f"Room unavailable: {room_type}")
        print(f"  ❌ Booking failed: No {room_type} rooms available.")

def _handle_modify_booking(state: HotelState):
    """Handles logic for modifications. Modifies state in-place."""
    print("  -> Executing 'modify' booking logic...")
    req = state['request']
    print(f"1234 --- {req}")
    booking_id = req.get("booking_id")
    if booking_id in existing_bookings:
        booking = existing_bookings[booking_id]
        modifications = req.get("modifications", {})
        booking.update(modifications)
        if "nights" in modifications:
            booking["total_cost"] = (150 if booking["room_type"] == "Standard" else 250 if booking["room_type"] == "Deluxe" else 400) * booking["nights"]
        booking["status"] = "Modified"
        booking.update({"customer": req.get('customer')})
        state['booking'] = booking
        print(f"  ✅ Booking {booking_id} successfully modified.")
    else:
        state['booking'] = {"status": "Failed", "reason": f"Booking ID {booking_id} not found."}
        state['errors'].append(f"Modification failed: Booking not found.")
        print(f"  ❌ Modification failed: Booking {booking_id} not found.")

def _handle_cancel_booking(state: HotelState):
    """Handles logic for cancellations. Modifies state in-place."""
    print("  -> Executing 'cancel' booking logic...")
    req = state['request']
    booking_id = req.get("booking_id")
    if booking_id in existing_bookings:
        booking_to_cancel = existing_bookings.pop(booking_id)
        available_rooms[booking_to_cancel["room_type"]].append(booking_to_cancel["room_number"])
        state['booking'] = {"booking_id": booking_id, "status": "Cancelled", "refund_status": "Processing", "customer" : req.get('customer')}
        print(f"  ✅ Booking {booking_id} cancelled. Room {booking_to_cancel['room_number']} returned to pool.")
    else:
         state['booking'] = {"status": "Failed", "reason": f"Booking ID {booking_id} not found."}
         state['errors'].append(f"Cancellation failed: Booking not found.")
         print(f"  ❌ Cancellation failed: Booking {booking_id} not found.")

def booking_agent(state: HotelState) -> HotelState:
    """
    Booking Agent: Routes to different handlers based on the requested action.
    """
    request_data = state['request'] 
    print("Booking Agent: Processing reservation request...")
    
    action = request_data.get("action", "create")

    if action == "create":
        _handle_create_booking(state)
    elif action == "modify":
        _handle_modify_booking(state)
    elif action == "cancel":
        _handle_cancel_booking(state)
    else:
        state['errors'].append(f"Invalid booking action: {action}")
        state['booking'] = {"status": "Failed", "reason": "Invalid action specified."}

    if state['booking'].get("status") not in ["Failed", None]:
        print("  📡 External API Simulator: Syncing booking status with external platforms...")

    return state


