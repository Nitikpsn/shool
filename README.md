# School Sync AI

An AI-powered Excel comparison tool for schools. Compare school records against portal data, generate CBSE and KVS reports, and query your data in plain English or Hindi.

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Make sure to set `AI_API_KEY` in `.env` to enable AI features.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database

```bash
mysql -u root -p < backend/database/schema.sql
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload two Excel files |
| POST | `/api/compare` | Run a comparison |
| GET | `/api/stats/{session_id}` | Get comparison stats |
| POST | `/api/reports` | Generate CBSE/KVS reports |
| POST | `/api/chat` | Ask questions in natural language |

## Tech Stack

- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Recharts, TanStack Table
- **Backend:** FastAPI, Pandas, OpenPyXL, RapidFuzz
- **AI:** Gemini 2.5 Flash — handles column mapping, Hindi normalization, and natural language queries

## Deployment

- Frontend → [Vercel](https://vercel.com)
