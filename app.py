import streamlit as st
from datetime import datetime
from vector_store import VectorStore
from conversational_rag import Conversation_Rag
from chat_history import ChatHistory
from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Conversational RAG UI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store_client" not in st.session_state:
    st.session_state.vector_store_client = None
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None

if "chat_history_manager" not in st.session_state:
    st.session_state.chat_history_manager = ChatHistory() # Creates a new timestamped session on first run
    st.session_state.messages = st.session_state.chat_history_manager.get_history()

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")

    vector_store = st.selectbox(
        "Vector Store",
        ("FAISS", "ChromaDB"),
        index=0,
        help="Select the vector store for retrieval."
    )
    
    vector_store_descriptions = {
        "FAISS": """
        **FAISS Performance:** In-memory and extremely fast for lookups. Ideal for smaller datasets that can fit into RAM, providing the quickest response times.
        """,
        "ChromaDB": """
        **ChromaDB Performance:** Disk-based and persistent. Better suited for larger datasets and allows for more complex filtering. Can be slightly slower than FAISS due to disk I/O.
        """
    }
    
    if vector_store in vector_store_descriptions:
        st.info(vector_store_descriptions[vector_store])

    embedding_model = st.selectbox(
        "Embedding Model",
        ("text-embedding-3-small-1", "text-embedding-005"),
        index=1,
        help="Select the model to generate embeddings."
    )

    if st.button("Initialize System"):
        with st.spinner("Initializing..."):
            API_KEY = os.getenv("DIAL_API_KEY")
            AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
            API_VERSION = os.getenv("API_VERSION")
            DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

            # Initialize LLM here to pass to RAG chain
            llm = AzureChatOpenAI(
                azure_endpoint=AZURE_ENDPOINT,
                openai_api_version=API_VERSION,
                deployment_name=DEPLOYMENT_NAME,
                openai_api_key=API_KEY,
                temperature=0,
                streaming=True
            )
            
            st.session_state.vector_store_client = VectorStore(
                store_name=vector_store, 
                model_name=embedding_model
            ).client
            
            st.session_state.rag_chain = Conversation_Rag(
                vector_store=st.session_state.vector_store_client,
                chat_history_manager=st.session_state.chat_history_manager,
                llm=llm  # Pass the initialized LLM
            )
        st.success("System initialized!")

    st.markdown("---")
    st.markdown("### Chat Actions")

    if st.button("💾 Archive Chat Session"):
        if st.session_state.messages:
            st.session_state.chat_history_manager.archive_session()
            st.success("Chat archived in `data/chat_sessions/`")
        else:
            st.warning("Cannot archive an empty chat.")

    if st.button("🗑️ Clear & Reset Chat"):
        st.session_state.chat_history_manager.clear_history()
        st.session_state.messages = []
        # Create a new session manager for the new chat
        st.session_state.chat_history_manager = ChatHistory()
        st.rerun()

st.title("🧠 Conversational RAG Interface")
st.caption(f"Using Vector Store: `{vector_store}` | Embedding Model: `{embedding_model}`")

if not st.session_state.messages:
    st.info("Start the conversation by typing your message below.")

# --- MAIN MESSAGE DISPLAY LOOP ---
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        ts = datetime.fromisoformat(message["timestamp"]).strftime('%I:%M:%S %p')
        st.markdown(f"*<small>{ts}</small>*", unsafe_allow_html=True)
        st.markdown(message["content"])

        # Display usage stats and feedback buttons for assistant messages
        if message["role"] == "assistant":
            if "usage_stats" in message:
                usage_stats = message["usage_stats"]
                with st.expander("📊 Usage & Cost Estimation"):
                    st.markdown(f"- **Original History Tokens:** `{usage_stats['original_tokens']}`")
                    st.markdown(f"- **Trimmed History Tokens (Context):** `{usage_stats['trimmed_tokens']}`")
                    st.markdown(f"- **Token Savings:** `{usage_stats['token_savings']}`")
                    st.markdown(f"- **Estimated Cost for this Turn:** `{usage_stats['estimated_cost']}`")
            
            # Add feedback buttons with unique keys
            col1, col2, col3 = st.columns([1, 1, 10])
            with col1:
                st.button("👍", key=f"thumbs_up_{i}")
            with col2:
                st.button("👎", key=f"thumbs_down_{i}")


# --- CHAT INPUT PROCESSING ---
if prompt := st.chat_input("Ask a question"):
    if st.session_state.rag_chain is None:
        st.error("System is not initialized. Please initialize from the sidebar.")
    else:
        with st.chat_message("user"):
            st.markdown(f"*<small>{datetime.now().strftime('%I:%M:%S %p')}</small>*", unsafe_allow_html=True)
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            usage_stats = None
            
            st.markdown(f"*<small>{datetime.now().strftime('%I:%M:%S %p')}</small>*", unsafe_allow_html=True)

            for chunk in st.session_state.rag_chain.get_response_stream(prompt):
                if isinstance(chunk, str):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                elif isinstance(chunk, dict):
                    usage_stats = chunk
            
            message_placeholder.markdown(full_response)
        
        # Attach usage_stats to the last assistant message in the session state
        if usage_stats:
            for msg in reversed(st.session_state.messages):
                if msg["role"] == "assistant":
                    msg["usage_stats"] = usage_stats
                    break
        
        # Force the script to re-run to display the updated state (the expander)
        st.rerun()