"""
FastMCP server with outbound rate limiting to manage the GitHub API quota.

- Outbound Limit: Manages the server's API quota with GitHub, respecting the 5000/hr
  (authenticated) or 1000/hr (unauthenticated) limits.

Requires a .env file. GITHUB_TOKEN is optional.
"""

import os
import base64
import httpx
import uvicorn
import time
import json
from dotenv import load_dotenv
from fastmcp import FastMCP

# --- Configuration ---
load_dotenv()
# GITHUB_TOKEN is now optional. The server will adapt.
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME")
DOCS_DIRECTORY = "docs"
STATE_FILE = "rate_limit_state.json"

# --- Validate Configuration ---
if not all([GITHUB_REPO_OWNER, GITHUB_REPO_NAME]):
    raise ValueError("Missing GITHUB_REPO_OWNER or GITHUB_REPO_NAME in .env file.")

# --- GitHub API Constants ---
GITHUB_API_BASE_URL = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}"

# --- Custom Exception for Outbound Limit ---
class GitHubRateLimitExceeded(Exception):
    pass

# --- Outbound Rate Limit State Management ---
def load_rate_limit_state():
    """Loads the request count and timestamp from the state file."""
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"count": 0, "window_start": time.time()}

def save_rate_limit_state(state):
    """Saves the current state to the file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# --- Centralized API Request "Gatekeeper" Function ---
async def make_github_api_request(url: str) -> httpx.Response:
    """
    Makes a rate-limited, authenticated request to the GitHub API.
    This function is the single point of control for all outgoing API calls.
    """
    limit = 5000 if GITHUB_TOKEN else 1000
    state = load_rate_limit_state()
    
    # Check if the 1-hour window has passed
    if time.time() - state["window_start"] > 3600:
        print("Hourly rate limit window reset.")
        state["count"] = 0
        state["window_start"] = time.time()

    # Check if the limit has been reached
    if state["count"] >= limit:
        raise GitHubRateLimitExceeded(
            f"GitHub API rate limit ({limit}/hour) exceeded. Try again later."
        )

    # Prepare headers based on authentication status
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    # Make the actual API call
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status() # Raise an exception for 4xx/5xx responses
    
    # If successful, increment count and save state
    state["count"] += 1
    save_rate_limit_state(state)
    print(f"GitHub API call successful. Count is now {state['count']}/{limit} for this window.")
    
    return response

# --- MCP Server Instance ---
mcp = FastMCP("GitHub & Docs Server")


# --- Tool Implementations (Refactored to use the gatekeeper) ---

@mcp.tool()
async def get_repository() -> dict:
    """Retrieves repo info. Respects outbound GitHub rate limits."""
    try:
        print("Tool 'get_repository' called.")
        # Outbound limit check and API call via the gatekeeper
        response = await make_github_api_request(GITHUB_API_BASE_URL)
        repo_data = response.json()
        
        return {
            "name": repo_data.get("full_name"),
            "description": repo_data.get("description"),
            "stars": repo_data.get("stargazers_count"),
        }
    except GitHubRateLimitExceeded as e:
        return {"error": str(e)}
    except httpx.HTTPStatusError as http_err:
        return {"error": f"HTTP error: {http_err}", "status_code": http_err.response.status_code}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {type(e).__name__} - {e}"}

@mcp.tool()
async def get_file_content(path: str = 'README.md') -> dict:
    """Retrieves file content. Respects outbound GitHub rate limits."""
    try:
        print(f"Tool 'get_file_content' called with path: {path}")
        # Outbound limit check and API call via the gatekeeper
        url = f"{GITHUB_API_BASE_URL}/contents/{path}"
        response = await make_github_api_request(url)
        content_data = response.json()
        
        if content_data.get("encoding") != "base64":
            return {"error": "File content is not base64 encoded as expected."}
        decoded_content = base64.b64decode(content_data["content"]).decode("utf-8")
        return {"path": path, "content": decoded_content}
    except GitHubRateLimitExceeded as e:
        return {"error": str(e)}
    except httpx.HTTPStatusError as http_err:
        return {"error": f"HTTP error for path '{path}': {http_err}", "status_code": http_err.response.status_code}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {type(e).__name__} - {e}"}

@mcp.tool()
def search_docs(keyword: str) -> dict:
    """Searches local files. This tool is not rate-limited."""
    print(f"Tool 'search_documentation' called with keyword: {keyword}")
    matches = []
    if not os.path.isdir(DOCS_DIRECTORY):
        return {"error": f"Docs directory '{DOCS_DIRECTORY}' not found."}
    for filename in os.listdir(DOCS_DIRECTORY):
        if filename.endswith(".md"):
            filepath = os.path.join(DOCS_DIRECTORY, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    if keyword.lower() in content.lower():
                        snippet = content[:200] + "..." if len(content) > 200 else content
                        matches.append({"document": filename, "content_snippet": snippet})
            except Exception as e:
                print(f"Could not read file {filepath}: {e}")
    return {"keyword": keyword, "matches_found": len(matches), "results": matches}


# --- Server Execution ---
if __name__ == "__main__":
    print("🚀 Starting FastMCP Server with Outbound GitHub Rate Limiting...")
    auth_status = "Authenticated" if GITHUB_TOKEN else "Unauthenticated"
    outbound_limit = 5000 if GITHUB_TOKEN else 1000
    print(f"Running in {auth_status} mode.")
    print(f"Outbound GitHub API limit set to: {outbound_limit}/hour")
    
    mcp.run(transport="streamable-http")