"""
🏨 Multi-Agent Hotel Management System - Main Application

This script orchestrates the hotel management workflow using LangGraph.
It is the main entry point for running the system.
"""
# --- PATH CORRECTION ---
# This block allows the script to be run directly and still find the `src` module.
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --- END PATH CORRECTION ---

import argparse
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the state and agent functions from their respective modules
from src.models.state import HotelState
from src.agents.booking import booking_agent
from src.agents.housekeeping import housekeeping_agent
from src.agents.customer_service import customer_service_agent


def should_continue_to_housekeeping(state: HotelState) -> str:
    """Route decision: proceed to housekeeping only if a booking was newly confirmed."""
    print("---")
    print("🚦 Routing Decision...")
    # Only newly created and confirmed bookings should trigger housekeeping
    if state['booking'].get("status") == "Confirmed" and state['request'].get("action") == "create":
        print("-> New booking confirmed. Proceeding to Housekeeping.")
        return "housekeeping"
    else:
        #print(f"-> Action is '{state['booking'].get('status')}'. Proceeding to Customer Service.")
        return "customer_service"

def should_continue_to_booking(state: HotelState) -> str:

    print(f"state['customer_service'] {state['customer_service']}")
    if state['customer_service'] and state['customer_service'].get('customer_query') :
        return "customer_service"
    else :
        return "booking"

def build_graph() -> StateGraph:
    """
    Constructs and compiles the LangGraph workflow for hotel management.
    """
    workflow = StateGraph(HotelState)
    workflow.add_node("booking", booking_agent)
    workflow.add_node("housekeeping", housekeeping_agent)
    workflow.add_node("customer_service", customer_service_agent)
    workflow.add_conditional_edges(
        START,
        should_continue_to_booking,
        {
            "booking": "booking",
            "customer_service": "customer_service"
        }
    )

    # 2. Second conditional branch: from the 'booking' node
    # This decides where to go *after* the booking agent has run.
    workflow.add_conditional_edges(
        "booking", # The starting point for this decision is the booking node
        should_continue_to_housekeeping,
        {
            "housekeeping": "housekeeping",
            "customer_service": "customer_service"
        }
    )

    # 3. Define the remaining standard edges
    workflow.add_edge("housekeeping", "customer_service")
    workflow.add_edge("customer_service", END)

    return workflow.compile()


def main():
    """Main execution function with argument parsing."""
    parser = argparse.ArgumentParser(description="Hotel Management System Demo")
    parser.add_argument("--action", choices=["create", "modify", "cancel"], default="create", help="Booking action to perform.")
    parser.add_argument("--booking_id", default="BKCDE54321", help="Booking ID for modify/cancel actions.")
    parser.add_argument("--customer", default="Alice Johnson", help="Customer name for new bookings.")
    parser.add_argument("--room-type", default="Deluxe", help="Room type for new bookings.")
    parser.add_argument("--nights", type=int, default=3, help="Number of nights for new or modified bookings.")
    parser.add_argument("--query", type=str, default="", help="A specific question for the customer service agent.")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    parser.add_argument("--assign-staff", action="store_true", help="Enable staff assignment logic in housekeeping.")
    parser.add_argument("--optimize-schedule", action="store_true", help="Enable cleaning schedule optimization.")
    parser.add_argument("--with-checklist", action="store_true", help="Add a room inspection checklist.")
    parser.add_argument("--handle-maintenance", action="store_true", help="Enable maintenance request handling.")
  
    args = parser.parse_args()

    print("🏨 Hotel Management System - Multi-Agent Demo")
    print("=" * 50)
    from src.utils.logger import setup_logger
    logger = setup_logger()
    logger.info("🏨 Hotel Management System - Multi-Agent Demo")
    logger.info("=" * 50)

    # Dynamic request data based on action
    #request_data = {
     #   "action": args.action,
    #    "customer_query": args.query
    #}
    request_data = {}
    from src.utils.dial_client import DIALClient
    initial_state = {
        "booking": {},
        "housekeeping": {},
        "customer_service": {},
        "errors": [],
        "dial_client": DIALClient()
    }
   # 2. Prioritize the customer query if it exists
    if args.query:
        print(f"▶️  Starting workflow for query: '{args.query}'")
        logger.info(f"▶️  Starting workflow for query: '{args.query}'")
        # Populate the customer_service part of the state
        initial_state["customer_service"] = {
            "customer_query": args.query,
            "customer": args.customer
        }
        # The 'request' can be empty as the query is the main input
        initial_state["request"] = {}

    # 3. Handle booking actions if no query is present
    else:
        print(f"▶️  Starting workflow for action: '{args.action}'")
        request_data = {"action": args.action }
        if args.action == "create":
            request_data.update({
                "customer": args.customer, "room_type": args.room_type, "nights": args.nights,
                "check_in": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
                "payment_details": {"card_type": "Visa", "status": "valid"}
            })
        elif args.action == "modify":
            request_data.update({"booking_id": args.booking_id, "modifications": {"nights": args.nights}, "customer": args.customer})
        elif args.action == "cancel":
            request_data.update({"booking_id": args.booking_id, "customer": args.customer})

        request_data['housekeeping_options'] = {
        "assign_staff": args.assign_staff,
        "optimize_schedule": args.optimize_schedule,
        "with_checklist": args.with_checklist,
        "handle_maintenance": args.handle_maintenance
        }

        initial_state["request"] = request_data
    
    hotel_graph = build_graph()

    try:
       
        final_state = hotel_graph.invoke(initial_state)

        print("\n" + "=" * 50, "\n📊 WORKFLOW COMPLETE\n" + "=" * 50)
        logger.info("\n" + "=" * 50 + "\n📊 WORKFLOW COMPLETE\n" + "=" * 50)
        logger.info("\n🗣️  FINAL CUSTOMER RESPONSE:")
        print("\n🗣️  FINAL CUSTOMER RESPONSE:")
        # We now access the final state using dictionary keys.
        print("-" * 30, f"\n{final_state['customer_service'].get('response_to_customer', 'No response generated.')}\n" + "-" * 30)
        
        if final_state.get('errors'): 
            print(f"\n⚠️  Errors encountered: {final_state['errors']}")
        
        if args.debug:
            import json
            print("\n🔍 Full State Debug:", json.dumps(final_state, indent=2))
            
    except Exception as e:
        print(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

