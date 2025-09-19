import asyncio
import argparse
import json
from fastmcp import Client

# Define the URL of your FastMCP server
SERVER_URL = "http://127.0.0.1:8000/mcp"

def print_response(title: str, response): # The type hint has been removed here
    """
    Helper function to format and print JSON responses from the server.
    """
    print(f"--- {title} ---")
    # A successful response object might not have a status_code,
    # so we check for the existence of the attribute.
    if getattr(response, 'status_code', 200) == 200:
        print(json.dumps(response.data, indent=2))
    else:
        print(f"Error: Received status code {response.status_code}")
        print(response.text)
    print("-" * (len(title) + 8) + "\n")

async def test_github_tools(client: Client):
    """
    Runs tests for tools related to GitHub integration.
    """
    print("\n>>> Running GitHub Integration Tests...")

    # Test 1: Get repository information
    repo_response = await client.call_tool("get_repository")
    if repo_response:
        print_response("Response for 'get_repository'", repo_response)

    # Test 2: Get the content of a specific file (e.g., README.md)
    file_params = {"path": "README.md"}
    file_response = await client.call_tool("get_file_content", file_params)
    if file_response:
        print_response("Response for 'get_file_content'", file_response)

async def test_docs_tool(client: Client):
    """
    Runs tests for tools related to documentation searching.
    """
    print("\n>>> Running Documentation Search Tests...")
    params = {"keyword": "API"}
    docs_response = await client.call_tool("search_docs", params)
    if docs_response:
        print_response("Response for 'search_docs'", docs_response)


async def main():
    """
    Main function to connect to the server and run specified tests.
    """
    parser = argparse.ArgumentParser(description="Test client for the FastMCP server.")
    parser.add_argument("--test-all", action="store_true", help="Run all available tests.")
    parser.add_argument("--test-github", action="store_true", help="Run only the GitHub integration tests.")
    parser.add_argument("--test-docs", action="store_true", help="Run only the documentation search test.")
    args = parser.parse_args()

    # Default to --test-all if no specific test is requested
    if not (args.test_github or args.test_docs):
        args.test_all = True

    async with Client(SERVER_URL) as client:
        print(f"Client connected to {SERVER_URL}: {client.is_connected()}")

        # List all available tools on the server
        tools = await client.list_tools()
        if tools:
            print("\n================== Available Tools ==================\n")
            print("\n".join([tool.name for tool in tools]))
            print("\n=====================================================\n")

        # Execute tests based on command-line arguments
        if args.test_all or args.test_github:
            await test_github_tools(client)

        if args.test_all or args.test_docs:
            await test_docs_tool(client)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nAn error occurred: {e}")