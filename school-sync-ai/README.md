# School Sync AI

Excel comparison tool for schools. Compare school.xlsx vs portal.xlsx, generate CBSE/KVS reports, and query data using natural language or Hindi.

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
# Set AI_API_KEY in ../.env for AI features
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database

```sql
mysql -u root -p < backend/database/schema.sql
```

## API Endpoints

- `POST /api/upload` — Upload two Excel files
- `POST /api/compare` — Run comparison
- `GET /api/stats/{session_id}` — Get statistics
- `POST /api/reports` — Generate CBSE/KVS report
- `POST /api/chat` — Natural language query

## Tech Stack

Frontend: React, TypeScript, Vite, Tailwind CSS, Recharts, TanStack Table
Backend: FastAPI, Pandas, OpenPyXL, RapidFuzz
AI: Gemini 2.5 Flash (column mapping, Hindi normalization, NL queries)

## Deployment

- Frontend → Vercel
- Backend → Railway / Render / Fly.io