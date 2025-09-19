import openai 
from openai import AzureOpenAI
import os



  # --- Configuration ---
API_KEY = os.getenv("DIAL_API_KEY") 
AZURE_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_VERSION = "2024-02-01"
DEPLOYMENT_NAME = "gpt-4" 
    # --- Initialize the client ---
client = None # Initialize client to None
try:
    client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=AZURE_ENDPOINT
    )
    print("✅ Client object created successfully.")
except Exception as e:
    print(f"🔥 Error initializing client object: {e}")
except Exception as e:
    print("🚨 DIAL API key not found or configured correctly.")
    print("Please set the DIAL_API_KEY environment variable.")
    exit()

def generate_python_function(description: str) -> str:
    """
    Generates a Python function from a natural language description using an LLM.

    This function constructs a few-shot prompt to guide a generative AI model
    to produce only the Python code corresponding to the input description,
    without any surrounding text or markdown formatting.

    Args:
        description: A natural language string describing the function to be created.
                     Example: "Create a Python function named 'calculate_average' that
                     takes a list of numbers and returns their average."

    Returns:
        A string containing only the generated Python code.
        
    Note:
        This function requires a configured generative AI model. For this example,
        we use the 'google.generativeai' library. You would need to set up your
        API key, for instance, as an environment variable 'GOOGLE_API_KEY'.
    """
    
    # In a real application, you would configure the API key.
    # For example: genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    # model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # The prompt is structured with a clear instruction and examples (few-shot)
    # to guide the model's output format. This ensures the output is clean code.
    prompt = f"""
You are an expert Python code generation assistant. Your task is to take a natural language description of a Python function and generate only the corresponding 
Python code.Do not include any explanations, introductory text, comments, or markdown formatting like ```python. Just provide the raw code.

---
**Description:** "Create a Python function named 'add' that takes two numbers, 'a' and 'b', and returns their sum."
**Code:**
def add(a, b):
    \"\"\"
    Takes two numbers, 'a' and 'b', and returns their sum.
    \"\"\"
    return a + b
---
**Description:** "Write a Python function called 'is_palindrome' that checks if a given string is a palindrome. It should be case-insensitive and ignore non-alphanumeric characters."
**Code:**
import re

def is_palindrome(s):
    \"\"\"
    Checks if a given string is a palindrome.
    It is case-insensitive and ignores non-alphanumeric characters.
    \"\"\"
    s_cleaned = re.sub(r'[^a-zA-Z0-9]', '', s).lower()
    return s_cleaned == s_cleaned[::-1]
---
**Description:** "{description}"
**Code:**
"""

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "assistant", "content": prompt}
               
            ],
           
            temperature=0, # Lower temperature for more predictable results
        )
      
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    return "Unable to generate the code now"

# Example of how to use the function:
description_input = "Create a Python function named 'calculate_average' that takes a list of numbers and returns their average."

# Generate the code
generated_code = generate_python_function(description_input)

# The 'generated_code' variable now holds a string containing only the Python function.
# You can then, for example, write it to a file or use `exec()` to make it available.
print(generated_code)

# To demonstrate that the generated code works, we can use exec()
# Note: Using exec() on untrusted code can be a security risk.
# This is for demonstration purposes only.
namespace = {}
exec(generated_code, namespace)
calculate_average_func = namespace['calculate_average']

# Test the dynamically created function
my_numbers = [10, 20, 30, 40, 50]
average = calculate_average_func(my_numbers)
print(f"\\nThe average is: {average}")