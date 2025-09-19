

## Implementation Document: FastAPI Tool Server

This document provides a comprehensive overview of the tool-calling API server and its Python test client. The server is built using the FastAPI framework and exposes several tools related to GitHub repository interaction and local document searching.

-----

### 1. High-Level Architecture 

The system consists of two main components: a **FastAPI server** and a **command-line client**.

  * **Server (`server.py`)**: A robust, asynchronous server that acts as the core of the application. It receives requests for specific "tools," executes the corresponding Python function, and returns the result. It features a sophisticated, dual-mode rate-limiting system.
  * **Client (`client.py`)**: A command-line utility designed to test the server's endpoints. It simulates tool calls by constructing the appropriate JSON payload and sending it to the server, then prints the response.

-----

### 2. Server Implementation (`server.py`) ⚙️

The server is a standalone FastAPI application responsible for defining, executing, and serving the tools over a RESTful API.

#### **2.1. Core Technologies**

  * **FastAPI**: For building the high-performance, asynchronous API.
  * **Uvicorn**: As the ASGI server to run the FastAPI application.
  * **SlowAPI**: For implementing a flexible and powerful rate-limiting middleware.
  * **Pydantic**: Used by FastAPI for data validation and defining the structure of API request bodies.
  * **Python-Dotenv**: For managing configuration and secrets through a `.env` file.

#### **2.2. Configuration**

The server loads its configuration from a **`.env`** file at startup. The following variables are required:

  * `GITHUB_TOKEN`: A GitHub Personal Access Token (PAT) with permissions to read repository data.
  * `GITHUB_REPO_OWNER`: The username of the owner of the target GitHub repository.
  * `GITHUB_REPO_NAME`: The name of the target GitHub repository.

#### **2.3. Available Tools**

The server exposes the following functions as tools:

1.  **`get_repository()`**

      * **Description**: Fetches general information about the configured GitHub repository.
      * **Arguments**: None.
      * **Returns**: A JSON object with the repository's name, description, star count, fork count, and URL.

2.  **`get_file_content(path: str)`**

      * **Description**: Retrieves the decoded content of a specific file from the repository.
      * **Arguments**:
          * `path` (string): The full path to the file within the repository (e.g., `"README.md"`).
      * **Returns**: A JSON object containing the file's path and its decoded UTF-8 content.

3.  **`search_docs(keyword: str)`**

      * **Description**: Performs a case-insensitive search for a keyword within all `.md` files in the local `./docs` directory.
      * **Arguments**:
          * `keyword` (string): The search term.
      * **Returns**: A JSON object containing the keyword, the number of matches found, and a list of results with document names and content snippets.

#### **2.4. API Endpoint**

The server exposes a single primary endpoint to handle all tool calls.

  * **Endpoint**: `POST /v1/tools`
  * **Request Body**: The endpoint expects a JSON payload that conforms to the `ToolRequest` Pydantic model.
    ```json
    {
      "tool_calls": [
        {
          "id": "call_some_id",
          "function": {
            "name": "name_of_the_tool",
            "arguments": "{\"arg1\": \"value1\", \"arg2\": 123}"
          }
        }
      ]
    }
    ```
  * **Success Response**: If the tool executes successfully, the server returns a JSON object containing the output.
    ```json
    {
      "tool_outputs": [
        {
          "call_id": "call_some_id",
          "output": "{\"name\": \"owner/repo\", \"description\": \"A great repo.\" ... }"
        }
      ]
    }
    ```

#### **2.5. Rate Limiting Implementation**

The server features a dynamic, authentication-aware rate-limiting system.

  * **Unauthenticated Requests**: Limited to **1000 requests per hour**. These requests are identified by the client's **IP address**.
  * **Authenticated Requests**: Limited to **5000 requests per hour**. These requests are identified by a unique **Bearer Token** sent in the `Authorization` header.

This is achieved by using two conditional decorators on the API endpoint. The `is_authenticated` helper function checks for the presence of the `Authorization` header. Based on its return value, the `exempt_when` parameter on each decorator ensures that only one of the two limits is ever active for a single request. The `get_request_identifier` function provides the unique key (either the token or the IP) that `slowapi` uses to track the requests.

-----

### 3. Client Implementation (`client.py`) 🧑‍💻

The client is a command-line tool for interacting with and testing the server.

#### **3.1. Usage**

The client is run from the terminal and accepts arguments to specify which tests to execute.

  * **Run all tests**:
    ```bash
    python client/client.py --test-all
    ```
  * **Run only GitHub-related tests**:
    ```bash
    python client/client.py --test-github
    ```
  * **Run only the documentation search test**:
    ```bash
    python client/client.py --test-docs
    ```
    If no arguments are provided, it defaults to running all tests.

#### **3.2. Core Logic**

The `call_tool` function is the heart of the client. It takes a tool name and a dictionary of parameters, constructs the JSON payload in the exact format the server expects, and sends it as a `POST` request.

The `test_*` functions orchestrate the calls for specific tools, providing predefined parameters to simulate realistic use cases and printing the server's formatted response.

#### **3.3. Making Authenticated Requests**

To take advantage of the higher rate limit, the client can be modified to send an `Authorization` header.

**Example Modification in `client.py`**:

```python
# A user-specific token would typically be used here
USER_TOKEN = "your-secret-user-token-123" 

# Add the Authorization header
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {USER_TOKEN}"
}

# The rest of the client code remains the same...
```

-----

### 4. Setup and Execution 🚀

Follow these steps to set up and run the project.

1.  **Prerequisites**: Python 3.8+ and `pip`.

2.  **Project Structure**: Organize your files as follows:

    ```
    /project-root
    ├── .env
    ├── client/
    │   └── client.py
    ├── server/
    │   └── server2.py
    └── docs/
        └── example.md
    ```

3.  **Installation**: Install all required dependencies.

    ```bash
    pip install "fastapi[all]" requests python-dotenv slowapi
    ```

4.  **Configuration**: Create a `.env` file in the project root and populate it with your GitHub credentials.

    ```
    GITHUB_TOKEN=ghp_YourGitHubTokenHere
    GITHUB_REPO_OWNER=YourGitHubUsername
    GITHUB_REPO_NAME=YourTargetRepoName
    ```

5.  **Run the Server**: Start the FastAPI server from the project root.

    ```bash
    python server/server2.py
    ```

    The server will start on `http://127.0.0.1:8000`.

6.  **Run the Client**: In a **new terminal**, run the client to test the server.

    ```bash
    python client/client.py
    ```