from ollama import Client
import os

client = Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))

MODEL = os.getenv("QWEN_MODEL", "qwen3:8b")


def ask_qwen(prompt: str) -> str:
    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]