import os
import json
from openai import AzureOpenAI

# --- Configuration ---
API_KEY = "dial-mqjekw9tuhcrugvqhko5yfju5t8" # Replace with your actual key or use os.getenv
AZURE_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_VERSION = "2024-02-01"
DEPLOYMENT_NAME = "gpt-4" 
    # --- Initialize the client ---
client = None # Initialize client to None
try:
    client = AzureOpenAI(
      api_key=API_KEY,
      api_version=API_VERSION,
      azure_endpoint=AZURE_ENDPOINT
    )
    print("✅ Client object created successfully.")
except Exception as e:
    print(f"🔥 Error initializing client object: {e}")
except Exception as e:
    print("🚨 OpenAI API key not found or configured correctly.")
    print("Please set the OPENAI_API_KEY environment variable.")
    exit()

# --- Core Function ---

def classify_and_prioritize(ticket_text: str) -> dict:
    """
    Classifies a support ticket and assigns a priority using an OpenAI model.

    This function uses a system prompt with few-shot examples to guide the model
    into providing a structured JSON output. It leverages OpenAI's JSON mode
    for reliable output.

    Args:
        ticket_text: The raw text from the user's support ticket.

    Returns:
        A dictionary containing the 'category' and 'priority',
        e.g., {"category": "Bug", "priority": "High"}.
        Returns an error dictionary if parsing fails.
    """
    # The system prompt sets the context and provides examples for the model.
    system_prompt = """
    You are an expert ticket classification system.
    Analyze the user's support ticket and classify it into one of five categories
    (Bug, Feature Request, Question, Praise, Complaint) and assign a priority
    (Low, Medium, High).

    You must return ONLY a valid JSON object with two keys: "category" and "priority".

    Here are some examples:
    - Ticket: "I can't log in! The app crashes every time I enter my password."
    - Output: {"category": "Bug", "priority": "High"}

    - Ticket: "It would be great if you could add a dark mode."
    - Output: {"category": "Feature Request", "priority": "Medium"}

    - Ticket: "How do I change my profile picture?"
    - Output: {"category": "Question", "priority": "Low"}
    """

    try:
        response = client.chat.completions.create(
            # Using a fast and capable model like gpt-4o-mini is cost-effective
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ticket_text}
            ],
            # Use JSON mode for guaranteed JSON output
            response_format={"type": "json_object"},
            temperature=0.2, # Lower temperature for more predictable results
        )
        # The response content is a JSON string, so we parse it
        return json.loads(response.choices[0].message.content)

    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON from model: {e}")
        print(f"Raw model response was: {response.choices[0].message.content}")
        return {"category": "Error", "priority": "Unknown"}
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return {"category": "Error", "priority": "Unknown"}

# --- Demonstration ---
if __name__ == "__main__":
    # Test cases to demonstrate the function's capabilities
    ticket1 = "The payment gateway is failing with a '500 Internal Server Error'. We can't process any customer orders! This is a catastrophe for our sales."
    ticket2 = "There's a small typo on the contact page. It says 'emial' instead of 'email'."
    ticket3 = "I'd love to see a feature that allows me to schedule reports to be sent to my email weekly."
    ticket4 = "I am extremely disappointed with the recent price increase. There was no warning and the service hasn't improved."

    print(f"Ticket: \"{ticket1}\"")
    print(f"Result: {classify_and_prioritize(ticket1)}\n") # Expected: Bug, High

    print(f"Ticket: \"{ticket2}\"")
    print(f"Result: {classify_and_prioritize(ticket2)}\n") # Expected: Bug, Low

    print(f"Ticket: \"{ticket3}\"")
    print(f"Result: {classify_and_prioritize(ticket3)}\n") # Expected: Feature Request, Medium

    print(f"Ticket: \"{ticket4}\"")
    print(f"Result: {classify_and_prioritize(ticket4)}\n") # Expected: Complaint, High