"""
Customer Service Agent: Handles guest communications and support using RAG.
"""
import os
from datetime import datetime
from typing import Dict, Any

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.models.state import HotelState

def _create_faq_vector_store():
    """
    Loads the FAQ PDF and builds a FAISS vector store for RAG.
    """
    print("---")
    print("🧠 Initializing FAQ Vector Store for Customer Service Agent...")

    try:
        # Build a reliable path to 'faq.pdf' from this script's location
        script_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(script_dir, '..'))
        pdf_path = os.path.join(project_root, 'data/faq.pdf')

        if not os.path.exists(pdf_path):
            print(f"❌ Error: FAQ document not found at '{pdf_path}'. RAG will be disabled.")
            return None

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = text_splitter.split_documents(documents)

        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=os.getenv("AZURE_ENDPOINT", "https://ai-proxy.lab.epam.com"),
            api_key=os.getenv("DIAL_API_KEY"),
            api_version=os.getenv("API_VERSION"),
            azure_deployment="text-embedding-3-small-1",
        )
        db = FAISS.from_documents(docs, embeddings)
        print("✅ FAQ Vector Store created successfully.")
        return db.as_retriever()
    except Exception as e:
        print(f"🔥 Error creating vector store: {e}")
        return None

# Initialize the RAG retriever once when the module is loaded
faq_retriever = _create_faq_vector_store()

def customer_service_agent(state: HotelState) -> HotelState:
    """
    Generates a final response to the customer using the DIAL client.
    This version includes sentiment analysis, complaint resolution, and proactive recommendations.
    """
    print("---")
    print("🎧 Customer Service Agent: Generating customer response...")
    dial_client = state['dial_client']
    query =  state['customer_service'].get('customer_query')

    #print(f"query is ----->>>>{query}")
    context = ""
    situation = ""

    try:
        # Highest priority: Handle booking failures from the system state
        if state['booking'].get("status") == "Failed":
            print("- Handling booking failure.")
            context = f"Booking failed. Reason: {state['booking'].get('reason')}. Errors: {state['errors']}"
            situation = f"Inform the customer, {state['booking'].get('customer')} politely about the booking failure at the hotel {state['booking'].get('hotel_name')} and suggest they try a different room type or date."

        # If there's a customer query, perform advanced analysis
        elif query:
            # 1. Add sentiment analysis for customer feedback
            sentiment = dial_client.analyze_sentiment(str(query))
            state['customer_service']['sentiment'] = sentiment
            print(f"- Customer sentiment analyzed as: {sentiment}")

            # 2. Implement complaint resolution workflow
            if sentiment == "NEGATIVE":
                print("- Activating complaint resolution workflow.")
                state['customer_service']['complaint_logged'] = True
                context = f"{state['customer_service'].get('customer')} has expressed a complaint or negative feedback. Their message is: '{query}'. Their booking details are: {state['booking']}."
                situation = "Generate an empathetic response. Apologize for the inconvenience, validate their concern, and offer a concrete resolution (e.g., offer to connect them with a manager, provide a 10% discount on their next stay, or offer a room upgrade if applicable). Ensure the tone is reassuring."

            # 3. Handle POSITIVE or NEUTRAL queries with proactive recommendations
            else:
                print("- Handling standard query with proactive recommendation.")
                faq_context = ""
                if faq_retriever:
                    retrieved_docs = faq_retriever.invoke(query)
                    faq_context = " ".join([doc.page_content for doc in retrieved_docs])
                
                context = f"Customer Query: '{query}'.\nRelevant FAQ Info: '{faq_context}'.\nBooking Details: {state['booking']}"
                situation = "First, answer the customer's query directly using the provided info. After answering, add a proactive service recommendation. Suggest a relevant paid service like a 'relaxing spa package', 'convenient airport transfer', or a 'guided city tour'."
        
        # If no query and booking was successful, provide confirmation with a recommendation
        else:
            print("- Providing booking confirmation with proactive recommendation.")
            context = f"Booking was successful. Details: {state['booking']}. Housekeeping status: {state['housekeeping']}."
            situation = f"Provide a friendly confirmation message to {state['booking'].get('customer')} summarizing the booking. After the confirmation, proactively recommend a relevant service like a 'spa package' or 'airport transfer' to enhance their stay."

        # Generate the final response based on the determined context and situation
        response_text = dial_client.generate_response(context, situation)
        state['customer_service']["response_to_customer"] = response_text

    except Exception as e:
        error_message = f"Customer service agent encountered an error: {str(e)}"
        state['errors'].append(error_message)
        state['customer_service']["response_to_customer"] = "We're sorry, but a system error occurred. Please contact support."
        print(f"❌ {error_message}")

    # 4. Integrate with external communication APIs (Simulation)
    print("---")
    print("📞 External API Simulator: Dispatching final response to customer...")
    print(f"   -> To: {state['customer_service'].get('customer')}")
    print(f"   -> Message: '{state['customer_service'].get('response_to_customer', '')[:70]}...'")

 
    return state
