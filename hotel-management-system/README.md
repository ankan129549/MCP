🏨 Multi-Agent Hotel Management SystemLast 
Updated: August 31, 2025
Author: Ankan
Location: Hyderabad, Telangana, India
1. Project Overview 
This project is a sophisticated multi-agent system designed to automate hotel management workflows using Python, LangGraph, and the EPAM DIAL AI service. The system simulates real-world hotel operations by orchestrating three distinct agents—Booking, Housekeeping, and Customer Service—to handle guest requests dynamically.The application is built with a modular and scalable architecture, allowing for easy extension and maintenance. It demonstrates advanced concepts such as conditional agent routing, shared state management, and AI-powered customer interaction through a Retrieval-Augmented Generation (RAG) pipeline.
2. System Architecture & Workflow
The entire system is orchestrated by LangGraph, which manages the flow of data and control between agents based on a shared HotelState object. This state acts as the central nervous system, ensuring that each agent has the context it needs to perform its tasks.The standard workflow is as follows:
[START]
   |
   V
[Booking Agent] ------(Booking Failed)------> [Customer Service Agent]
   |
(Booking Succeeded)
   |
   V
[Housekeeping Agent]
   |
   V
[Customer Service Agent]
   |
   V
[END]
Shared State (HotelState): A central Python class that holds all data related to a single request, including booking details, housekeeping status, customer service logs, and any errors.LangGraph Orchestrator: The main graph defined in src/agents.py controls the execution flow. It uses conditional edges to decide the next step based on the outcome of the booking_agent.
3. Agent Capabilities
Each agent is a specialized Python function responsible for a specific domain within the hotel's operations.🏨 Booking Agent (src/agents/booking.py)This agent is a comprehensive reservation management tool.Multi-Action Handling: Manages three distinct actions: create, modify, and cancel.Availability Validation: Checks a mock database (available_rooms in mocks.py) to ensure a room is available before confirming a new booking.Payment Simulation: Includes a _simulate_payment_processing function to approve or decline transactions, adding a layer of realism to the booking process.Booking Database: Interacts with a mock existing_bookings dictionary to manage the lifecycle of a reservation, from creation to cancellation.API Integration Simulation: Prints a log message to simulate syncing the booking status with external platforms like Booking.com or Expedia.🧹 Housekeeping Agent (src/agents/housekeeping.py)This agent activates upon a successful new booking to manage room turnover with advanced logic.Intelligent Staff Assignment: Assigns available cleaners from a mock staff pool (housekeeping_staff) and updates their status to "Assigned".Optimized Cleaning Schedules: Queues cleaning for reservations far in the future and schedules immediate cleaning for imminent arrivals.Dynamic Inspection Checklists: Generates a standard checklist for every work order to ensure quality control.Proactive Maintenance Handling: Automatically checks for pre-existing maintenance flags for a room and logs a work order with an assigned technician if an issue is found.🎧 Customer Service Agent (src/agents/customer_service.py)This is the most advanced agent, leveraging the EPAM DIAL service to handle all guest communication.Sentiment Analysis: Analyzes the sentiment of incoming customer queries to classify them as POSITIVE, NEGATIVE, or NEUTRAL.Complaint Resolution Workflow: If a negative sentiment is detected, it triggers a specialized workflow to provide an empathetic apology and offer a concrete resolution (e.g., a discount or an offer to speak with a manager).RAG for FAQ Handling: For standard queries, it uses a Retrieval-Augmented Generation (RAG) pipeline. It loads the faq.pdf into a FAISS vector store to find the most relevant information and generate an accurate, context-aware answer.Proactive Service Recommendations: In all non-complaint interactions, the agent is prompted to suggest relevant upsells, such as a spa package or airport transfer, to enhance the guest experience.External API Simulation: Simulates dispatching the final generated response to the customer via email or a messaging app.
4. Project Structure
The project is organized into a modular structure for clarity and scalability.hotel-management-system/
├── README.md                 # This documentation file
├── requirements.txt          # All Python dependencies
├── .env.example              # Template for environment variables
├── faq.pdf                   # Knowledge base for the Customer Service Agent
└── src/
    ├── __init__.py
    ├── agents.py             # Main application entrypoint and LangGraph orchestrator
    ├── models/
    │   ├── __init__.py
    │   └── state.py          # Definition of the shared HotelState object
    ├── agents/
    │   ├── __init__.py
    │   ├── booking.py        # Logic for the Booking Agent
    │   ├── housekeeping.py   # Logic for the Housekeeping Agent
    │   └── customer_service.py # Logic for the Customer Service Agent
    └── utils/
        ├── __init__.py
        ├── dial_client.py    # Client for connecting to the EPAM DIAL API
        └── mocks.py          # Mock data for rooms, staff, and bookings

5. Setup & InstallationFollow these steps to get the application running.
Step 1: 
Clone the project files & Create Environment
# Navigate to your development directory
cd path/to/your/projects

# Navigate to the project folder where the files from this project were copied
cd hotel-management-system

# Create a Python virtual environment
python3 -m venv venv
source venv/bin/activate  
# On Windows: venv\Scripts\activate
Step 2: Install Dependencies 
Install all required Python packages from the requirements.txt file.pip install -r requirements.txt
Step 3: Configure Environment Variables
Create a .env file in the project root by copying the example file.cp .env.example .env
Now, open the .env file and add your EPAM DIAL API key:DIAL_API_KEY=your_dial_api_key_here

6. Usage & Commands
The main application is run from src/agents.py and supports various command-line arguments to test different scenarios.Creating a BookingThis is the default action. The following command attempts to book a Deluxe room for Alice Johnson.
python  src/agents.py --action create --customer "Alice Johnson" --room-type "Deluxe" --nights 2
To test a booking failure (e.g., no suites available), run:
python  src/agents.py --action create --room-type "Suite"
Modifying a Booking
This command modifies the pre-existing booking BKCDE54321 to be 5 nights instead of 2.
python  src/agents.py --action modify --booking_id "BKCDE54321" --nights 5
Cancelling a Booking
This command cancels the pre-existing booking, returning its room to the available pool.
python  src/agents.py --action cancel --booking_id "BKCDE54321"
Answering a Standard Query (RAG) This command triggers the RAG pipeline to answer a question about hotel policy.python  src/agents.py --query "Are pets allowed in the hotels?"
Handling a Complaint
This command sends a negative message to trigger the complaint resolution workflow.
python  src/agents.py --query "My previous stay was terrible, the room was not clean at all."
This commands triggers all the flows of housekeeping
python src/agents.py --action create --room-type Deluxe --assign-staff --optimize-schedule --with-checklist --handle-maintenance
Debug Mode
Add the --debug flag to any command to print the complete final HotelState object for detailed inspection.
python  src/agents.py --action create --debug
