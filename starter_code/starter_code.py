import openai

# PROMPT DECLARATIONS
def iterative_prompt(puzzle_words, incorrect_guesses, last_guess):
    # print(puzzle_words)
    last_guess_text = f"This was your last guess, DO NOT REPEAT THESE: {', '.join(last_guess)}" if last_guess else ""
    incorrect_guess_text = f"These are the incorrect guesses, DO NOT REPEAT THESE: {', '.join('[' + ', '.join(guess) + ']' for guess in incorrect_guesses)}" if incorrect_guesses else ""
    prompt = f"""
    I want you to solve a daily word puzzle that finds commonalities between words. There are 16 words, which form 4 groups of 4 words. Each group has some common theme that links the words. You must use each of the 16 words, and use each word only once. Each group of 4 words are linked together in some way. The connection between words can be simple, such as "types of fish": Bass, Flounder, Salmon, Trout. The connections can also be more abstract, like "things that start with FIRE": Ant, Drill, Island, Opal...
    ...Provide the one group you are most sure of as your final answer. I will enter this into the puzzle and give you feedback: I will tell you whether it is correct, incorrect, or nearly correct (3/4 words).
    Then we will continue until the puzzle is solved, or you lose.
    
    Format your answer with no quotes as:
    GROUP NAME: [WORD, WORD, WORD, WORD]

    Some rules:
    - First, briefly summarize the rules and objective of the puzzle (in no more than 50 words).
    - Next, come up with a category to which four of the words belong and briefly explain why you think they belong to that category.
    - Give your final answer in the format described above. Do not add any additional text to your final answer, just the group name and the 4 words.

    Some suggestions:
    - Prioritize making your confident guesses first
    - Make your earlier guesses simpler, safer subjects

    Here are the words you have left:
    {(puzzle_words)}

    {incorrect_guess_text}

    {last_guess_text}
    """
    return prompt

def start_guess_prompt(remaining_words):
    prompt = f"""
    Here are the words you have left:
    {(remaining_words)}
    """
    return prompt

def chain_of_thought_prompt():
    prompt = """
    - First, briefly summarize the rules and objective of the puzzle (in no more than 50 words).
    - Next, come up with a category to which four of the words belong and briefly explain why you think they belong to that category:
    """
    return prompt

def correct_guess_prompt(remaining_words):
    prompt = f"""
    The response from the game from the last guess was: Correct! 
    Continue to solve the puzzle.
    Format your answer with no quotes as:
    GROUP NAME: [WORD, WORD, WORD, WORD]
    Again, here are the remaining words:
    {', '.join(remaining_words)}
    """
    return prompt

def nearly_correct_guess_prompt(remaining_words):
    prompt = f"""
    The response from the game from the last guess was: Nearly Correct. Three of your words are in a group, but one is not in the same group. 
    Continue to solve the puzzle. Again, provide one group you are most certain of. MAKE SURE YOU DON\'T REPEAT ANY OF YOUR PREVIOUS GUESSES.
    Format your answer with no quotes as:
    GROUP NAME: [WORD, WORD, WORD, WORD]
    Again, here are the remaining words:
    {', '.join(remaining_words)}
    """
    return prompt

def incorrect_guess_prompt(remaining_words):
    prompt = f"""
    The response from the game from the last guess was: Incorrect guess. This means ATLEAST TWO WORDS MUST BE CHANGED FROM THE LAST GUESS.
    Let\'s continue to solve the puzzle. MAKE SURE YOU DON\'T REPEAT ANY OF YOUR PREVIOUS GUESSES.
    Format your answer with no quotes as:
    GROUP NAME: [WORD, WORD, WORD, WORD]
    Again, here are the remaining words:
    {', '.join(remaining_words)}
    """
    return prompt

def invalid_guess_prompt(remaining_words):
    prompt = f"""
    The response from the game from the last guess was: Invalid guess. Please try again. Your answer wasn\'t formatted correctly. Try again, and follow the formatting instructions carefully.
    Format your answer with no quotes as:
    GROUP NAME: [WORD, WORD, WORD, WORD]
    Again, here are the remaining words:
    {', '.join(remaining_words)}
    """
    return prompt

# CHATGPT WRAPPER
import openai
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key = 'openrouter_key'
)

openai.api_key = 'key'
def chatgpt_wrapper(prompt, first):
    if(first):
        try:
            # The messages parameter should be a list of message dictionaries
            response = client.chat.completions.create(
                model="openai/o1-preview",  # Or another model you're using
                messages=[
                    {"role": "user", "content": prompt}  # User's prompt
                ],
                max_tokens=1600
            )
            return response
        except client.OpenAIError as e:
            print(f"OpenAI API error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        try:
            # The messages parameter should be a list of message dictionaries
            response = openai.chat.completions.create(
                model="gpt-4o",  # Or another model you're using
                messages=[
                    {"role": "user", "content": prompt}  # User's prompt
                ],
                max_tokens=1600
            )
            return response
        except openai.OpenAIError as e:
            print(f"OpenAI API error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# format response to return an array
def format_response(response):
    print(response.choices[0].message.content)
    # Assuming response is the response object from ChatGPT
    content = response.choices[0].message.content

    # Find the last occurrences of '[' and ']'
    save_answer = content[content.rfind('[') + 1 : content.rfind(']')]

    # print(save_answer)
    save_answer = save_answer.strip("[]").replace(" ", "").split(",")
    return save_answer

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

    # Your Code here
    # Good Luck!
    # print(f'Previous guesses: {previousGuesses}')

    # determine if worth trying again
    first = len(previousGuesses)

    num_correct = len(correctGroups)
    points = {
    0: 0,
    1: 1,
    2: 3,
    3: 6,
    4: 9
    }
    current_points=points.get(num_correct, 0) 
    gain_points=points.get(num_correct+1, 0) 


    multiplier = {
    0: 100,
    1: 90,
    2: 75,
    3: 50,
    4: 25
    }
    current_multiplier=multiplier.get(strikes, 0) 
    loss_multiplier=multiplier.get(strikes+1, 0) 

    MODEL_ACCURACY = 1/3
    potential_loss = current_points * loss_multiplier
    potential_gain = gain_points * current_multiplier
    expected_gain = MODEL_ACCURACY * potential_gain - (1-MODEL_ACCURACY) * potential_loss

    if(expected_gain < 0 and num_correct != 3):
        return [], True
    
    joined_string = ''.join(words)

    # Step 2: Remove brackets and quotes
    cleaned_string = joined_string.replace("[", "").replace("]", "").replace("'", "")

    # Step 3: Split by commas and strip whitespace
    words_list = [word.strip() for word in cleaned_string.split(",")]
    words = words_list

    # Example code where guess is hard
    words_remaining = []
    for word in words:
        # Check if the word is not in any group within correctGroups
        if not any(word in group for group in correctGroups):
            words_remaining.append(word)
    print(words_remaining)
 
    # iterative, correct, nearly correct, incorrect, invalid
    
    # iterative runs every time with words remaining
    # HISTORY REPLACEMENT: context: guesses that are wrong that don't contain a correct group EXCEPT LAST GUESS

    # context: LAST GUESS
    last_guess = []
    prevGuess = previousGuesses[:]
    if(len(prevGuess)):
        # separate last guess and previous guess
        # remove last guess
        last_guess = prevGuess.pop()
        
    # context: incorrect guesses
    incorrectGuesses = []
    for i in range(len(prevGuess)):
        # check if any correct word is in the guess
        guess = prevGuess[i]
        add_guess = True
        for group in correctGroups:
            for word in group:
                if word in guess:
                    add_guess = False
                    break
            if(not add_guess):
                break
        if(add_guess):
            incorrectGuesses.append(guess)

    prompt = iterative_prompt(words_remaining, incorrectGuesses, last_guess)

    # add context from last guess 
    if(last_guess):
        # error
        if error:
            print(f'ERROR: ' + error)
            prompt += invalid_guess_prompt(words_remaining)
            # => prompt error
        # one away
        elif isOneAway:
            prompt += nearly_correct_guess_prompt(words_remaining)
            # => prompt nearly correct
        # correct
        elif (correctGroups and any(set(last_guess) == set(group) for group in correctGroups)):
            prompt += correct_guess_prompt(words_remaining)
            # => prompt correct too
        # incorrect
        else:
            prompt += incorrect_guess_prompt(words_remaining) 
            # => prompt incorrect

    # format response
    print(prompt)
    response = chatgpt_wrapper(prompt, first)
    guess = format_response(response)
    
    endTurn = False
    if(strikes == 4):
        endTurn = True

    return guess, endTurn

# TEST FUNCTION
# group1 = ["TRACE", "RADICAL", "POWER", "TWISTED", 
#           "BENT", "REST", "WARPED", "ROOT", 
#           "LICK", "EXPONENT", "GNARLY", "POWDER", 
#           "OUNCE", "BATH", "SHRED", "THRONE"]
# group1_answers = [
#         {
#             "words": ["BENT", "GNARLY", "TWISTED", "WARPED"],
#             "category": "CONTORTED"
#         },
#         {
#             "words": ["LICK", "OUNCE", "SHRED", "TRACE"],
#             "category": "SMALLEST AMOUNT"
#         },
#         {
#             "words": ["EXPONENT", "POWER", "RADICAL", "ROOT"],
#             "category": "ALGEBRA TERMS"
#         },
#         {
#             "words": ["BATH", "POWDER", "REST", "THRONE"],
#             "category": "WORDS BEFORE “ROOM” TO MEAN LAVATORY"
#         }
#     ]

#words = group1
# word = model(group1, 0, False, [], [], 0)
# print(word)
#for word in group1_answers[0]["words"]:
#    if word in group1:
#        group1.remove(word)

# words strikes oneaway correctgroups previousguesses error
# word = model(group1, 4, False, [group1_answers[0]], [group1_answers[0], ["EXPONENT", "LICK", "OUNCE", "ROOT"], ["EXPONENT", "LICK", "OUNCE", "SHRED"], ["BATH", "POWER", "REST", "EXPONENT"]], False)




    
    
    
    
    # if(error):
    #     print("Error Occurred")
    # elif(len(previousGuesses)): # if there's no previous guesses we use the iterative prompt
    #     prompt = iterative_prompt(words)
    #     response = chatgpt_wrapper(prompt)
    #     formatted_response = format_response(response)
    # if the last item in the previous guess array is = to the last item in correct guess array(and correct>1) - use correct guess prompt
    # elif(previousGuesses[-1] == correctGroups[-1]):
    #     prompt = correct_guess_prompt
    #     response = chatgpt_wrapper(prompt)
    #     formatted_response = format_response(response)
    # elif(isOneAway==True): # nearly correct prompt
    #     prompt = iterative_prompt(words)
    #     response = chatgpt_wrapper(prompt)
    #     formatted_response = format_response(response)

    # elif(correctGroups):
    #     PUZZLE_WORDS = ""
    #     for group in correctGroups:
    #         if group not in words:
    #             PUZZLE_WORDS += ", ".join(group)

    #     prompt = correct_guess_prompt
    #     response = chatgpt_wrapper(prompt)
    # elif()
    

