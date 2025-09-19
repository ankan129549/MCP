from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import tiktoken
from dotenv import load_dotenv
import os
# --- Added imports for standalone execution ---
import argparse
from utils.dial_client import DIALClient

load_dotenv()

class MessageTrimming:
    """
    A class to handle smart trimming of conversation history to manage token limits.
    """
    def __init__(self, max_tokens: int = 4096, strategy: str = "smart", llm=None):
        """
        Initializes the MessageTrimming utility.

        Args:
            max_tokens (int): The maximum number of tokens allowed.
            strategy (str): The trimming strategy ("smart" or "summarization").
            llm: An initialized LangChain LLM instance, required for "summarization".
        """
        self.max_tokens = max_tokens
        self.strategy = os.getenv("TRIMMING_STRATEGY") or strategy
        self.llm = llm
        if self.strategy == "summarization" and self.llm is None:
            raise ValueError("An LLM instance must be provided for the 'summarization' strategy.")

    def trim(self, messages: List[Dict]) -> List[Dict]:
        """
        Trims the messages according to the selected strategy.
        """
        if self.strategy == "smart":
            return self._trim_by_recency(messages)
        elif self.strategy == "summarization":
            return self._trim_by_summarization(messages)
        else:
            raise ValueError(f"Unknown trimming strategy: {self.strategy}")

    def _get_token_count(self, messages: List[Dict], model_name: str = "gpt-4") -> int:
        """
        Calculates the number of tokens in a list of messages.
        """
        text = " ".join(m['content'] for m in messages)
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))


    def _trim_by_recency(self, messages: List[Dict]) -> List[Dict]:
        """
        Trims messages by keeping the most recent ones that fit within the token limit.
        """
        token_count = 0
        trimmed_messages = []
        for message in reversed(messages):
            message_tokens = self._get_token_count([message])
            if token_count + message_tokens <= self.max_tokens:
                trimmed_messages.insert(0, message)
                token_count += message_tokens
            else:
                break
        
        print(f"Original message count: {len(messages)}, Trimmed by recency: {len(trimmed_messages)}")
        return trimmed_messages

    def _summarize_messages(self, messages_to_summarize: List[Dict]) -> str:
        """Uses the provided LLM to summarize a list of messages."""
        if not self.llm:
            return "[Summarization failed: LLM not available]"

        conversation_text = "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in messages_to_summarize
        )

        prompt = ChatPromptTemplate.from_template(
            "Concisely summarize the key points of the following conversation:\n\n{conversation}"
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            summary = chain.invoke({"conversation": conversation_text})
            return summary
        except Exception as e:
            print(f"Error during summarization: {e}")
            return "[Summarization failed due to an error]"

    def _trim_by_summarization(self, messages: List[Dict], keep_recent: int = 6) -> List[Dict]:
        """
        Keeps the N most recent messages and summarizes the rest.
        """
        if self._get_token_count(messages) <= self.max_tokens:
            return messages

        if len(messages) <= keep_recent:
            return self._trim_by_recency(messages)

        messages_to_summarize = messages[:-keep_recent]
        recent_messages = messages[-keep_recent:]

        summary = self._summarize_messages(messages_to_summarize)
        
        summary_message = {"role": "system", "content": f"[Summary of earlier conversation]: {summary}"}

        trimmed_messages = [summary_message] + recent_messages
        
        if self._get_token_count(trimmed_messages) > self.max_tokens:
            print("⚠️ Summarization + recent messages still exceed token limit. Applying recency trimming.")
            return self._trim_by_recency(trimmed_messages)

        print(f"Original message count: {len(messages)}, Trimmed with summary: {len(trimmed_messages)}")
        return trimmed_messages

# --- Main execution block for CLI testing ---
def run_trimming_test():
    """
    Generates a long sample conversation and demonstrates the trimming strategies.
    """
    print("--- Running Message Trimming Test ---")

    # 1. Create a long, sample conversation history
    sample_messages = [
        {"role": "user", "content": f"This is user message number {i}. It contains some text to increase the token count significantly."}
        if i % 2 == 0 else
        {"role": "assistant", "content": f"This is assistant response number {i}. Each message adds more content to the history, making it longer and longer."}
        for i in range(20)
    ]
    
    # 2. Initialize LLM (required for summarization)
    llm = DIALClient().client

    # 3. Test setup
    max_tokens_limit = 100 # A low limit to ensure trimming occurs
    original_tokens = MessageTrimming()._get_token_count(sample_messages)
    
    print(f"\nOriginal Message Count: {len(sample_messages)}")
    print(f"Original Token Count: {original_tokens}")
    print(f"Max Token Limit Set To: {max_tokens_limit}")
    print("-" * 30)

    # 4. Test "smart" (recency) trimming
    print("\nTesting 'smart' (recency) trimming...")
    smart_trimmer = MessageTrimming(max_tokens=max_tokens_limit, strategy="smart")
    smart_trimmed = smart_trimmer.trim(sample_messages)
    print("Resulting messages:")
    for msg in smart_trimmed:
        print(f"  - {msg['role']}: {msg['content'][:40]}...")
    print(f"Final Token Count: {smart_trimmer._get_token_count(smart_trimmed)}")
    print("-" * 30)
    
    # 5. Test "summarization" trimming
    print("\nTesting 'summarization' trimming...")
    summary_trimmer = MessageTrimming(max_tokens=max_tokens_limit, strategy="summarization", llm=llm)
    summary_trimmed = summary_trimmer.trim(sample_messages)
    print("Resulting messages:")
    for msg in summary_trimmed:
        print(f"  - {msg['role']}: {msg['content'][:70]}...")
    print(f"Final Token Count: {summary_trimmer._get_token_count(summary_trimmed)}")
    print("-" * 30)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test message trimming strategies.")
    parser.add_argument("--test", action="store_true", help="Run the built-in test for trimming.")
    args = parser.parse_args()

    if args.test:
        run_trimming_test()
    else:
        print("Use the --test flag to run the trimming demonstration.")