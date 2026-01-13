from groq import Groq

client = Groq(api_key="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")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Say hello and tell me a joke!"}
    ]
)

print(response.choices[0].message.content)