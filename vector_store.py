from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS, Chroma
from utils.dial_openAI_embedding_client import DIALEmbeddingClient

class VectorStore:
    """
    A class to configure and manage the vector store and embedding model.
    """
    def __init__(self, store_name: str, model_name: str):
        """
        Initializes the VectorStore based on user selections.

        Args:
            store_name (str): The name of the vector store (e.g., "FAISS").
            model_name (str): The name of the embedding model.
        """
        self.store_name = store_name
        self.model_name = model_name
        self.client = None
        
        print(f" Initializing VectorStore...")
        print(f"   - Store: {self.store_name}")
        print(f"   - Model: {self.model_name}")
        
        self._initialize_client()
    

    def _initialize_client(self):
        """
        Initializes the vector store client (FAISS or ChromaDB).
        """
        documents = self.load_documents()
        embeddings = DIALEmbeddingClient(model_name=self.model_name).client
        
        if self.store_name == "FAISS":
            self.client = FAISS.from_documents(documents, embeddings)
            print("FAISS vector store created successfully.")
        elif self.store_name == "ChromaDB":
           self.client = Chroma.from_documents(documents, embeddings)
           print("ChromaDB vector store created successfully.")
        else:
            raise ValueError(f"Unsupported vector store: {self.store_name}")
       

    def get_info(self):
        """Returns a summary of the current configuration."""
        return f"Store: **{self.store_name}** | Model: **{self.model_name}**"
    
    def load_documents(self, content_dir: str = "data/extracted_content"):
        """
        Loads and splits documents from the specified content directory.
        
        Args:
            content_dir (str): Directory containing content files.
        """
        print(f"Loading documents from '{content_dir}'...")
       
        loader = DirectoryLoader(content_dir, glob="**/*.json", loader_cls=TextLoader)
        documents = loader.load()
        
        if not documents:
            print("⚠️ No documents found. Please check the content directory.")
            # Create a dummy document to avoid errors during initialization
            documents = [type('obj', (object,), {'page_content': 'No content available', 'metadata': {'source': 'dummy'}})()]


        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(documents)
        
        print(f"Loaded {len(documents)} documents and split them into {len(split_docs)} chunks.")
        return split_docs
