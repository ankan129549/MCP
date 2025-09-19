from langchain_openai import AzureOpenAIEmbeddings
#from dotenv import load_dotenv

#load_dotenv()

#embedding = OpenAIEmbeddings(model='text-embedding-3-large', dimensions=32)

documents = [
    "Delhi is the capital of India",
    "Kolkata is the capital of West Bengal",
    "Paris is the capital of France"
]

#result = embedding.embed_documents(documents)

#print(str(result))

API_KEY = "dial-mqjekw9tuhcrugvqhko5yfju5t8"
AZURE_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_VERSION = "2024-02-01"

DEPLOYMENT_NAME = "text-embedding-3-small-1"

try:
    # --- Initialize the LangChain embeddings model ---
    embedding = AzureOpenAIEmbeddings(
        azure_endpoint=AZURE_ENDPOINT,
        openai_api_version=API_VERSION,
        azure_deployment=DEPLOYMENT_NAME, 
        openai_api_key=API_KEY,
        dimensions=32 # Optional
    )
    print("✅ AzureOpenAIEmbeddings model initialized successfully.")

    # --- Generate an embedding for a document ---
    result = embedding.embed_documents(documents)

    print(f"\n--- Embedding for: '{documents}' ---")
    # The result is a list of floating-point numbers (a vector)
    print(result)

    # length of the vector should match the 'dimensions'
    print(f"\nVector Dimensions: {len(result)}")


except Exception as e:
    print(f"🔥 Error during model initialization or invocation: {e}")