# Install necessary libraries if not already installed
# !pip install tiktoken numpy

import tiktoken
import numpy as np
import pandas as pd

# --- Part 1: Tokenization Across Models and Languages ---

# Define the texts for each language as provided in the PDF
texts = {
    "English": "The cat sat on the windowsill, watching the rain fall. Suddenly, a flash of lightning lit up the sky, startling the little creature. It leaped down and scurried to its favorite hiding spot under the bed.",
    "Spanish": "El gato estaba sentado en el alféizar de la ventana, mirando la lluvia caer. De repente, un relámpago iluminó el cielo, sobresaltando a la pequeña criatura. Saltó y corrió a su escondite favorito debajo de la cama.",
    "Arabic": "جلست القطة على حافة النافذة، تراقب هطول المطر. وفجأة، أضاءت ومضة من البرق السماء، مما . أثار ذهول المخلوق الصغير. قفزت إلى أسفل وهرعت إلى مكان اختبائها المفضل تحت السرير",
    "Hindi": "बिल्ली खिड़की पर बैठी हुई बारिश को देख रही थी। अचानक, आसमान में बिजली चमकी, जिससे छोटा जीव चौंक गया। वह नीचे कूद गई और बिस्तर के नीचे अपनी पसंदीदा छिपने की जगह पर भाग गई।"
}

# Define the OpenAI models and their corresponding encodings
# As per OpenAI documentation and search results:
# GPT-4o uses 'o200k_base'
# GPT-4 and GPT-3.5-Turbo use 'cl100k_base'
# Note: For Mistral Nemo and LLAMA 3.1, specific tokenizer libraries would be needed,
# which are not directly available via tiktoken. This example focuses on OpenAI models.
models = {
    "GPT-3.5-Turbo": "cl100k_base",
    "GPT-4": "cl100k_base",
    "GPT-4o": "o200k_base"
}

# Dictionary to store token counts
token_counts = {}

print("Calculating token counts...\n")

for lang, text in texts.items():
    token_counts[lang] = {}
    for model_name, encoding_name in models.items():
        try:
            # Get the encoding for the specified model
            encoding = tiktoken.get_encoding(encoding_name)
            # Encode the text and get the number of tokens
            tokens = encoding.encode(text)
            num_tokens = len(tokens)
            token_counts[lang][model_name] = num_tokens
            print(f"Language: {lang}, Model: {model_name}, Tokens: {num_tokens}")
        except Exception as e:
            token_counts[lang][model_name] = f"Error: {e}"
            print(f"Error for {lang} with {model_name}: {e}")

print("\nToken count calculation complete.")

# --- Part 2: Positional Embeddings ---

def get_sinusoidal_positional_embeddings(sequence_length: int, d_model: int) -> np.ndarray:
    """
    Generates sinusoidal positional embeddings.

    Args:
        sequence_length (int): The maximum length of the sequence (number of tokens).
        d_model (int): The dimension of the embedding space.

    Returns:
        np.ndarray: A numpy array of shape (sequence_length, d_model)
                    containing the positional embeddings.
    """
    # Initialize a matrix for positional encodings with zeros
    positional_embeddings = np.zeros((sequence_length, d_model))

    # Create a position vector (0, 1, 2, ..., sequence_length-1)
    position = np.arange(sequence_length)[:, np.newaxis]

    # Calculate the division term for the sinusoidal functions
    # This term decreases with increasing dimension index (i)
    div_term = np.exp(np.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))

    # Apply sine to even indices in the embedding dimension
    positional_embeddings[:, 0::2] = np.sin(position * div_term)

    # Apply cosine to odd indices in the embedding dimension
    positional_embeddings[:, 1::2] = np.cos(position * div_term)

    return positional_embeddings

print("\n--- Positional Embeddings Generation for Each Language ---")

# Define a common embedding dimension (d_model) for demonstration
# This is a hyperparameter of the LLM and can vary.
embedding_dimension = 512

# Dictionary to store generated positional embeddings
generated_pos_embeddings = {}

for lang, models_data in token_counts.items():
    # Use the token count from GPT-4o as the sequence length for positional embeddings
    # since it's a modern model and the counts are consistent across OpenAI models for these texts.
    sequence_length = models_data.get("GPT-4o")
    if isinstance(sequence_length, int): # Ensure it's an integer (not an error string)
        print(f"\nGenerating positional embeddings for {lang} (Sequence Length: {sequence_length}, Embedding Dimension: {embedding_dimension})...")
        pos_embeddings = get_sinusoidal_positional_embeddings(sequence_length, embedding_dimension)
        generated_pos_embeddings[lang] = pos_embeddings
        print(f"Shape of positional embeddings for {lang}: {pos_embeddings.shape}")
        # Optionally print a small sample
        print(f"First 3 positions, first 5 dimensions for {lang}:\n{pos_embeddings[:3, :5]}")
    else:
        print(f"\nCould not generate positional embeddings for {lang} due to tokenization error.")

print("\nPositional embeddings generation complete for all languages.")
print("\nExplanation of Positional Embeddings:")
print("Positional embeddings are crucial for Transformer models because they process input tokens in parallel,")
print("meaning they don't inherently 'know' the order of words. These embeddings inject information about")
print("the position of each token in the sequence.")
print("The sinusoidal functions (sine and cosine) are used because they create a unique pattern for each position")
print("that can generalize to longer sequences than seen during training. Different frequencies allow the model")
print("to capture both fine-grained and broad positional relationships.")
print("When an LLM processes text, the token embedding (representing the word's meaning) is combined (usually added)")
print("with its corresponding positional embedding. This combined vector then carries both semantic and positional information.")
