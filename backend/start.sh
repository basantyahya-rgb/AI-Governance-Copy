#!/bin/sh

echo "======================================"
echo "Starting AI Governance Backend..."
echo "======================================"

echo "Waiting for Ollama..."

until curl -s http://ollama:11434/api/tags >/dev/null
do
    echo "Ollama is not ready..."
    sleep 2
done

echo "Ollama is ready."

MODEL=${QWEN_MODEL:-qwen3:8b}

echo "Checking model: $MODEL"

if ! curl -s http://ollama:11434/api/tags | grep -q "\"$MODEL\""; then
    echo "Downloading model $MODEL ..."
    curl http://ollama:11434/api/pull \
        -d "{\"name\":\"$MODEL\"}"
fi

echo "Starting FastAPI..."

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000