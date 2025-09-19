"""
TODO: Compare different embedding models

Requirements:
1. Test sentence-transformers embeddings (e.g., all-MiniLM-L6-v2)
2. Test other embedding models (if available)
3. Compare embedding quality using similarity tasks
4. Compare embedding speed and computational requirements
5. Document when to use which embedding model

Example usage:
    python embedding_comparison.py
"""

import time
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from utils.dial_openAI_embedding_clinet import DIALEmbeddingClient

class EmbeddingComparison:
    def __init__(self):
        """
        TODO: Initialize embedding models for comparison
        """
        self.models: Dict[str, SentenceTransformer] = {}
        model_names = ["all-MiniLM-L6-v2", "all-mpnet-base-v2"]
        for name in model_names:
            print(f"Loading sentence transformer model {name}")
            self.models[name] = self.load_sentence_transformers_model(name)
            print(f"Sentence Transformers Model {name} loaded successfully.")
        
        self.load_other_embedding_models()
    
    def load_sentence_transformers_model(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        TODO: Load sentence-transformers model
        
        Args:
            model_name (str): Name of the sentence-transformers model
            
        Returns:
            Embedding model object
        """
        try:
            return SentenceTransformer(model_name)
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            raise
    
    def load_other_embedding_models(self):
        """
        TODO: Load other embedding models for comparison
        
        Returns:
            Dict of embedding models
        """
        self.models["openai"] = DIALEmbeddingClient("text-embedding-3-small-1").client
        self.models["vertexai"] = DIALEmbeddingClient("text-embedding-005").client
                           
    def measure_embedding_speed(self, texts: List[str], model_name: str):
        """
        TODO: Measure time to generate embeddings
        
        Args:
            texts (List[str]): Test texts
            model_name (str): Name of the model
            
        Returns:
            float: Average time per embedding
        """
        start_time = time.time()
        model = self.models[model_name]
        if not model:
            raise Exception("model not found")
        if isinstance(model, SentenceTransformer):
                embeddings = model.encode(texts, convert_to_numpy=True)
        else:
                embeddings_list = [model.embed_query(text) for text in (texts) ]
                embeddings = np.array(embeddings_list)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_ms = (total_time / len(texts)) * 1000
        return avg_time_ms
    
    def evaluate_embedding_quality(self, model_name: str):
        """
        TODO: Evaluate embedding quality using similarity tasks
        
        Args:
            model_name (str): Name of the model to evaluate
            
        Returns:
            Dict[str, float]: Quality metrics
        """
        test_pairs = {
            "High Similarity (Cat)": ("The cat is sitting on the mat.", "A feline is resting on the rug."),
            "Medium Similarity (Pets)": ("The dog is playing in the yard.", "My cat loves to chase mice."),
            "Low Similarity (Unrelated)": ("The weather is sunny today.", "Quantum mechanics is a complex field."),
            "Negation Test": ("He is happy.", "He is not happy.")
        }
        
        quality_metrics = {}
        model = self.models[model_name]
        if not model:
            raise Exception("model not found")
        for name, (sent1, sent2) in test_pairs.items():
            embeddings=None
            if isinstance(model, SentenceTransformer):
                embeddings = model.encode([sent1, sent2], convert_to_numpy=True)
                #print(f"embeddings ::: {embeddings}")
            else:
                embeddings_list = [model.embed_query(text) for text in (sent1, sent2) ]
                embeddings = np.array(embeddings_list)
            # Cosine similarity is a measure of similarity between two non-zero vectors.
            # It is calculated as the cosine of the angle between the vectors.
            # A value of 1 means the vectors are identical; 0 means they are orthogonal (unrelated).
            if embeddings is not None:
                similarity_score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                quality_metrics[name] = float(similarity_score)
            
        return quality_metrics
    
    def compare_embedding_dimensions(self):
        """
        TODO: Compare embedding dimensions and their impact
        
        Returns:
            Dict[str, int]: Embedding dimensions for each model
        """
        dimensions = {}
        for name, model in self.models.items():
            # Check if the model object has the specific method
            if hasattr(model, 'get_sentence_embedding_dimension'):
                dim = model.get_sentence_embedding_dimension()
            else:
                # Fallback: encode a dummy sentence and get the length of the vector
                # This works for any model with a standard .encode() method, like a hypothetical
                # 'text-embedding-005' wrapper or other APIs.
                print(f"Note: '{name}' does not have a dedicated dimension method. Inferring dimension...")
                try:
                    # We encode a single, simple text to get a representative embedding
                    test_embedding = model.embed_query("What is the dimension of this model?")
                    # The dimension is the length of the resulting 1D array or list
                    dim = len(test_embedding)
                except Exception as e:
                    print(f"Could not determine dimension for '{name}'. Setting to 0. Error: {e}")
                    dim = 0
                    
            dimensions[name] = dim
            
        return dimensions
    
    def run_comparison(self):
        """
        TODO: Run complete embedding model comparison
        """
        print("=== Embedding Model Comparison Report ===")
        print("TODO: Implement comparison logic")
        
        # TODO: Load test data
        # TODO: Compare embedding speed
        # TODO: Compare embedding quality
        # TODO: Compare computational requirements
        # TODO: Generate recommendations

        # 1. Load test data
        # A sample of sentences for speed testing.
        speed_test_texts = ["This is a test sentence."] * 100
        print(f"Running speed test with {len(speed_test_texts)} sentences...")
        
        # 2. Get embedding dimensions
        dimensions = self.compare_embedding_dimensions()
        
        results = {}

        # 3. Run comparison for each model
        for name, model in self.models.items():
            print(f"\n--- Testing Model: {name} ---")
            
            # Compare embedding speed
            avg_speed = self.measure_embedding_speed(speed_test_texts, name)
            
            # Compare embedding quality
            quality = self.evaluate_embedding_quality(name)
            
            results[name] = {
                "Dimension": dimensions[name],
                "Avg Speed (ms/text)": avg_speed,
                "Quality (Similarity Scores)": quality
            }
            
            print(f"  - Embedding Dimension: {results[name]['Dimension']}")
            print(f"  - Average Speed: {results[name]['Avg Speed (ms/text)']:.4f} ms/text")
            print("  - Quality Scores:")
            for task, score in results[name]['Quality (Similarity Scores)'].items():
                print(f"    - {task}: {score:.4f}")


if __name__ == "__main__":
    comparison = EmbeddingComparison()
    comparison.run_comparison()

