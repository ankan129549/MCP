from langchain_openai import AzureChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

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
        temperature=0,
        max_tokens=1024  # Note: The parameter is 'max_tokens'
    )
    print("✅ AzureChatOpenAI model initialized successfully.")

    memory = ConversationBufferMemory()
    conversation = ConversationChain(llm=model, memory=memory, verbose=True)
    conversation.predict(input = "Hola !! Can I call you Alexa?")
    conversation.predict(input = "what is 1+1. Please give me an answer")
    conversation.predict(input = "what is my name?")
    print(memory.load_memory_variables({}))
except Exception as e:
    print(f"🔥 Error during model initialization or invocation: {e}")