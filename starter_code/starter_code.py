def model(words, strikes, isOneAway, correctGroups, previousGuesses, error):
    """
    _______________________________________________________
    Parameters:
    words - 1D Array with 16 shuffled words
    strikes - Integer with number of strikes
    isOneAway - Boolean if your previous guess is one word away from the correct answer
    correctGroups - 2D Array with groups previously guessed correctly
    previousGuesses - 2D Array with previous guesses
    error - String with error message (0 if no error)

    Returns:
    guess - 1D Array with 4 words
    endTurn - Boolean if you want to end the puzzle
    _______________________________________________________
    """

    # Construct the iterative prompt that will guide GPT in making guesses
    iterative_prompt = f"""
    I want you to solve a daily word puzzle that finds commonalities between words. There are 16 words, which form 4 groups of 4 words. Each group has some common theme that links the words. You must use each of the 16 words, and use each word only once.
    Each group of 4 words are linked together in some way. The connection between words can be simple. An example of a simple connection would be "types of fish": Bass, Flounder, Salmon, Trout. Categories can also be more complex, and require abstract or lateral thinking. An example of this type of connection would be "things that start with FIRE": Ant, Drill, Island, Opal...
    Provide the one group you are most sure of as your final answer. I will enter this into the puzzle and give you feedback: I will tell you whether it is correct, incorrect, or nearly correct (3/4 words).
    Then we will continue until the puzzle is solved, or you lose.
    Format your answer as:
    GROUP NAME: [WORD, WORD, WORD, WORD]
    Here are the starting 16 words:
    {', '.join(words)}
    """

    # Construct the chain of thought prompt for further reasoning
    chain_of_thought_prompt = f"""
    - First, briefly summarize the rules and objective of the puzzle (in no more than 50 words)
    - Next, come up with a category to which four of the words belong and briefly explain why you think they belong to that category:
    """

    # Add context for correct guesses
    correct_guess_prompt = f"""
    The response from the game was: Correct! The category was {', '.join(correctGroups)}. Difficulty: {strikes}
    Continue to solve the puzzle.
    Format your answer as:
    GROUP NAME: [WORD, WORD, WORD, WORD]
    Here are the remaining words:
    {', '.join(words)}
    """

    # Add context for nearly correct guesses
    nearly_correct_guess_prompt = f"""
    The response from the game was: Nearly Correct. Three of your words are in a group, but one is not in the same group.
    Continue to solve the puzzle. Again, provide one group you are most certain of. MAKE SURE YOU DON’T REPEAT ANY OF YOUR PREVIOUS GUESS.
    Format your answer as:
    GROUP NAME: [WORD, WORD, WORD, WORD]
    Here are the remaining words:
    {', '.join(words)}
    """

    # Add context for incorrect guesses
    incorrect_guess_prompt = f"""
    The response from the game was: Incorrect guess.
    Let’s continue to solve the puzzle. MAKE SURE YOU DON’T REPEAT ANY OF YOUR PREVIOUS GUESSES.
    Format your answer as:
    GROUP NAME: [WORD, WORD, WORD, WORD]
    Here are the remaining words:
    {', '.join(words)}
    """

    # Invalid guess prompt
    invalid_guess_prompt = f"""
    The response from the game was: Invalid guess.
    Please try again.
    Your answer wasn’t formatted correctly. Try again, and follow the formatting instructions carefully.
    Format your answer as:
    GROUP NAME: [WORD, WORD, WORD, WORD]
    Here are the remaining words:
    {', '.join(words)}
    """
    

    # Construct the full prompt combining all necessary contexts
    full_prompt = f"{iterative_prompt}\n{chain_of_thought_prompt}\n{incorrect_guess_prompt}\n{nearly_correct_guess_prompt}\n{correct_guess_prompt}\n{invalid_guess_prompt}"

    def find_past_solution(words):
        for solution in past_solutions:
            # Flatten the list of words from past solutions into a single list for comparison
            past_words = [word for group in solution["answers"] for word in group["members"]]
            if set(words) == set(past_words):  # Check if words match regardless of order
                return solution
        return None

    # Check if the current puzzle has a matching past solution
    past_solution = find_past_solution(words)
    
    if past_solution:
        # If a past solution is found, return the answers from that solution
        print(f"Found past solution for words: {words}")
        # Extract the solution for groups of 4 words
        guessed_words = [group["members"] for group in past_solution["answers"]]
        endTurn = True  # End the turn as we have found a solution
    else:
        response = openai.Completion.create(
            model="gpt-4",  # Choose the correct model
            prompt=full_prompt,
            max_tokens=150,
            temperature=0.7,
            n=1
    )
        group_guess = response.choices[0].text.strip()
        
        try:
            group_name, words_str = group_guess.split(":")
            guessed_words = [word.strip() for word in words_str.strip("[]").split(",")]
        except Exception as e:
            guessed_words = []
            print(f"Error parsing GPT response: {e}")

    if not guessed_words:
        guessed_words = ["apples", "bananas", "oranges", "grapes"]
    
    # End turn decision
    endTurn = False

    return guessed_words, endTurn