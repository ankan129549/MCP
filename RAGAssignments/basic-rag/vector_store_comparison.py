"""
TODO: Compare FAISS vs ChromaDB vector stores

Requirements:
1. Implement both FAISS and ChromaDB vector stores
2. Compare indexing performance (time to create index)
3. Compare retrieval performance (query speed)
4. Compare storage requirements
5. Document trade-offs and recommendations

Example usage:
    python vector_store_comparison.py
"""

import time
import os
import shutil
import numpy as np
import faiss
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any


 # --- Helper function to get directory size ---
def get_dir_size(path='.'):

        """Calculates the total size of a directory in bytes."""
        total = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += get_dir_size(entry.path)
        print(f"total Docs : {total}")
        return total


class VectorStoreComparison:

   


    def __init__(self):
        """
        TODO: Initialize comparison framework
        """
        # --- 1. Setup Data Directory ---
        data_dir = "data/extracted_content"
        # --- 2. Initialize Models and Load Documents ---
        print("Initializing comparison with a small, fast embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        print(f"Loading documents from '{data_dir}'...")
        self.documents = []
        # Loop through all files in the directory
        for filename in os.listdir(data_dir):
            file_path = os.path.join(data_dir, filename)
            # Check if it's a file to avoid reading subdirectories
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.documents.append(f.read())
                except Exception as e:
                    print(f"Warning: Could not read file {file_path}. Reason: {e}")

        if not self.documents:
            raise ValueError(f"No documents found in '{data_dir}'. Please add text files to this directory.")

        print(f"Successfully loaded {len(self.documents)} documents.")

        # Use a lightweight and fast model for demonstration purposes
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        
        # Get embedding dimension from the model
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Placeholders for stores and paths
        self.faiss_index = None
        self.faiss_doc_store = []
        self.chroma_collection = None
        
        self.faiss_path = "faiss_index.bin"
        self.chroma_path = "chroma_db"
        
        # Clean up previous runs
        self._cleanup()

    def setup_faiss_store(self, documents: List[str]):
            """
            TODO: Setup FAISS vector store
            
            Args:
                documents (List[str]): Documents to index
                
            Returns:
                FAISS store object
            """
            embeddings = self.embedding_model.encode(documents, show_progress_bar=False)
            self.faiss_index = faiss.IndexFlatL2(self.embedding_dim)
            self.faiss_index.add(np.array(embeddings).astype('float32'))
            self.faiss_doc_store = documents
            return self.faiss_index, self.faiss_doc_store
    
    def setup_chromadb_store(self, documents: List[str]):
        """
        TODO: Setup ChromaDB vector store
        
        Args:
            documents (List[str]): Documents to index
            
        Returns:
            ChromaDB store object
        """
        embeddings = self.embedding_model.encode(documents, show_progress_bar=False)
        client = chromadb.PersistentClient(path=self.chroma_path)
        
        self.chroma_collection = client.get_or_create_collection(
            name="document_collection",
            #embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(model_name='all-MiniLM-L6-v2')
        )
        # ChromaDB requires unique IDs for each document
       # print(f"After creating the chroma collection ::: {self.chroma_collection}")
        doc_ids = [f"doc_{i}" for i in range(len(documents))]
       # print(f"doc_ids :: {doc_ids}")
        self.chroma_collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            ids=doc_ids
        )
        #print("before returning from chroma db setup")
        return self.chroma_collection
        
    def measure_indexing_performance(self, documents: List[str]):
        """
        TODO: Measure time to create indexes for both stores
        
        Args:
            documents (List[str]): Documents to index
            
        Returns:
            Dict[str, float]: Indexing times for each store
        """
         # --- FAISS Indexing ---
        start_time_faiss = time.time()
        self.setup_faiss_store(documents)
        end_time_faiss = time.time()
        faiss_indexing_time = end_time_faiss - start_time_faiss
        #print(f"*****FAISS store setup complete in {faiss_indexing_time} ***")
        # --- ChromaDB Indexing ---
        start_time_chroma = time.time()
        self.setup_chromadb_store(documents)
        #print("*****Chroma complete***")
        end_time_chroma = time.time()
        chroma_indexing_time = end_time_chroma - start_time_chroma

        return {
            "FAISS": faiss_indexing_time,
            "ChromaDB": chroma_indexing_time
        }
    
    def measure_query_performance(self, query: str, k: int = 5, num_queries: int = 100):
        """
        TODO: Measure query performance for both stores
        
        Args:
            query (str): Test query
            num_queries (int): Number of queries to run for average
            
        Returns:
            Dict[str, float]: Query times for each store
        """
        query_times = {}

        # --- FAISS Querying ---
        query_embedding = self.embedding_model.encode([query]).astype('float32')
        start_time_faiss = time.time()
        for _ in range(num_queries):
            self.faiss_index.search(query_embedding, k)
        end_time_faiss = time.time()
        avg_time_faiss = ((end_time_faiss - start_time_faiss) / num_queries) * 1000  # to ms
        query_times["FAISS"] = avg_time_faiss

        # --- ChromaDB Querying ---
        start_time_chroma = time.time()
        for _ in range(num_queries):
            self.chroma_collection.query(query_texts=[query], n_results=k)
        end_time_chroma = time.time()
        avg_time_chroma = ((end_time_chroma - start_time_chroma) / num_queries) * 1000  # to ms
        query_times["ChromaDB"] = avg_time_chroma

        return query_times
    
    def compare_storage_requirements(self):
        """
        TODO: Compare storage/memory requirements
        
        Returns:
            Dict[str, int]: Storage requirements for each store
        """
        storage = {}

        # --- FAISS Storage ---
        faiss.write_index(self.faiss_index, self.faiss_path)
        storage["FAISS"] = os.path.getsize(self.faiss_path)
        
        # --- ChromaDB Storage ---
        # ChromaDB is already persisted, so we just measure the directory size.
        storage["ChromaDB"] = get_dir_size(self.chroma_path)

        return storage
    
    def run_comparison(self):
        """
        TODO: Run complete comparison and generate report
        """
        #print("=== Vector Store Comparison Report ===")
        #print("TODO: Implement comparison logic")
        
        # TODO: Load test documents
        # TODO: Run indexing performance tests
        # TODO: Run query performance tests
        # TODO: Compare storage requirements
        # TODO: Generate recommendations
        print("\n" + "="*40)
        print("=== Vector Store Comparison Report ===")
        print("="*40 + "\n")

        # 1. Indexing Performance
        print("--- 1. Measuring Indexing Performance ---")
        indexing_times = self.measure_indexing_performance(self.documents)
        print(f"FAISS Indexing Time:     {indexing_times['FAISS']:.4f} seconds")
        print(f"ChromaDB Indexing Time:  {indexing_times['ChromaDB']:.4f} seconds")
        print("-" * 40 + "\n")

        # 2. Query Performance
        print("--- 2. Measuring Query Performance ---")
        test_query = "Tell me About Sundar Pichai?"
        query_times = self.measure_query_performance(test_query)
        print(f"Test query: '{test_query}' (averaged over 100 runs)")
        print(f"FAISS Avg Query Time:    {query_times['FAISS']:.4f} ms")
        print(f"ChromaDB Avg Query Time: {query_times['ChromaDB']:.4f} ms")
        print("-" * 40 + "\n")

        # --- NEW SECTION: Print Search Results ---
        print("--- 3. Verifying Search Results ---")
        print(f"Retrieving top 5 results for the query: '{test_query}'\n")

        # FAISS search and results
        print("🔍 FAISS Results:")
        query_embedding = self.embedding_model.encode([test_query]).astype('float32')
        distances, indices = self.faiss_index.search(query_embedding, 5)
        # The 'indices' array is 2D, so we access the first element
        for i, doc_index in enumerate(indices[0]):
            print(f"  {i+1}. (Dist: {distances[0][i]:.4f}) - '{self.faiss_doc_store[doc_index]}'")
        
        print("\n") # Add a newline for spacing

        # ChromaDB search and results
        print("🔍 ChromaDB Results:")
        chroma_results = self.chroma_collection.query(query_texts=[test_query], n_results=5)
        # The 'documents' list is nested, so we access the first element
        for i, doc in enumerate(chroma_results['documents'][0]):
            dist = chroma_results['distances'][0][i]
            print(f"  {i+1}. (Dist: {dist:.4f}) - '{doc}'")
        print("-" * 40 + "\n")
        # --- END OF NEW SECTION ---

        # 3. Storage Requirements
        print("--- 3. Comparing Storage Requirements ---")
        storage_sizes = self.compare_storage_requirements()
        print(f"FAISS Storage Size:      {storage_sizes['FAISS'] / 1024 / 1024:.2f} MB")
        print(f"ChromaDB Storage Size:   {storage_sizes['ChromaDB'] / 1024 / 1024:.2f} MB")
        print("-" * 40 + "\n")
        self._cleanup()
        
    def _cleanup(self):
        """Removes temporary files and directories created during the comparison."""
        if os.path.exists(self.faiss_path):
            os.remove(self.faiss_path)
        if os.path.exists(self.chroma_path):
            shutil.rmtree(self.chroma_path)
        print("Cleaned up previous run artifacts.")

if __name__ == "__main__":
    comparison = VectorStoreComparison()
    comparison.run_comparison()

