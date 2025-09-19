#from langchain_openai import ChatOpenAI
#from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

#load_dotenv()

prompt1 = PromptTemplate(
    template='Generate a detailed report on {topic}',
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template='Generate a 5 pointer summary from the following text \n {text}',
    input_variables=['text']
)
#--Configure the Model ---
API_KEY = "" 
AZURE_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_VERSION = "2024-02-01"
DEPLOYMENT_NAME = "gpt-4o"

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

except Exception as e:
    print(f"🔥 Error during model initialization or invocation: {e}")


parser = StrOutputParser()

chain = prompt1 | model | parser | prompt2 | model | parser

result = chain.invoke({'topic': 'Unemployment in India'})

print(result)


chain.get_graph().print_ascii()
