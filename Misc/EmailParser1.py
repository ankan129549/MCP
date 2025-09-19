import json
import os
from openai import AzureOpenAI

# --- Configuration ---

API_KEY = os.getenv("DIAL_API_KEY") 
AZURE_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_VERSION = "2024-02-01"
DEPLOYMENT_NAME = "gpt-4"

def get_completion(messages):
    """
    Sends a request to the Azure OpenAI API and returns the response content.
    Returns None if an error occurs.
    """
    try:
        client = AzureOpenAI(
            api_key=API_KEY,
            api_version=API_VERSION,
            azure_endpoint=AZURE_ENDPOINT
        )
        print("✅ Client object created successfully.")
    except Exception as e:
        print(f"🔥 Error initializing client object: {e}")
        return None

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ An unexpected error occurred during the API call: {e}")
        return None

def extract_contact_json(text):
    """
    Extracts contact information for the primary sender from text by calling an LLM.
    Returns a JSON object or None if no clear signature is found or an error occurs.
    """
    # The prompt now clearly asks for a JSON object as the output.
    prompt = f"""
    From the text below, identify the primary sender's signature and extract their contact information into a valid JSON object.
    In an email chain, the primary sender is the author of the most recent message.
    If a field (name, email, phone) is missing, its value should be null.
    If no clear signature can be found, return an empty JSON object.

    ---
    Text: "You can contact me, John Smith, on my mobile at (123) 456-7890."
    Output:
    {{
        "name": "John Smith",
        "email": null,
        "phone": "(123) 456-7890"
    }}
    ---
    Text: "
    Hi team, FYI.

    Thanks,
    Alex Ray
    Project Manager
    alex.ray@email.io | M: 111-222-3333

    --- Forwarded message ---
    From: Sarah Peer <sarah.peer@email.io>
    Date: Fri, Aug 1, 2025 at 4:10 PM
    Subject: Project Update
    "
    Output:
    {{
        "name": "Alex Ray",
        "email": "alex.ray@email.io",
        "phone": "111-222-3333"
    }}
    ---
    Text: "Just a quick reminder about the meeting tomorrow."
    Output:
    {{}}
    ---
    Text: "{text}"
    Output:
    """
    
    messages = [{"role": "user", "content": prompt}]
    
    response_text = get_completion(messages)

    if not response_text:
        print(" Received no response from the API.")
        return None

    try:
        # Since we requested a JSON object, we can try to parse the whole response.
        parsed_json = json.loads(response_text)
        
        # If the model returns an empty object, no clear signature was found.
        if not parsed_json:
            print(" Model indicated no clear signature was found.")
            return None
            
        return parsed_json
        
    except json.JSONDecodeError as e:
        print(f"🔥 Could not parse JSON. Error: {e}")
        print(f"Raw response was: \n{response_text}")
        return None

# --- Test with a forwarded email chain ---
forwarded_email = """
Hi team,

FYI on the thread below.

Thanks,
Alex Ray
Project Manager
alex.ray@email.io | M: 111-222-3333

--- Forwarded message ---
From: Sarah Peer <sarah.peer@email.io>
Date: Fri, Aug 1, 2025 at 4:10 PM
Subject: Project Update
To: Alex Ray <alex.ray@email.io>

Hi Alex,

Here is the update you requested.

Thanks,
Sarah Peer
Senior Software Engineer
sarah.peer@email.io | M: 555-010-2233
"""

contact_info = extract_contact_json(forwarded_email)

if contact_info:
    print("\n✅ Successfully extracted primary sender's JSON:")
    print(json.dumps(contact_info, indent=2))
else:
    print("\n❌ Could not extract contact information.")