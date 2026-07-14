# CTFT Comparison Tool for Teachers

AI-powered Excel comparison tool for KV teachers. Compare student records against portal data, generate CBSE/KVS reports, and query data in plain English or Hindi.

## Prerequisites

- Python 3.13+
- Node.js 18+
- (Optional) Google Gemini API key for AI features

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Create a `.env` file in the project root (next to `backend/`) with your key:

```bash
AI_API_KEY=your_google_gemini_api_key
```

The `.env` file is in `.gitignore` and will not be committed.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

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
