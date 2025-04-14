from src.flow import handle_input

from dotenv import load_dotenv

load_dotenv()

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit", "q"]:
        break

    response = handle_input(user_input)
    print(f"AI: {response['response']}")
