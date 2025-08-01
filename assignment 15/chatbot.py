# openai library must be installed already
from openai import OpenAI

# IMPORTANT: You should never hardcode the API key inside your code file like here. This is for exercise only.
OPENAI_API_KEY = "aa-1Ah75KXjSa4fUHaU0bLDhc6YETr7lIwhAmBnNamhDiy8j2nD"

# The custom base_url you provided for the translation service
AVALAI_BASE_URL = "https://api.avalai.ir/v1"

client = OpenAI(api_key=OPENAI_API_KEY, base_url=AVALAI_BASE_URL)


# Get initial user input for tone
tone = input("Enter the tone for the conversation (e.g., sarcastically, cheerfully, angrily): ")

if not tone.strip:
    print('An error occurred: empty message !')
    exit()
# TODO: Validate that the tone is not empty; if empty, print an error and exit
# [Hint: Use tone.strip() to check if the input is empty]

# Initialize conversation history with system prompt
prompts = [
    {
        'role': 'system',
        'content': [
            {
                'type': 'text',
                'text': f'Respond {tone}! Keep all replies in this tone.'
            }
        ]
    }
]

    # TODO: Add system prompt to set the tone (e.g., "Respond {tone}!")
    # [Hint: Follow the structure {'role': 'system', 'content': [{'type': 'text', 'text': ...}]}]


# Define exit words
EXIT_WORDS = {"quit", "exit", "stop"}

# Main conversation loop
while True:
    # Get user message
    user_message = input("\nEnter your message (or 'quit', 'exit', or 'stop' to end): ")
    


    # Check for exit condition
    if user_message.lower() in EXIT_WORDS:
         print("Ending conversation.")
         break
    if not user_message.strip:
        print('An error occurred: empty message !')
        break  
        # TODO: Validate that the user message is not empty; if empty, print an error and continue
        # [Hint: Use user_message.strip() to check if the input is empty]

    # Add user message to conversation history

    
    # TODO: add the "user" prompt
    prompts.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_message
                        }
                            ]
                   })
    

    try:


        # TODO: Send request to the API. Use "GPT-4.1-nano" model.
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompts
        )

        # TODO: Extract the AI's response and save it in 'response' variable
        response = response.choices[0].message.content

        # TODO: Append the AI's response to the conversation history as an "assistant" message
        # [Hint: Append a dictionary with role "assistant" and the response content]
        prompts.append({
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": response 
                            }
                                ]
                       })
        # TODO: Print the full conversation history
        # [Hint: Loop through prompts and print each message with its role, e.g., System/User/Assistant]
        for msg in prompts:
            role = msg['role'].capitalize()
            text = msg['content'][0]['text']
            print(f"{role}: {text}")

    except Exception as e:
        print(f"An error occurred: {e}")