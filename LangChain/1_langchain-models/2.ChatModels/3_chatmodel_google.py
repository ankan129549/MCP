from langchain_google_genai import ChatGoogleGenerativeAI
import os

#  If you're managing your API key as an environment variable (recommended)
#  You'll need to set the GOOGLE_API_KEY environment variable. 
#  For example: os.environ["GOOGLE_API_KEY"] = "your_google_ai_api_key_here"

os.environ["GOOGLE_API_BASE"] = "https://ai-proxy.lab.epam.com"

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # Specify the Gemini 1.5 Flash model
    temperature=0,                  #  Set the sampling temperature (0.0 to 1.0).
    max_tokens=1024,                #  Maximum number of tokens to generate.
    api_key="dial-mqjekw9tuhcrugvqhko5yfju5t8",                #  Optionally pass your Anthropic API key here.
    GOOGLE_API_BASE="https://ai-proxy.lab.epam.com",               #  Optional: Specify a custom base URL if using a proxy or service emulator.
    timeout=None,                 #  Optional: Timeout for requests.
    max_retries=2,                #  Optional: Max number of retries if a request fails.
        
)

result = model.invoke('What is the capital of India')
print("--Answer--")
print(result.content)

   curl -s "https://ai-proxy.lab.epam.com/openai/models" -H "Api-Key: dial-mqjekw9tuhcrugvqhko5yfju5t8"
