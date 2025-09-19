import tiktoken
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch


def count_and_print_openai_tokens(text: str, model_name: str) -> int:
    """
    Calculates tokens for OpenAI models (GPT-3.5-Turbo, GPT-4, GPT-4o).
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
        encodedText = encoding.encode(text)
       # print (encodedText)
        return len(encodedText)
    except KeyError:
        print(f"Warning: Model '{model_name}' not found in tiktoken. Using 'cl100k_base' as fallback.")
        encoding = tiktoken.get_encoding("cl100k_base")
       
        return len(encoding.encode(text))

def count_hf_tokens(text: str, model_path: str) -> int:
    """
    Calculates tokens for Hugging Face models (Mistral, Llama).
    """  
    # Load the tokenizer (this will download it to cache if not present)
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # Load the model (this will download it to cache if not present)
    # Use torch_dtype=torch.bfloat16 for better memory efficiency if your GPU supports it.
    # device_map="auto" will automatically distribute the model across available devices (GPU/CPU).
    model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16, # Or torch.float16 if bfloat16 is not supported
    device_map="auto"
)
    tokenizer = AutoTokenizer.from_pretrained(model_path, token="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")
    #generator = pipeline(
     #   "text-generation",
      #  model=model,
       # tokenizer=tokenizer,
        #return_full_text=False, # False means to not include the prompt text in the returned text
        #max_new_tokens=50, 
        #do_sample=False, # no randomness in the generated text
    #)

    #print(f"Model '{model_path}' successfully loaded and cached!")
    encodedText = tokenizer.encode(text)
   # print (encodedText)
    print(tokenizer.decode(text))
    return len(encodedText)

# Create a pipeline

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
    gpt35_tokens = count_and_print_openai_tokens(text, "gpt-3.5-turbo")
    print(f"GPT-3.5-Turbo Tokens: {gpt35_tokens}")

    # GPT-4 (uses cl100k_base encoding)
    gpt4_tokens = count_and_print_openai_tokens(text, "gpt-4")
    print(f"GPT-4 Tokens: {gpt4_tokens}")

    # GPT-4o (uses o200k_base encoding)
    gpt4o_tokens = count_and_print_openai_tokens(text, "gpt-4o")
    print(f"GPT-4o Tokens: {gpt4o_tokens}")


print("\n--- Other Models (Optional Comparison) ---")
# Mistral Nemo - HF Path 'mistralai/Mistral-Nemo-Instruct-2407'
# Note: You might need to download the model first or ensure transformers can access it.
#try:
 #   for version, text in text_versions.items():
   #     print(f"\nText Version: '{version}'")
    #    print(f"Original Text (first 50 chars): '{text[:50]}...'")
     #   mistral_nemo_tokens = count_hf_tokens(text, "mistralai/Mistral-Nemo-Instruct-2407") # Example path
      #  print(f"Mistral Nemo Tokens: {mistral_nemo_tokens}")
#except Exception as e:
    #print(f"Could not load Mistral Nemo tokenizer (or model not found): {e}")
    #print("Please ensure 'mistralai/Mistral-Nemo-Instruct-2407' or a valid Mistral model is accessible via Hugging Face.")

# Llama 3.1 - HF path - 'meta-llama/Meta-Llama-3.1-8B-Instruct'

try:
    for version, text in text_versions.items():
        print(f"\nText Version: '{version}'")
        print(f"Original Text (first 50 chars): '{text[:50]}...'")
        llama31_tokens = count_hf_tokens(text, "meta-llama/Llama-3.1-8B-Instruct") # Example path
        print(f"LLaMA 3.1 Tokens: {llama31_tokens}")
except Exception as e:
    print(f"Could not load LLaMA 3.1 tokenizer (or model not found): {e}")
    print("Please ensure 'meta-llama/Meta-Llama-3.1-8B-Instruct' or a valid Llama 3.1 model is accessible via Hugging Face.")