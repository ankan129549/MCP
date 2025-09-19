from dotenv import load_dotenv
load_dotenv()
import os
from openai import AzureOpenAI

# --- Your Configuration ---
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

# --- Test the connection by making an API call ---
if client:
    try:
        print("\nAttempting to test connection...")
        # This call will fail if the endpoint, key, or deployment name is wrong.
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": "hello"}]
        )
        #print("✅ Connection successful! Received a response.", response)
        # You can optionally print the response to see it
        print(response.choices[0].message.content)
        print(os.getenv("DIAL_API_KEY"))
        
    except Exception as e:
        print(f"🔥 Connection Test Failed: {e}")