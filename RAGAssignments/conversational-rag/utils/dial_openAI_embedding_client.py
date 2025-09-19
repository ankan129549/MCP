"""
EPAM DIAL API Client for OpenAI access.

This module provides a simple interface to interact with OpenAI models
through EPAM's DIAL service.
"""

import os
from langchain_openai import AzureOpenAIEmbeddings
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

class DIALEmbeddingClient:
    """
    Client for interacting with EPAM DIAL API.
    
    Example usage:
        client = DIALClient()
        response = client.get_completion([
            {"role": "user", "content": "Hello, how can I help you?"}
        ])
    """
    
    def __init__(self, model_name):
        """
        Initialize DIAL client.
        
        Args:
            api_key: DIAL API key (will use DIAL_API_KEY env var if not provided)
            model: Model name to use (default: gpt-4)
        """
        self.api_key = os.getenv("DIAL_API_KEY", "<YOUR_API_KEY_HERE>")
        self.model = model_name
        self.azure_endpoint = os.getenv("AZURE_ENDPOINT")
        self.api_version = os.getenv("API_VERSION") 
        
        # Initialize Azure OpenAI client
        print(f"Loading other model {self.model}")
        try:
            self.client = AzureOpenAIEmbeddings(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.azure_endpoint,
                azure_deployment=self.model,
               # dimensions=32, # Optional:,
               check_embedding_ctx_length=False
            )
            
            if not self.api_key or self.api_key == "<YOUR_API_KEY_HERE>":
                print("🚨 DIAL API Key not found. Please set the DIAL_API_KEY environment variable.")
                self.client = None
            else:
                print(f" DIAL Client for {self.model} model initialized successfully!")
                
        except Exception as e:
            print(f"🔥 Error initializing DIAL client: {e}")
            self.client = None
    


# Test function to verify DIAL connectivity
def test_dial_connection(self):
    """Test DIAL API connection and basic functionality."""
    print("🧪 Testing DIAL API connection...")
    if not self.client:
        print("❌ OpenAI Embedding DIAL client initialization failed")
        return False
    
    query = "Delhi is the capital of India"
    result_vector = self.client.embed_query(query)

    print(f"\n--- Embedding for: '{query}' ---")
    # The result is a list of floating-point numbers (a vector)
    print(result_vector)
    # length of the vector should match the 'dimensions'
    print(f"\nVector Dimensions: {len(result_vector)}")

if __name__ == "__main__":
    # Run connection test
    test_dial_connection(DIALEmbeddingClient("text-embedding-005"))