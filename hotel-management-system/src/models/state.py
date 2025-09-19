"""
Shared state definition for the hotel management workflow.
"""
from typing import Dict, Any, List, TypedDict
from src.utils.dial_client import DIALClient
# No longer importing DIALClient here as it won't be part of the state dictionary.


class HotelState(TypedDict):
    """
    Shared state object for hotel management workflow, defined as a TypedDict.

    Attributes:
        request: Initial customer request data.
        booking: Booking information and status.
        housekeeping: Room preparation status.
        customer_service: Customer interaction logs.
        errors: Any errors encountered during processing.
    """
    request: Dict[str, Any]
    booking: Dict[str, Any]
    housekeeping: Dict[str, Any]
    customer_service: Dict[str, Any]
    errors: List[str]
    dial_client : DIALClient
