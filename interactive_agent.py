from groq import Groq

client = Groq(api_key="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")

def chat_with_agent(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that gives concise answers."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def save_conversation(conversation, filename="conversation.txt"):
    with open(filename, "w") as file:
        for message in conversation:
            role = message['role']
            content = message['content']
            file.write(f"{role.upper()}: {content}\n\n")

print("Welcome to the Chat Agent!")
print("Type 'exit' to end the conversation.")
print( '-' * 40 )

def main():
    conversation = []
    while True:
        user_input = input("You: ")

        if user_input.lower() == 'exit':
            break
        elif user_input.strip() == '':
            print("Please enter a message.")
            continue
        elif user_input.lower() == 'save':
            save_conversation(conversation)
            print("Conversation saved to conversation.txt")
            continue
        elif user_input.lower() == 'clear':
            conversation = []
            print("Conversation cleared.")
            continue
        elif user_input.lower() == '/help':
            print("Available commands:")
            print("  exit  - End the conversation")
            print("  save  - Save the conversation to a file")
            print("  clear - Clear the current conversation")
            print("  help  - Show this help message")
            continue
        conversation.append({"role": "user", "content": user_input})
        agent_response = chat_with_agent(user_input)
        conversation.append({"role": "assistant", "content": agent_response})
        print(f"Agent: {agent_response}\n")
    save_conversation(conversation)
    print("Conversation saved to conversation.txt")

main()