# AI Governance Frontend

Responsive React + Vite frontend for the AI Governance Platform.

## Run

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api/*` to `http://127.0.0.1:8000`.

Start the FastAPI backend separately:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Production / separate backend

Set `VITE_API_BASE_URL` in `.env` to the public backend origin, for example:

```env
VITE_API_BASE_URL=https://api.example.com
```

Then build:

```bash
npm run build
```
