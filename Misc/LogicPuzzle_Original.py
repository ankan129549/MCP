import openai 
import os
from openai import AzureOpenAI

# --- Configuration ---
# It's recommended to load secrets from environment variables for security
API_KEY = os.getenv("DIAL_API_KEY") 
AZURE_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_VERSION = "2024-02-01"
DEPLOYMENT_NAME = "gpt-4" 

# --- Initialize the client ---
client = None # Initialize client to None
if not API_KEY:
    print("🚨 DIAL API key not found or configured correctly.")
    print("Please set the DIAL_API_KEY environment variable.")
    exit()

try:
    client = AzureOpenAI(
        api_key=API_KEY,
        api_version=API_VERSION,
        azure_endpoint=AZURE_ENDPOINT
    )
    print("✅ Client object created successfully.")
except Exception as e:
    print(f"🔥 Error initializing client object: {e}")
    exit()

def solve_logic_puzzle(puzzle: str) -> str:
    """
    Solves a logic puzzle by providing a clear, step-by-step example to an LLM.

    This function constructs a prompt that first demonstrates how to solve a 
    similar logic puzzle correctly. It then asks the LLM to follow the same 
    reasoning process to find the solution for the user's puzzle.

    Args:
        puzzle: A string containing the logic puzzle to be solved.

    Returns:
        A string containing the model's step-by-step reasoning and the final answer.
    """

    # A clear, correct, and simple logic puzzle is used as a one-shot example.
    # This teaches the model the desired step-by-step reasoning process.
    # The key is to be direct and logical, without showing confusion.
    one_shot_example = """
    Q: "Four colleagues, Alice, Bob, Carol, and Dan, are sitting in a row of four chairs numbered 1 to 4. Alice is sitting directly in front of Bob. Carol is sitting in one of the end chairs (1 or 4). Dan is not sitting next to Carol. What is their seating arrangement from front to back?"

    A: Let's solve this step by step.
    1.  **Analyze the clues:**
        - There are 4 people (Alice, Bob, Carol, Dan) in 4 positions (1, 2, 3, 4).
        - Clue A: Alice and Bob are an adjacent block: (Alice, Bob).
        - Clue B: Carol is in position 1 or 4.
        - Clue C: Dan is not next to Carol.

    2.  **Test the possibilities based on the strongest clue (Carol's position):**
        - **Case 1: Carol is in position 1.** The arrangement is (Carol, _, _, _).
            - Based on Clue C, Dan cannot be in position 2.
            - The (Alice, Bob) block needs two adjacent spots. The only ones available are 3 and 4.
            - This forces Dan into the only remaining spot: position 2.
            - This creates a contradiction: Dan must be in position 2, but he cannot be. So, this case is impossible.

        - **Case 2: Carol is in position 4.** The arrangement is (_, _, _, Carol).
            - Based on Clue C, Dan cannot be in position 3.
            - The (Alice, Bob) block needs two adjacent spots. The available spots are (1, 2) and (2, 3).
            - If we place (Alice, Bob) in (2, 3), Dan must go in position 1. The arrangement is (Dan, Alice, Bob, Carol). Let's check: Dan (1) is not next to Carol (4). All clues fit.
            - If we place (Alice, Bob) in (1, 2), Dan must go in position 3. This contradicts our deduction that Dan cannot be in position 3.

    3.  **Conclusion:** The only valid arrangement is: Dan, Alice, Bob, Carol.
    """

    # The actual prompt that will be sent to the LLM.
    final_prompt = f"""
Follow the example below to solve the logic puzzle. Provide a step-by-step thinking process and then state the final answer.

---
{one_shot_example}
---

Now, solve this puzzle using the same step-by-step thinking. There is only one correct solution.

Q: "{puzzle}"

A:
"""

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
             
               {"role": "system", "content": "You are an expert at solving logic puzzles. You will be given an example of how to solve a puzzle, and then a new puzzle to solve. Follow the reasoning process of the example carefully."},
               # The user message contains the full request
               {"role": "user", "content": final_prompt}
            ],
            temperature=0, # Lower temperature for more deterministic, logical results
        )
      
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    return "Unable to solve the puzzle at this time."

# --- Main Execution ---
if __name__ == '__main__':
  
    user_puzzle = "Four friends, Alex, Ben, Chris, and David, are standing in a line. Chris is not at either end. Ben is directly in front of Alex. " \
    "David is somewhere behind Chris. Determine the order of the friends from front to back."
    
    solution = solve_logic_puzzle(user_puzzle)
    
    print("Logic Puzzle:")
    print(f"> \"{user_puzzle}\"")
    print("\n" + "="*40 + "\n")
    print("🤖 AI's Reasoning and Solution:")
    print(solution)

