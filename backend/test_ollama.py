from ollama import chat

response = chat(
    model="qwen2.5-coder:7b",
    messages=[
        {
            "role": "user",
            "content": "Write a Python function to reverse a string."
        }
    ]
)

print(response["message"]["content"])