from langchain_core.prompts import PromptTemplate
#from langchain_openai import ChatOpenAI
#from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

#load_dotenv()

#model = ChatOpenAI()

# detailed way
template2 = PromptTemplate(
    template='Greet this person in 5 languages. The name of the person is {name}',
    input_variables=['name']
)

# fill the values of the placeholders
prompt = template2.invoke({'name':'John'})

#result = model.invoke(prompt)

# print(result.content)
print(prompt)

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
    result = model.invoke(prompt)

    print("\n--- Result ---")
    print(result.content)

except Exception as e:
    print(f"🔥 Error during model initialization or invocation: {e}")



