# 1. Variables and basic operations
name = "Gaurav"
age = 25  # adjust to your actual age
print(f"Hello, I'm {name} and I'm {age} years old")

# 2. Lists (arrays)
todos = ["learn Python", "build agent", "deploy it"]
todos.append("get users")
print(f"My todos: {todos}")
print(f"First todo: {todos[0]}")

# 3. Dictionaries (key-value pairs)
user = {
    "name": "Gaurav",
    "role": "builder",
    "excited": True
}
print(f"User info: {user['name']} is a {user['role']}")

# 4. Loops
print("\nAll my todos:")
for todo in todos:
    print(f"- {todo}")

# 5. Functions
def analyze_text(text):
    word_count = len(text.split())
    return f"Your text has {word_count} words"

def count_vowels(text):
    vowels = 'aeiouAEIOU'
    count = sum(1 for char in text if char in vowels)
    return count
vowel_count = count_vowels("This is my first Python function")
print(f"Number of vowels: {vowel_count}")

result = analyze_text("This is my first Python function")
print(result)
for i in range(10):
    print(f"- {i}")
# 6. Conditionals
credits_left = 100
if credits_left > 50:
    print("Plenty of credits!")
elif credits_left > 10:
    print("Running low on credits")
else:
    print("Need to add credits")

# 7. Working with external data
import json

data = {
    "agent": "my first agent",
    "status": "working",
    "calls": 5
}

# Convert to JSON string
json_string = json.dumps(data)
print(f"\nJSON: {json_string}")

# Convert back to Python dict
parsed_data = json.loads(json_string)
print(f"Agent status: {parsed_data['status']}")