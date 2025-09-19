from langchain_openai import AzureChatOpenAI
import os

# --- Configuration ---

API_KEY = "dial-mqjekw9tuhcrugvqhko5yfju5t8" 
AZURE_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_VERSION = "2024-02-01"
DEPLOYMENT_NAME = "gpt-4"

try:

    model = AzureChatOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        openai_api_version=API_VERSION,
        deployment_name=DEPLOYMENT_NAME,
        openai_api_key=API_KEY,
        temperature=0.8,
        max_tokens=100  
    )
    print("✅ AzureChatOpenAI model initialized successfully.")

    # --- Invoke the model ---
    result = model.invoke("Write a 5 line poem on cricket")

    print("\n--- Poem ---")
    print(result.content)

except Exception as e:
    print(f"🔥 Error during model initialization or invocation: {e}")