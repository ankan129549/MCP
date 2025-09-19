import tiktoken
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from accelerate import Accelerator # Still good to keep for device_map="auto"



def count_openai_tokens(text: str, model_name: str) -> int:
    """
    Calculates tokens for OpenAI models (GPT-3.5-Turbo, GPT-4, GPT-4o).
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
        return len(encoding.encode(text))
    except KeyError:
        print(f"Warning: Model '{model_name}' not found in tiktoken. Using 'cl100k_base' as fallback.")
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

def count_hf_tokens(text: str, model_path: str) -> int:
    """
    Calculates tokens for Hugging Face models (Mistral, Llama).
    """
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    return len(tokenizer.encode(text))



# --- Text to tokenize ---
text_versions = {
    "short": "Hello, world! This is a short sentence.",
    "medium": "This is a slightly longer piece of text to demonstrate token counting. It includes a few more words and some punctuation.",
    "long": """
    Large language models (LLMs) are a type of artificial intelligence program that can generate human-like text.
    They are trained on vast amounts of text data and can perform various natural language processing tasks,
    such as language translation, text summarization, and question answering.
    The efficiency of an LLM is often measured by its ability to process and generate text using a minimal number of tokens,
    as token usage directly impacts computational cost and inference speed. Different models employ distinct tokenization
    strategies, leading to variations in token counts for the same input text.
    Understanding these differences is crucial for optimizing LLM applications.
    """
}

# --- Calculate tokens for each model ---

print("--- OpenAI Models ---")
for version, text in text_versions.items():
    print(f"\nText Version: '{version}'")
    print(f"Original Text (first 50 chars): '{text[:50]}...'")

    # GPT-3.5-Turbo (uses cl100k_base encoding)
    gpt35_tokens = count_openai_tokens(text, "gpt-3.5-turbo")
    print(f"GPT-3.5-Turbo Tokens: {gpt35_tokens}")

    # GPT-4 (uses cl100k_base encoding)
    gpt4_tokens = count_openai_tokens(text, "gpt-4")
    print(f"GPT-4 Tokens: {gpt4_tokens}")

    # GPT-4o (uses o200k_base encoding)
    gpt4o_tokens = count_openai_tokens(text, "gpt-4o")
    print(f"GPT-4o Tokens: {gpt4o_tokens}")


print("\n--- Other Models (Optional Comparison) ---")

# Mistral Nemo (using quantization and device_map)
try:
    mistral_nemo_model_path = "mistralai/Mistral-Nemo-Instruct-2407" # The model you specified
    print(f"\nAttempting to load Mistral Nemo: {mistral_nemo_model_path}")

    # Quantization configuration
    quantization_config_4bit = {
        "load_in_4bit": True,
        "bnb_4bit_quant_type": "nf4",
        "bnb_4bit_compute_dtype": torch.bfloat16, # Or torch.float16 if bfloat16 is not supported
        "bnb_4bit_use_double_quant": True,
    }

    print("Trying to load Mistral Nemo with 4-bit quantization...")
    tokenizer_nemo = AutoTokenizer.from_pretrained(mistral_nemo_model_path)
    model_nemo = AutoModelForCausalLM.from_pretrained(
        mistral_nemo_model_path,
        **quantization_config_4bit, # Apply 4-bit quantization
        device_map="auto", # Automatically distributes model layers
        torch_dtype=torch.bfloat16, # Use bfloat16 for computation if supported by GPU
    )
    print("Mistral Nemo loaded successfully with 4-bit quantization!")

    for version, text in text_versions.items():
        print(f"\nText Version: '{version}'")
        print(f"Original Text (first 50 chars): '{text[:50]}...'")
        mistral_nemo_tokens = count_hf_tokens(text, mistral_nemo_model_path)
        print(f"Mistral Nemo Tokens: {mistral_nemo_tokens}")

    # Free up memory if you want to load another large model
    del model_nemo
    del tokenizer_nemo
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

except Exception as e:
    print(f"Could not load Mistral Nemo model with 4-bit quantization: {e}")
    print("If you have insufficient VRAM/RAM, consider running it on a machine with more resources.")
    print("Ensure you have requested access to the Mistral Nemo model on Hugging Face and logged in.")


# Llama 3.1 (You'll need to specify a model path from Hugging Face)
try:
    llama31_model_path = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    print(f"\nAttempting to load LLaMA 3.1: {llama31_model_path}")

    print("Trying to load LLaMA 3.1 with 4-bit quantization...")
    tokenizer_llama = AutoTokenizer.from_pretrained(llama31_model_path)
    model_llama = AutoModelForCausalLM.from_pretrained(
        llama31_model_path,
        **quantization_config_4bit, # Apply 4-bit quantization
        device_map="auto", # Automatically distributes model layers
        torch_dtype=torch.bfloat16, # Use bfloat16 for computation if supported by GPU
    )
    print("LLaMA 3.1 loaded successfully with 4-bit quantization!")

    for version, text in text_versions.items():
        print(f"\nText Version: '{version}'")
        print(f"Original Text (first 50 chars): '{text[:50]}...'")
        llama31_tokens = count_hf_tokens(text, llama31_model_path)
        print(f"LLaMA 3.1 Tokens: {llama31_tokens}")

except Exception as e:
    print(f"Could not load LLaMA 3.1 model with 4-bit quantization: {e}")
    print("Ensure you have requested access to the LLaMA 3.1 model on Hugging Face and logged in.")