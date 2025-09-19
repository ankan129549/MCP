from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langserve import add_routes
import uvicorn
import os
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Langchain Server",
    version="1.0",
    description="A simple API Server"
)

# Initialize models (only after FastAPI app creation)
try:
    model = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    llm = OllamaLLM(model="llama3.2:1b")
    
    # Create prompts
    prompt1 = ChatPromptTemplate.from_template("Give me an essay about {topic} in 100 words")
    prompt2 = ChatPromptTemplate.from_template("Give me a poem about {topic} for a 5 year old in 100 words")
    
    # Add routes - one at a time to isolate issues
    add_routes(app, prompt1 | model, path="/essay")
    add_routes(app, prompt2 | llm, path="/poem")
    
except Exception as e:
    print(f"Error during setup: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)