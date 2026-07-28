#!/bin/sh

echo "Waiting for Ollama..."

until curl -fs http://ollama:11434/api/tags > /dev/null; do
    sleep 2
done

echo "Downloading Qwen model if needed..."

curl -X POST http://ollama:11434/api/pull \
-H "Content-Type: application/json" \
-d '{"name":"qwen3:8b"}'

echo "Starting FastAPI..."

uvicorn app.main:app --host 0.0.0.0 --port 8000