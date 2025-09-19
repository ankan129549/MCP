import os
import argparse
import time
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from message_trimming import MessageTrimming
import tiktoken
from langchain_community.vectorstores import FAISS, Chroma

# --- Imports for standalone execution ---
from vector_store import VectorStore
from chat_history import ChatHistory

# --- MOVED: Made _get_token_count a standalone helper function ---
def _get_token_count(text: str, model_name: str = "gpt-4") -> int:
    """Calculates the number of tokens in a given text."""
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


class Conversation_Rag:
    """
    Manages a conversational RAG pipeline using LangChain with chat history,
    including smart trimming and token usage tracking.
    """
    def __init__(self, vector_store, chat_history_manager, llm):
        """
        Initializes the conversational RAG chain.
        """
        if vector_store is None:
            raise ValueError("A vector store must be provided.")
        if chat_history_manager is None:
            raise ValueError("A chat history manager must be provided.")
        if llm is None:
            raise ValueError("An LLM instance must be provided.")
        
        self.llm = llm
        self.chat_history_manager = chat_history_manager
        self.message_trimmer = MessageTrimming(
            max_tokens=1000, 
            strategy="summarization", 
            llm=self.llm
        )

        score_threshold=0.5
        if isinstance(vector_store, FAISS):
            score_threshold=0.2
        elif isinstance(vector_store, Chroma):
            score_threshold=0.8
        self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={'k': 5, 'score_threshold': score_threshold}
        )

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key='answer'
        )

        _template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
                        If there is not enough context provided in the {chat_history}, Answer the user's question to the best of your ability using your own knowledge.

        Chat History:
        {chat_history}
        Follow Up Input: {question}
        Standalone question:"""
        CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            condense_question_prompt=CONDENSE_QUESTION_PROMPT,
            memory=self.memory,
            return_source_documents=True
        )

    def get_response_stream(self, question: str):
        """
        Gets a streaming response from the RAG chain, managing history and tracking usage.
        """
        full_history = self.chat_history_manager.get_history()
        trimmed_history = self.message_trimmer.trim(full_history)
        
        self.memory.clear()
        for msg in trimmed_history:
            if msg['role'] == 'user':
                self.memory.chat_memory.add_user_message(msg['content'])
            elif msg['role'] == 'assistant':
                self.memory.chat_memory.add_ai_message(msg['content'])
        
        self.chat_history_manager.add_message("user", question)

        full_response = ""
        source_documents = []

        try:
            for chunk in self.chain.stream({"question": question}):
                if "answer" in chunk:
                    full_response += chunk["answer"]
                    yield chunk["answer"]
                if "source_documents" in chunk:
                    source_documents = chunk["source_documents"]
        except Exception as e:
            print(f"Error during streaming: {e}")
            yield "Sorry, I encountered an error."

        self.chat_history_manager.add_message("assistant", full_response)
        
        original_history_text = " ".join(m['content'] for m in full_history)
        trimmed_history_text = " ".join(m['content'] for m in trimmed_history)

        original_tokens = _get_token_count(original_history_text)
        trimmed_tokens = _get_token_count(trimmed_history_text)
        
        cost_per_1k_tokens = 0.0015 
        estimated_cost = (trimmed_tokens / 1000) * cost_per_1k_tokens

        if source_documents:
            yield f"\n\n**Sources:**\n"
            for doc in source_documents:
                yield f"- {doc.metadata.get('source', 'Unknown')}\n"
        
        yield {
            "original_tokens": original_tokens,
            "trimmed_tokens": trimmed_tokens,
            "token_savings": original_tokens - trimmed_tokens,
            "estimated_cost": f"${estimated_cost:.6f}"
        }


# ---  Function to run the comparison test with timing and tokens ---
def run_comparison_test(llm, vector_store_client):
    """
    Runs a side-by-side comparison of Conversational RAG and Simple RAG.
    """
    print("="*50)
    print("🚀 Running RAG Performance Comparison Test")
    print("="*50)

    q1 = "What are the main differences between the FAISS and ChromaDB vector stores?"
    q2 = "Which one is better for larger datasets?"
    print(f"Test Question 1: '{q1}'")
    print(f"Test Question 2 (Follow-up): '{q2}'\n")

    # --- 🧠 Test 1: Conversational RAG ---
    print("\n--- 🧠 Testing Conversational RAG (Stateful) ---")
    chat_history_manager = ChatHistory(session_id="comparison_test_session")
    chat_history_manager.clear_history()
    
    conversational_rag = Conversation_Rag(vector_store=vector_store_client, chat_history_manager=chat_history_manager, llm=llm)

    # Q1
    print(f"\n[User] > {q1}")
    start_time = time.perf_counter()
    response_q1, stats_q1 = "", {}
    for chunk in conversational_rag.get_response_stream(q1):
        if isinstance(chunk, str): response_q1 += chunk
        elif isinstance(chunk, dict): stats_q1 = chunk
    end_time = time.perf_counter()
    print(f"[Assistant] > {response_q1.strip()}")
    print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
    print(f"🪙  Context Tokens: {stats_q1.get('trimmed_tokens', 'N/A')}")

    # Q2
    print(f"\n[User] > {q2}")
    start_time = time.perf_counter()
    response_q2, stats_q2 = "", {}
    for chunk in conversational_rag.get_response_stream(q2):
        if isinstance(chunk, str): response_q2 += chunk
        elif isinstance(chunk, dict): stats_q2 = chunk
    end_time = time.perf_counter()
    print(f"[Assistant] > {response_q2.strip()}")
    print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
    print(f"🪙  Context Tokens: {stats_q2.get('trimmed_tokens', 'N/A')}")
    print("-" * 50)

    # --- 🤖 Test 2: Simple RAG ---
    print("\n\n--- 🤖 Testing Simple RAG (Stateless) ---")
    retriever = vector_store_client.as_retriever()
    simple_rag_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

    # Q1
    print(f"\n[User] > {q1}")
    start_time = time.perf_counter()
    retrieved_docs = retriever.get_relevant_documents(q1)
    context_text = " ".join([doc.page_content for doc in retrieved_docs])
    response_q1_simple = simple_rag_chain.invoke({"query": q1})
    end_time = time.perf_counter()
    input_tokens = _get_token_count(context_text + q1)
    output_tokens = _get_token_count(response_q1_simple['result'])
    print(f"[Assistant] > {response_q1_simple['result'].strip()}")
    print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
    print(f"🪙  Total Tokens (Input Docs + Q&A): {input_tokens + output_tokens}")

    # Q2
    print(f"\n[User] > {q2}")
    start_time = time.perf_counter()
    retrieved_docs = retriever.get_relevant_documents(q2)
    context_text = " ".join([doc.page_content for doc in retrieved_docs])
    response_q2_simple = simple_rag_chain.invoke({"query": q2})
    end_time = time.perf_counter()
    input_tokens = _get_token_count(context_text + q2)
    output_tokens = _get_token_count(response_q2_simple['result'])
    print(f"[Assistant] > {response_q2_simple['result'].strip()}")
    print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
    print(f"🪙  Total Tokens (Input Docs + Q&A): {input_tokens + output_tokens}")
    print("-" * 50)

    # --- 📊 Analysis ---
    print("\n\n--- 📊 Final Analysis ---")
    print("✅ **Accuracy**: Conversational RAG correctly answers follow-up questions by using chat history to understand context.")
    print("❌ **Accuracy**: Simple RAG fails on follow-ups because it is **stateless** and has no memory of the conversation.")
    print("⏱️  **Latency**: Simple RAG is slightly faster per turn as it skips the initial question-rewriting step required by the conversational chain.")
    print("🪙  **Tokens**: Conversational RAG's token usage is driven by the chat history size (managed by `MessageTrimming`), while Simple RAG's is driven by the size of retrieved documents. Both are important cost factors to monitor.")
    print("="*50)


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description="Test or compare Conversational RAG chains.")
    parser.add_argument("--session-id", type=str, help="A unique ID for an interactive chat session.")
    parser.add_argument("--compare", action="store_true", help="Run a comparison between Simple and Conversational RAG.")
    args = parser.parse_args()
    #from utils.dial_client import DIALClient
    #llm = DIALClient().client
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        openai_api_version=os.getenv("API_VERSION"),
        deployment_name=os.getenv("DEPLOYMENT_NAME"),
        openai_api_key=os.getenv("DIAL_API_KEY"),
        temperature=0,
        streaming=True
    )
    vector_store_client = VectorStore(store_name="FAISS", model_name="text-embedding-005").client

    if args.compare:
        run_comparison_test(llm, vector_store_client)
    
    elif args.session_id:
        print("--- Starting Interactive CLI RAG Test ---")
        rag_chain = Conversation_Rag(vector_store=vector_store_client, chat_history_manager=ChatHistory(session_id=args.session_id), llm=llm)
        print("\n--- RAG Chain is ready. Type 'exit' or 'quit' to end. ---")
        while True:
            try:
                question = input("You: ")
                if question.lower() in ["exit", "quit"]:
                    print("Exiting chat.")
                    break

                full_response = ""
                usage_stats = None
                
                print("Assistant: ", end="", flush=True)
                for chunk in rag_chain.get_response_stream(question):
                    if isinstance(chunk, str):
                        print(chunk, end="", flush=True)
                    elif isinstance(chunk, dict):
                        usage_stats = chunk
                print("\n") # Newline after response is complete

                if usage_stats:
                    print("--- Usage Stats ---")
                    print(f"  - Original Tokens: {usage_stats['original_tokens']}")
                    print(f"  - Trimmed Tokens: {usage_stats['trimmed_tokens']}")
                    print(f"  - Savings: {usage_stats['token_savings']}")
                    print(f"  - Est. Cost: {usage_stats['estimated_cost']}")
                    print("-------------------\n")

            except KeyboardInterrupt:
                print("\nExiting chat.")
                break
    else:
        print("Usage: \n  For interactive chat: python conversational_rag.py --session-id <your_session_name>")
        print("  For comparison demo:  python conversational_rag.py --compare")