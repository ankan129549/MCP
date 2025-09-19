import openai 
from openai import AzureOpenAI
import os
import json

def get_completion(messages):
 # --- Configuration ---
    API_KEY = "dial-mqjekw9tuhcrugvqhko5yfju5t8"
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
        print("🚨 DIAL API key not found or configured correctly.")
        print("Please set the DIAL_API_KEY environment variable.")
        exit()

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": messages}
            ],
           
            temperature=0, # Lower temperature for more predictable results
        )
      
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    return "Unable to extract the response now"

def extract_contact_json(text):
    """
    Extracts contact information for the primary sender from text and returns a JSON object.
    
    This function instructs the model to identify the most likely (e.g., most recent)
    signature in a text, like an email chain. It returns a JSON object with the
    contact details or None if no clear signature is found.
    """
    prompt = f"""
     From the text below, identify the primary sender's signature and extract their contact information. 
    In an email chain, this is the most recent signature. If no clear signature can be found, return an empty JSON object.

    ---
    Text: "Please reach out to Jane Doe at jane.d@example.com."
    Output:
    ```json
    {{
        "name": "Jane Doe",
        "email": "jane.d@example.com",
        "phone": null
    }}
    ```
    ---
    Text: "You can contact me, John Smith, on my mobile at (123) 456-7890. My email is j.smith@workplace.net."
    Output:
    ```json
    {{
        "name": "John Smith",
        "email": "j.smith@workplace.net",
        "phone": "(123) 456-7890"
    }}
    ```
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

    Here is the update.
    
    Thanks,
    Sarah Peer
    Senior Software Engineer
    "
    Output:
    ```json
    {{
        "name": "Alex Ray",
        "email": "alex.ray@email.io",
        "phone": "111-222-3333"
    }}
    ```
    ---
    Text: "Just a quick reminder about the meeting tomorrow."
    Output:
    ```json
    {{}}
    ```
    ---
    Text: "{text}"
    Output:
    """
    
    messages = [{"role": "user", "content": prompt}]
    response_text = get_completion(messages)
    
    # The model sometimes adds explanations. Let's find the JSON block.
    try:
        # Find the start and end of the JSON block
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON object found in the response.")
            
        json_string = response_text[json_start:json_end]
        
        # Parse the extracted string into a Python dictionary
        return json.loads(json_string)
    
    
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"🔥 Could not parse JSON. Error: {e}")
        print(f"Raw response was: \n{response_text}")
        return None
    
# Let's test with a forwarded email chain.
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
    print("✅ Successfully extracted primary sender's JSON:")
    print(json.dumps(contact_info, indent=2))