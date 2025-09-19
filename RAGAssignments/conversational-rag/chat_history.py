import os
import json
from datetime import datetime
# --- Added imports for standalone execution ---
import argparse

class ChatHistory:
    """
    Manages loading, saving, and interacting with chat conversation history.
    Ensures that the number of saved chat sessions does not exceed a defined limit.
    """
    def __init__(self, session_id: str = None, max_files: int = 10):
        """
        Initializes the ChatHistory manager.

        Args:
            session_id (str, optional): The ID of the chat session. 
                                        If None, a new session is created.
            max_files (int): The maximum number of chat history files to retain.
        """
        self.session_dir = "data/chat_sessions"
        os.makedirs(self.session_dir, exist_ok=True)
        self.max_files = max_files

        if session_id:
            self.session_id = session_id
        else:
            self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            # Clean up old session files only when creating a new session
            self._enforce_max_files()

        self.filepath = os.path.join(self.session_dir, f"{self.session_id}.json")
        self.history = self._load_history()

    def _enforce_max_files(self):
        """
        Ensures that the number of session and archive files does not exceed the maximum limit.
        Deletes the oldest files if the limit is surpassed.
        """
        files = [
            os.path.join(self.session_dir, f) for f in os.listdir(self.session_dir)
            if f.endswith('.json') or f.endswith('.txt')
        ]
        
        if len(files) >= self.max_files:
            files.sort(key=os.path.getmtime)
            num_to_delete = len(files) - self.max_files + 1
            for i in range(num_to_delete):
                try:
                    os.remove(files[i])
                    print(f"Removed old chat history file: {files[i]}")
                except OSError as e:
                    print(f"Error removing file {files[i]}: {e}")

    def _load_history(self) -> list:
        """
        (MODIFIED) Loads chat history. If a session_id was provided, it loads
        that specific file. Otherwise, it concatenates history from ALL .json files.
        """
        # This logic is adjusted to better support exporting a single file.
        # When a session ID is given, we prioritize loading just that session.
        if os.path.exists(self.filepath):
             try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        print(f"Loaded {len(data)} messages from specific session: {self.session_id}.json")
                        return data
                    return []
             except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load or parse {self.filepath}: {e}. Starting fresh.")
                return []
        
        # Original behavior: If no specific file exists or no session_id given, load all.
        combined_history = []
        try:
            json_files = sorted([f for f in os.listdir(self.session_dir) if f.endswith('.json')])
        except OSError as e:
            print(f"Error reading directory {self.session_dir}: {e}")
            return combined_history

        for filename in json_files:
            filepath = os.path.join(self.session_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        combined_history.extend(data)
            except (json.JSONDecodeError, IOError):
                pass # Silently skip malformed files in this broad load
        
        print(f"Loaded a total of {len(combined_history)} messages from {len(json_files)} session files.")
        return combined_history


    def _save_history(self):
        """Saves the current chat history to its specific session JSON file."""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.history, f, indent=4)
        except IOError as e:
            print(f"Error saving history file {self.filepath}: {e}")

    def add_message(self, role: str, content: str):
        """Adds a new message to the chat history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.history.append(message)
        self._save_history()

    def get_history(self) -> list:
        """Returns the entire chat history."""
        return self.history

    def clear_history(self):
        """Clears the current chat history."""
        self.history = []
        self._save_history()

    def get_formatted_history(self) -> str:
        """Formats the chat history into a human-readable string for download."""
        formatted_text = f"Chat Session: {self.session_id}\n"
        formatted_text += "=" * 30 + "\n\n"
        for msg in self.history:
            try:
                ts = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %I:%M:%S %p")
                role = msg.get("role", "Unknown").capitalize()
                content = msg.get("content", "")
                formatted_text += f"[{ts}] {role}: {content}\n"
            except (ValueError, KeyError) as e:
                print(f"Skipping malformed message in history: {msg}, error: {e}")
        return formatted_text

    def archive_session(self):
        """
        Saves the current chat history to a new timestamped .txt file on the server
        and then enforces the max files limit.
        """
        if not self.history:
            print("Cannot archive an empty chat session.")
            return

        formatted_text = self.get_formatted_history()
        archive_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_filename = f"chat_archive_{archive_timestamp}.txt"
        archive_filepath = os.path.join(self.session_dir, archive_filename)

        try:
            with open(archive_filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_text)
            print(f"Chat session successfully archived to: {archive_filepath}")
        except IOError as e:
            print(f"Error writing archive file: {e}")
            return
        # Enforce file limit after creating a new archive
        self._enforce_max_files()

# --- ADDED: Main execution block for CLI exporting ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export a chat session to a .txt file.")
    parser.add_argument("--export", type=str, metavar="SESSION_ID", help="The session ID to export (without the .json extension).")
    args = parser.parse_args()

    if args.export:
        session_id_to_export = args.export
        print(f"Attempting to export session: {session_id_to_export}")
        
        # Instantiate the manager for the specific session
        history_manager = ChatHistory(session_id=session_id_to_export)
        
        # Check if history was actually loaded for that session
        if not history_manager.get_history():
            print(f"Error: No history found for session '{session_id_to_export}'.")
            print(f"Please check if '{history_manager.filepath}' exists and is a valid JSON file.")
        else:
            history_manager.archive_session()
    else:
        print("Usage: python chat_history.py --export <session_id>")