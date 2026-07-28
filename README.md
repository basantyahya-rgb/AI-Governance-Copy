# AI Governance

## Requirements

- Docker Desktop

## Clone

git clone https://github.com/basantyahya-rgb/AI-Governance-Copy.git

cd AI-Governance-Copy

## Configure

Copy

backend/.env.example

to

backend/.env

## Run

docker compose up --build

## First Run

If the model is not available:

docker exec -it ollama ollama pull qwen3:8b

## API

http://localhost:8000

Swagger

http://localhost:8000/docs

Health Check

http://localhost:8000/health
