import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Brev API credentials from environment
BREV_ID = os.getenv("BREV_ID")
BREV_SECRET = os.getenv("BREV_SECRET")
MODEL_ENDPOINT = "https://jupyter0-4lqfzd4hk.brevlab.com/v1/models/Connections2-llama3-8b-finetuned/generate"

# Define headers for authentication
headers = {
    "CF-Access-Client-Id": BREV_ID,
    "CF-Access-Client-Secret": BREV_SECRET,
    "Content-Type": "application/json"
}

# Function to construct the prompt for each attempt
def iterative_prompt(puzzle_words, incorrect_guesses, last_guess):
    last_guess_text = f"This was your last guess, DO NOT REPEAT THESE: {', '.join(last_guess)}" if last_guess else ""
    incorrect_guess_text = f"These are the incorrect guesses, DO NOT REPEAT THESE: {', '.join(['[' + ', '.join(guess) + ']' for guess in incorrect_guesses])}" if incorrect_guesses else ""
    
    prompt = f"""
    I want you to solve a daily word puzzle that finds commonalities between words. There are 16 words, which form 4 groups of 4 words. Each group has some common theme that links the words. You must use each of the 16 words, and use each word only once. Each group of 4 words are linked together in some way. The connection between words can be simple, such as "types of fish": Bass, Flounder, Salmon, Trout. The connections can also be more abstract, like "things that start with FIRE": Ant, Drill, Island, Opal...
    {last_guess_text}
    {incorrect_guess_text}
    Given these constraints, please identify one group of 4 words from this list:
    {', '.join(puzzle_words)}
    """
    
    return prompt.strip()

# Function to query the model using the Brev API
def query_model(prompt):
    payload = {
        "prompt": prompt,
        "max_tokens": 200,  # Adjust as needed
        "temperature": 0.7  # Adjust for desired randomness
    }
    
    # Make a POST request to the Brev API with the prompt payload
    response = requests.post(MODEL_ENDPOINT, headers=headers, json=payload)
    
    # Check if the request was successful and retrieve the generated response
    if response.status_code == 200:
        response_data = response.json()
        generated_text = response_data.get("text", "")  # Adjust based on actual response format
        return generated_text
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Main function to execute the iterative prompting
def main():
    puzzle_words = ["sports", "practice", "bike", "straw", "pipe", "drill", "ticket", "hose", "knife", "wrench", "candlestick", "tube", "study", "cigarette", "train", "rope"]
    incorrect_guesses = []
    last_guess = []
    
    # Maximum number of attempts to solve the puzzle
    max_attempts = 5
    for attempt in range(max_attempts):
        prompt = iterative_prompt(puzzle_words, incorrect_guesses, last_guess)
        response_text = query_model(prompt)
        
        if response_text:
            print(f"Attempt {attempt + 1}:\n{response_text}\n")
            # Update guesses based on the response (parse as needed)
