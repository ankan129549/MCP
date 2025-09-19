import os
import base64
import requests
import json
from dotenv import load_dotenv

# --- Imports for FastAPI and Rate Limiting ---
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --- Load Configuration (No changes here) ---
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME")
DOCS_DIRECTORY = "docs"

if not all([GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

GITHUB_API_BASE_URL = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}"
GITHUB_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# --- Tool Implementations (No changes here) ---

def get_repository() -> dict:
    # ... function content is unchanged
    print("Tool 'get_repository' called.")
    try:
        response = requests.get(GITHUB_API_BASE_URL, headers=GITHUB_HEADERS)
        response.raise_for_status()
        repo_data = response.json()
        return {
            "name": repo_data.get("full_name"), "description": repo_data.get("description"),
            "stars": repo_data.get("stargazers_count"), "forks": repo_data.get("forks_count"),
            "url": repo_data.get("html_url"),
        }
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}", "status_code": http_err.response.status_code}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def get_file_content(path: str) -> dict:
    
    print(f"Tool 'get_file_content' called with path: {path}")
    url = f"{GITHUB_API_BASE_URL}/contents/{path}"
    try:
        response = requests.get(url, headers=GITHUB_HEADERS)
        response.raise_for_status()
        content_data = response.json()
        if content_data.get("encoding") != "base64":
            return {"error": "File content is not base64 encoded."}
        decoded_content = base64.b64decode(content_data["content"]).decode("utf-8")
        return {"path": path, "content": decoded_content}
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred for path '{path}': {http_err}", "status_code": http_err.response.status_code}
    except Exception as e:
        return {"error": f"An unexpected error occurred for path '{path}': {e}"}

def search_docs(keyword: str) -> dict:
   
    print(f"Tool 'search_docs' called with keyword: {keyword}")
    matches = []
    if not os.path.exists(DOCS_DIRECTORY):
        return {"error": f"Docs directory '{DOCS_DIRECTORY}' not found."}
    for filename in os.listdir(DOCS_DIRECTORY):
        if filename.endswith(".md"):
            filepath = os.path.join(DOCS_DIRECTORY, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                   # print(f"in search_docs, content is -->>>>> {content}")
                    if keyword.lower() in content.lower():
                        matches.append({"document": filename, "content_snippet": content[:200] + "..."})
            except Exception as e:
                print(f"Could not read file {filepath}: {e}")
    return {"keyword": keyword, "matches_found": len(matches), "results": matches}

# --- Map Tool Names to Functions  ---
AVAILABLE_TOOLS = {
    "get_repository": get_repository,
    "get_file_content": get_file_content,
    "search_docs": search_docs,
}

# --- FastAPI Server & Rate Limiting Setup ---

# This function identifies the requester by token or IP. 
def get_request_identifier(request: Request) -> str:
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return get_remote_address(request)


def is_authenticated(request: Request) -> bool:
    return "authorization" in request.headers and request.headers["authorization"].startswith("Bearer ")

# Create the limiter instance using our identifier function.
limiter = Limiter(key_func=get_request_identifier)

# Create a FastAPI app instance and apply the limiter.
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# --- Pydantic Models for Request Body  ---
class FunctionCall(BaseModel):
    name: str
    arguments: str

class ToolCall(BaseModel):
    id: str
    function: FunctionCall

class ToolRequest(BaseModel):
    tool_calls: List[ToolCall]


# --- API Endpoint with Correct Rate Limiting ---

# The unauthenticated limit: it is skipped if the user IS authenticated.
@limiter.limit("1000/hour", exempt_when=is_authenticated)
# The authenticated limit: it is skipped if the user IS NOT authenticated.
@limiter.limit("5000/hour", exempt_when=lambda request: not is_authenticated(request))
@app.post("/v1/tools")
async def handle_tool_call(request_body: ToolRequest, request: Request):
    tool_call = request_body.tool_calls[0]
    tool_name = tool_call.function.name
    
    if tool_name in AVAILABLE_TOOLS:
        function_to_call = AVAILABLE_TOOLS[tool_name]
        try:
            args = json.loads(tool_call.function.arguments)
            result = function_to_call(**args)
            return {
                "tool_outputs": [{ "call_id": tool_call.id, "output": json.dumps(result) }]
            }
        except Exception as e:
            return {"error": f"Error executing tool '{tool_name}': {e}"}
    else:
        return {"error": f"Tool '{tool_name}' not found."}


# --- Main Execution Block (No changes here) ---
if __name__ == "__main__":
    print("Starting FastAPI Tool Server with Rate Limiting...")
    print(f"Configured for repository: {GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}")
    print("Available tools:", ", ".join(AVAILABLE_TOOLS.keys()))
    uvicorn.run(app, host="127.0.0.1", port=8000)
