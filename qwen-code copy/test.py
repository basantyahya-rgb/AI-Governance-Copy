import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "qwen2.5-coder:7b",
    "prompt": "Write a Python hello world",
    "stream": False
}

response = requests.post(url, json=payload)

print(response.json()["response"])