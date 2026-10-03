# AI Governance Platform

AI Governance Platform for prompt validation, risk assessment, PII detection, and secure AI responses.

## Requirements

- Git
- Docker Desktop
- Node.js + npm

## 1. Clone the Project

```bash
git clone https://github.com/basantyahya-rgb/AI-Governance-Copy.git
cd AI-Governance-Copy
```

## 2. Configure the Backend

Copy:

```text
backend/.env.example
```

to:

```text
backend/.env
```

Windows PowerShell:

```powershell
Copy-Item backend/.env.example backend/.env
```

## 3. Run the Backend + Ollama

Make sure Docker Desktop is running.

From the project root:

```bash
docker compose up --build
```

This starts the FastAPI backend and Ollama.

Backend API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

### First Run: Download Qwen

If the model is not available, open another terminal:

```bash
docker exec -it ollama ollama pull qwen3:8b
```

## 4. Run the Frontend

Open a **new terminal**:

```bash
cd AI-Governance-Copy/frontend
```

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

Open the URL shown in the terminal (usually the Vite development URL).

## 5. Run the Whole Project

You need **two terminals**.

### Terminal 1 — Backend

```bash
cd AI-Governance-Copy
docker compose up --build
```

### Terminal 2 — Frontend

```bash
cd AI-Governance-Copy/frontend
npm install
npm run dev
```

Then open the frontend URL shown by Vite.

## 6. Stop the Project

Stop the frontend with:

```text
Ctrl + C
```

Stop the backend with:

```text
Ctrl + C
```

Or:

```bash
docker compose down
```

## Troubleshooting

### Backend is not responding

Open:

```text
http://localhost:8000/health
```

### Qwen model is missing

Run:

```bash
docker exec -it ollama ollama pull qwen3:8b
```

### Frontend dependencies are missing

Run:

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```text
AI-Governance-Copy/
├── backend/
├── frontend/
├── docker-compose.yml
├── Dockerfile
└── README.md
```

> Do not commit `backend/.env`, API keys, passwords, or other secrets to GitHub.
