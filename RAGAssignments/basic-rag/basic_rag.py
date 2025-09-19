"""
TODO: Implement basic RAG system using vector stores and DIAL API

Requirements:
1. Load processed content from extract_content.py
2. Create embeddings and populate vector store
3. Implement similarity search for retrieval
4. Build prompt template with retrieved context
5. Generate responses using EPAM DIAL API

Example usage:
    python basic_rag.py --query "What is the main topic of the content?"
"""

import os
import argparse
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
#import faiss
#import chromadb
from langchain_community.vectorstores import FAISS, Chroma
from utils.dial_openAI_embedding_clinet import DIALEmbeddingClient
from utils.dial_client import DIALClient

load_dotenv()

class BasicRAG:
    def __init__(self, vector_store_type="faiss"):
        """
        TODO: Initialize RAG system
        
        Args:
            vector_store_type (str): Type of vector store to use (faiss/chromadb)
        """
        self.dial_client = DIALClient()
        # Initialize vector store and embeddings
        embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME") or "text-embedding-005"
        self.embeddings = DIALEmbeddingClient(model_name=embedding_model_name).client
        self.vector_store_type = vector_store_type
        self.vector_store = None
        # A template to guide the language model in answering questions based on context
        self.prompt_template = """
            You are an assistant for question-answering tasks.
            Use the following pieces of retrieved context to answer the question.
            If you don't know the answer, just say that you don't know. Use three sentences maximum and 
            keep the answer concise.

            Context:
            {context}

            Question:
            {question}

            Answer:
        """
    
    def load_documents(self, content_dir: str = "data/extracted_content"):
        """
        TODO: Load processed documents from content directory
        
        Args:
            content_dir (str): Directory containing processed content
        """
        print(f"Loading documents from '{content_dir}'...")
        loader = DirectoryLoader(content_dir, glob="**/*.json", loader_cls=TextLoader)
        documents = loader.load()
        
        # Split documents into smaller, manageable chunks for better retrieval
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(documents)
        
        print(f"Loaded {len(documents)} documents and split them into {len(split_docs)} chunks.")
        return split_docs
    
    def create_vector_store(self, documents: list):
        """
        TODO: Create vector store from documents
        
        Args:
            documents (list): List of documents to index
        """
        print(f"Creating vector store using '{self.vector_store_type}'...")
        if self.vector_store_type == "faiss":
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            print("FAISS vector store created successfully.")
        elif self.vector_store_type == "chromadb":
            self.vector_store = Chroma.from_documents(documents, self.embeddings)
            print("ChromaDB vector store created successfully.")
        else:
            raise ValueError(f"Unsupported vector store type: {self.vector_store_type}")

    
    def retrieve_relevant_docs(self, query: str, k: int = 3):
        """
        TODO: Retrieve relevant documents for query
        
        Args:
            query (str): User query
            k (int): Number of documents to retrieve
            
        Returns:
            list: List of relevant documents
        """
        if self.vector_store is None:
            raise RuntimeError("Vector store has not been created. Please run create_vector_store first.")
        
        print(f"Retrieving top {k} relevant documents for the query...")
        retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        retrieved_docs = retriever.invoke(query)
        print(f"Retrieved docs from the vector store {retrieved_docs}")
        return retrieved_docs
    
    def generate_response(self, query: str, retrieved_docs: list):
        """
        TODO: Generate response using DIAL API and retrieved context
        
        Args:
            query (str): User query
            retrieved_docs (list): Retrieved relevant documents
            
        Returns:
            str: Generated response
        """
        # Format the retrieved documents into a single context string
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # Create a prompt instance from the template
        prompt = PromptTemplate(
            template=self.prompt_template, input_variables=["context", "question"]
        )
        
        # Format the prompt with the actual context and query
        formatted_prompt = prompt.format(context=context, question=query)
        
        print("Generating response with DIAL API...")
        response = self.dial_client.generate_response(formatted_prompt, query)
        return response
    
    def query(self, query: str):
        """
        TODO: Complete RAG pipeline - retrieve and generate
        
        Args:
            query (str): User query
            
        Returns:
            str: Generated response
        """
        retrieved_docs = self.retrieve_relevant_docs(query)
        response = self.generate_response(query, retrieved_docs)
        return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Basic RAG Question Answering")
    parser.add_argument("--query", required=True, help="Query to ask")
    parser.add_argument("--vector_store", default="faiss", choices=["faiss", "chromadb"], help="Vector store type")
    
    args = parser.parse_args()
    
    # TODO: Implement main execution logic
 # --- Main Execution Logic ---
    print(" Starting RAG system...")
    
    # 1. Initialize the RAG system with the chosen vector store
    rag_system = BasicRAG(vector_store_type=args.vector_store)
    
    # 2. Load and process the source documents
    # This assumes an `extract_content.py` script has placed text files
    # in the `data/extracted_content` directory.
    documents = rag_system.load_documents()
    
    # 3. Create the vector store from the documents
    rag_system.create_vector_store(documents)
    
    # 4. Execute the query against the RAG system
    print(f"\n Answering query: '{args.query}'")
    answer = rag_system.query(args.query)
    
    # 5. Print the final answer
    print("\n --- Generated Answer ---")
    print(answer)
    print("--------------------------")


