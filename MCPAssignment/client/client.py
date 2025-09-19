import argparse
import requests
import json

# --- Configuration ---
SERVER_URL = "http://127.0.0.1:8000/v1/tools"
HEADERS = {"Content-Type": "application/json"}

# --- Helper Functions ---

def print_response(title, response):
    """Helper to print formatted JSON responses."""
    print(f"--- {title} ---")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: Received status code {response.status_code}")
        print(response.text)
    print("-" * (len(title) + 8) + "\n")

def call_tool(tool_name, params=None):
    """Constructs the request and calls the MCP server."""
    payload = {
        "tool_calls": [
            {
                "id": f"call_{tool_name}",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(params) if params else "{}"
                }
            }
        ]
    }
    try:
        #response = requests.post(SERVER_URL, headers=HEADERS, json=payload)
        response = requests.post(SERVER_URL, headers=HEADERS, json=payload)
        #print(f"response ------------- {response}")
        return response
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: Could not connect to the server at {SERVER_URL}.")
        print("Please ensure the 'server.py' is running.")
        return None


# --- Test Functions ---

def test_github_tools():
    """Tests the get_repository and get_file_content tools."""
    print(" Testing GitHub Tools...")
    
    # Test 1: Get repository info
    repo_response = call_tool("get_repository")
    if repo_response:
        print_response("Response for 'get_repository'", repo_response)

    # Test 2: Get file content (e.g., README.md)
    file_params = {"path": "README.md"} # Assuming a README.md exists
    file_response = call_tool("get_file_content", file_params)
    if file_response:
        print_response("Response for 'get_file_content'", file_response)

def test_docs_tool():
    """Tests the search_docs tool."""
    print("📂 Testing Documentation Search Tool...")
    
    # Test 1: Search for a common keyword like 'API'
    search_params = {"keyword": "API"}
    docs_response = call_tool("search_docs", search_params)
    if docs_response:
        print_response("Response for 'search_docs' with keyword 'API'", docs_response)


# --- Main Execution ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test client for the MCP Code Review Server.")
    parser.add_argument("--test-all", action="store_true", help="Run all available tests.")
    parser.add_argument("--test-github", action="store_true", help="Run only the GitHub integration tests.")
    parser.add_argument("--test-docs", action="store_true", help="Run only the documentation search test.")
    args = parser.parse_args()

    # Default to --test-all if no arguments are provided
    if not (args.test_all or args.test_github or args.test_docs):
        args.test_all = True

    if args.test_all or args.test_github:
        test_github_tools()

    if args.test_all or args.test_docs:
        test_docs_tool()

    print("✅ Client tests finished.")
