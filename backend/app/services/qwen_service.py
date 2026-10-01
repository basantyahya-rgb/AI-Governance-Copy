"""Local Ollama/Qwen service with lightweight inference settings."""

import os

from ollama import Client


HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434",
)


MODEL = os.getenv(
    "QWEN_MODEL",
    "qwen3:8b",
)


KEEP_ALIVE = os.getenv(
    "OLLAMA_KEEP_ALIVE",
    "30m",
)


NUM_PREDICT = int(
    os.getenv(
        "QWEN_NUM_PREDICT",
        "384",
    )
)


client = Client(
    host=HOST
)


def ask_qwen(prompt: str) -> str:

    kwargs = {

        "model": MODEL,

        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],

        "keep_alive": KEEP_ALIVE,

        "options": {

            "num_predict": NUM_PREDICT,

            "temperature": 0.2,
        },
    }

    # Qwen3 thinking control.
    # Compatibility fallback for older
    # Ollama Python clients.

    try:

        response = client.chat(
            **kwargs,
            think=False,
        )

    except TypeError:

        response = client.chat(
            **kwargs
        )

    return response[
        "message"
    ][
        "content"
    ]