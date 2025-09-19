from langchain_openai import AzureOpenAIEmbeddings
#from dotenv import load_dotenv

#load_dotenv()

#embedding = OpenAIEmbeddings(model='text-embedding-3-large', dimensions=32)

#result = embedding.embed_query("Delhi is the capital of India")

#print(str(result))


# --- Configuration ---

API_KEY = "dial-mqjekw9tuhcrugvqhko5yfju5t8"
AZURE_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_VERSION = "2024-02-01"

# IMPORTANT: Replace this with the actual name you gave your deployment in Azure OpenAI Studio.
# The error message indicates "text-embedding-3-large" is not a recognized deployment name at your endpoint.
DEPLOYMENT_NAME = "text-embedding-3-small-1"
#DEPLOYMENT_NAME = "text-embedding-005"

try:
    # --- Initialize the LangChain embeddings model ---
    embedding_model = AzureOpenAIEmbeddings(
        azure_endpoint=AZURE_ENDPOINT,
        openai_api_version=API_VERSION,
        azure_deployment=DEPLOYMENT_NAME, # This is the crucial parameter
        openai_api_key=API_KEY,
        #dimensions=32 , # Optional: text-embedding-3-large defaults to 3072. Specify a smaller size like 1536 or 256 if needed.
        check_embedding_ctx_length=False
    )
    print("✅ AzureOpenAIEmbeddings model initialized successfully.")

    # --- Generate an embedding for a query ---
    query = "Delhi is the capital of India"
    result_vector = embedding_model.embed_query(query)

    print(f"\n--- Embedding for: '{query}' ---")
    # The result is a list of floating-point numbers (a vector)
    print(result_vector)

    # length of the vector should match the 'dimensions'
    print(f"\nVector Dimensions: {len(result_vector)}")


except Exception as e:
    print(f"🔥 Error during model initialization or invocation: {e}")