# CTFT Comparison Tool for Teachers

AI-powered Excel comparison tool for KV teachers. Compare student records against portal data, generate CBSE/KVS reports, and query data in plain English or Hindi.

## Prerequisites

Before you begin, make sure you have the following installed on your machine:

- **Python 3.13+** — You can check by running `python --version` or `python3 --version`
- **Node.js 18+** — Check with `node -v`. If you don't have it, install from [nodejs.org](https://nodejs.org)
- **(Optional) Google Gemini API key** — Only needed if you want the AI chat and smart column mapping features

## Running Locally

This project has two parts — a **backend** (Python/FastAPI) and a **frontend** (React/Vite). You'll need to run both at the same time in separate terminal windows.

### 1. Clone the repo and open the project

```bash
git clone https://github.com/your-username/CTFT-1.git
cd CTFT-1
```

### 2. Set up the Backend

Open a new terminal and run these commands:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Now create a `.env` file in the project root (the folder that has `backend/` and `frontend/` inside it):

```bash
AI_API_KEY=your_google_gemini_api_key
```

> If you don't have a Gemini API key, you can still use the app — the AI features just won't work.

Start the backend server:

```bash
uvicorn main:app --reload
```

The API will be running at **http://localhost:8000**. You can visit **http://localhost:8000/docs** to see the interactive API docs.

### 3. Set up the Frontend

Open a **second terminal** (keep the backend running in the first one) and run:

```bash
cd frontend
npm install
npm run dev
```

The frontend will start at **http://localhost:5173**. Open that URL in your browser and you're good to go.

### Quick recap — run these in two separate terminals:

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload two Excel/CSV files |
| GET | `/api/sessions` | List recent upload sessions |
| POST | `/api/compare` | Run a comparison |
| GET | `/api/stats/{session_id}` | Get comparison statistics |
| POST | `/api/reports` | Generate CBSE/KVS reports |
| GET | `/api/reports/download/{session_id}` | Download the generated report |
| POST | `/api/chat` | Query data in natural language or Hindi |

## Project Structure

```
shool/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # App settings (API key, upload dirs)
│   ├── requirements.txt
│   ├── api/                 # HTTP route handlers
│   │   ├── upload.py
│   │   ├── compare.py
│   │   ├── reports.py
│   │   └── ai.py
│   ├── services/            # Business logic
│   │   ├── excel_parser.py
│   │   ├── comparator.py
│   │   ├── validator.py
│   │   ├── stats_engine.py
│   │   ├── exporter.py
│   │   └── gemini_service.py
│   └── utils/               # Helpers
│       ├── normalize.py     # Gender/category/language normalization
│       └── fuzzy_match.py   # Fuzzy string matching via RapidFuzz
└── frontend/
    ├── src/
    │   ├── pages/           # Home, Compare, Reports
    │   ├── components/      # UI components (tables, charts, upload, chat)
    │   ├── services/        # API client
    │   └── types/           # TypeScript interfaces
    ├── package.json
    └── vite.config.ts
```

## Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Recharts, TanStack Table, Lucide icons
- **Backend:** FastAPI, Pandas, OpenPyXL, RapidFuzz
- **AI:** Google Gemini 2.5 Flash — column mapping, Hindi normalization, natural language queries

## Deployment

Deployed on Vercel — Python backend via `@vercel/python`, frontend as static build.
