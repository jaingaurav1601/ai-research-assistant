from groq import Groq
import requests
import json
from datetime import datetime

client = Groq(api_key="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")

def search_web(query):
    """Search the web using a free API"""
    # Using DuckDuckGo's instant answer API (free, no key needed)
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # Get abstract or related topics
        result = data.get('AbstractText', '')
        if not result:
            topics = data.get('RelatedTopics', [])
            if topics and 'Text' in topics[0]:
                result = topics[0]['Text']
        
        return result if result else "No results found"
    except:
        return "Search failed"

def calculate(expression):
    """Safely evaluate math expressions"""
    try:
        # Only allow numbers and basic operators
        allowed = "0123456789+-*/(). "
        if all(c in allowed for c in expression):
            result = eval(expression)
            return f"Result: {result}"
        else:
            return "Invalid expression"
    except:
        return "Calculation error"

def get_time(input):
    """Get current time"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Tool definitions
tools = {
    "search": {
        "description": "Search the web for information",
        "function": search_web
    },
    "calculate": {
        "description": "Calculate math expressions",
        "function": calculate
    },
    "time": {
        "description": "Get the current time",
        "function": get_time
    }
}

def agent_with_tools(user_message):
    """Agent that can decide which tool to use"""
    
    # First, ask the LLM what to do
    system_prompt = f"""You are a helpful assistant with access to tools.

Available tools:
- search(query): Search the web
- calculate(expression): Do math calculations
- time(): Get the current time

When the user needs information, respond with: USE_TOOL: search: <query>
When the user needs math, respond with: USE_TOOL: calculate: <expression>
When the user needs the current time, respond with: USE_TOOL: time: <empty>
Otherwise, just answer normally.

Examples:
User: "What is the capital of France?"
You: USE_TOOL: search: capital of France

User: "What's 123 * 456?"
You: USE_TOOL: calculate: 123 * 456

User: "What time is it?"
You: USE_TOOL: time:

User: "How are you?"
You: I'm doing great! How can I help you?"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    
    agent_response = response.choices[0].message.content
    
    # Check if agent wants to use a tool
    if "USE_TOOL:" in agent_response:
        parts = agent_response.split("USE_TOOL:")[1].strip().split(":", 1)
        tool_name = parts[0].strip()
        tool_input = parts[1].strip() if len(parts) > 1 else ""
        
        if tool_name in tools:
            print(f"🔧 Using tool: {tool_name}")
            if tool_name == "time":
                tool_input = ""  # No input needed for time tool
            tool_result = tools[tool_name]["function"](tool_input)
            
            # Send result back to LLM for final answer
            final_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Summarize this information naturally for the user."},
                    {"role": "user", "content": f"User asked: {user_message}\nTool result: {tool_result}"}
                ]
            )
            return final_response.choices[0].message.content
    
    return agent_response

def save_conversation(conversation, filename="conversation.txt"):
    """Save conversation history to a file"""
    with open(filename, "w") as file:
        for message in conversation:
            role = message['role']
            content = message['content']
            file.write(f"{role.upper()}: {content}\n\n")

# Main loop
print("Welcome to the Agent with Tools!")
print("Type 'exit' to end the conversation.")
print("-" * 50)

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
            print("  /help - Show this help message")
            continue
        
        conversation.append({"role": "user", "content": user_input})
        agent_response = agent_with_tools(user_input)
        conversation.append({"role": "assistant", "content": agent_response})
        print(f"Agent: {agent_response}\n")
    
    save_conversation(conversation)
    print("Conversation saved to conversation.txt")

if __name__ == "__main__":
    main()