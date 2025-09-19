import openai 
import os
from openai import AzureOpenAI

  # --- Configuration ---
API_KEY = os.getenv("DIAL_API_KEY") 
AZURE_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_VERSION = "2024-02-01"
DEPLOYMENT_NAME = "deepseek-r1" 
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

def solve_logic_puzzle(puzzle: str) -> str:
    """
    Solves a logic puzzle by generating a Chain of Thought prompt for an LLM.

    This function constructs a detailed prompt that first demonstrates how to solve
    a similar, but different, logic puzzle step-by-step. It then presents the
    user's puzzle and asks the LLM to follow the same reasoning process to find
    the solution.

    Args:
        puzzle: A string containing the logic puzzle to be solved.

    Returns:
        A string representing the final order of the friends from front to back.
    """

    # A different logic puzzle is used as a one-shot example for the LLM.
    # This teaches the model the desired reasoning process (Chain of Thought).
    cot_example_prompt = """
    Q: "Four colleagues, Alice, Bob, Carol, and Dan, are sitting in a row of four chairs. Alice is sitting directly infront  of Bob. Carol is sitting in one of the end chairs. Dan is not sitting next to Carol. What is their seating arrangement?"

    A: Let's solve this step by step.
    1.  **Identify the entities and the setup.** We have four people (Alice, Bob, Carol, Dan) and four positions in a row, which we can label 1, 2, 3, and 4.
    2.  **Analyze each clue:**
        * Clue 1: "Alice is sitting directly in front  of Bob." This means they form an adjacent block, 
        like (Alice, Bob).
        * Clue 2: "Carol is sitting in one of the end chairs." This places Carol in position 1 or position 4.
        * Clue 3: "Dan is not sitting next to Carol." This is a constraint we'll use to validate our hypotheses.
    3.  **Formulate and test hypotheses based on the strongest clue (Carol's position).**
        * **Hypothesis A: Carol is in position 1.**
            * If Carol is in 1, then from Clue 3, Dan cannot be in position 2.
            * The (Alice, Bob) block needs two adjacent seats. The only available adjacent pair is (3, 4).
            * This would force Dan into the only remaining seat, position 2.
            * This creates a contradiction: Dan must be in position 2, but he cannot be. Therefore, Hypothesis A is incorrect.
        * **Hypothesis B: Carol is in position 4.**
            * If Carol is in 4, then from Clue 3, Dan cannot be in position 3.
            * The (Alice, Bob) block needs two adjacent seats. The only available adjacent pair is (1, 2).
            * This leaves position 3 for Dan.
            * This contradicts our deduction that Dan cannot be in position 3. Let me re-evaluate. Ah, if Dan is in position 3 and Carol is in 4, they are next to each other. So Dan cannot be in 3. This hypothesis is also incorrect.

    Let me retrace my logic carefully. I seem to have made a mistake.

    **Corrected Reasoning:**
    1.  Setup: 4 chairs (1, 2, 3, 4), 4 people (A, B, C, D).
    2.  Clues: (A,B) block. C is in 1 or 4. D is not next to C.
    3.  Hypotheses revisited:
        * **Case 1: Carol in chair 1.** Dan cannot be in chair 2. The (A,B) block may occupy chairs 3 and 4. This leaves chair 2 for Dan. This is a contradiction. Case 1 is impossible.
        * **Case 2: Carol in chair 1.** Dan cannot be in chair 2. The (A,B) block may occupy chairs 2 and 3. This leaves chair 4 for Dan. This is a possible solution.
        * **Case 3: Carol in chair 4.** Dan cannot be in chair 3. The (A,B) block may occupy chairs 1 and 2. This leaves chair 3 for Dan. This is a contradiction.
        * **Case 4: Carol in chair 4.** Dan cannot be in chair 3. The (A,B) block may occupy chairs 2 and 3. This leaves chair 1 for Dan. This is a possible solution.
    4. Validate : 
        * **Alice Should be ahead and Adjacent to Bob. so Alice at 1 and Bob at 3 or 4 is an incorrect combination.

    I must have an error in my understanding. Let's re-read the puzzle. "Dan is not sitting next to Carol."
     Let's try again.

    **Third Attempt at Reasoning:**
    1. Setup: Chairs 1, 2, 3, 4. People: Alice, Bob, Carol, Dan.
    2. Clues:
       - {Alice, Bob} are adjacent. if Alice is at 1, Bob has to be at 2. If Alice is at 2, Bob has to be at 3. if Alice is at 1, Bob can not be at 4, as they would not be adjacent then.
       - Carol is in chair 1 or 4.
       - Dan is NOT next to Carol.
    3. Test cases based on Carol's position:
       - **Scenario 1: Carol is in chair 1.**
         - Dan cannot be in chair 2.
         - The remaining chairs are 2, 3, 4.
         - Alice & Bob must sit together, so they take chairs (3 and 4) or (2 and 3).
         - When Alice & Bob sit on chairs (3 and 4) then This leaves chair 2 for Dan.
         - This contradicts "Dan cannot be in chair 2". So, this scenario is impossible. 
         - When Alice & Bob sit on chairs (2 and 3) then This leaves chair 1 for Dan. This is a possible solution.
       - **Scenario 2: Carol is in chair 4.**
         - Dan cannot be in chair 3.
         - The remaining chairs are 1, 2, 3.
         - Alice & Bob must sit together, so they take chairs (1 and 2) or (2 and 3).
         - When Alice & Bob sit on chairs (1 and 2), This leaves chair 3 for Dan.
         - This contradicts "Dan cannot be in chair 3".
         - When Alice & Bob sit on chairs (2 and 3), This leaves chair 1 for Dan. This is a possible solution.
    4.  Validate:
    
         - Alice Should be ahead and Adjacent to Bob. so Alice at 1 and Bob at 3 or 4 is an incorrect combination.

    
   
    """

    # The actual prompt that will be sent to the LLM. It combines the CoT example
    # with the new puzzle provided by the user.
    final_prompt = f"""
Follow the example below to solve the logic puzzle.

{cot_example_prompt}

---
Now, solve this puzzle using the same step-by-step thinking: Please consider only one solution. 

Q: "{puzzle}"

A:
"""


    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
               #{"role": "system", "content": cot_example_prompt},
                {"role": "user", "content": final_prompt}
                #{"role": "user", "content": puzzle}
            ],
           
            temperature=0, # Lower temperature for more predictable results
        )
      
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    return "Unable to solve the puzzle now"

# --- Main Execution ---
if __name__ == '__main__':
  
    user_puzzle = "Four friends, Alex, Ben, Chris, and David, are standing in a line. Chris is not at either end. Ben is directly in front of Alex. " \
    "David is somewhere behind Chris. Determine the order of the friends from front to back."
    
    final_order = solve_logic_puzzle(user_puzzle)
    
    print("Logic Puzzle:")
    print(f"> \"{user_puzzle}\"")
    print("\n" + "="*40 + "\n")
    print(f"🧑‍🤝‍🧑 The final order from front to back is: \n   **{final_order}**")