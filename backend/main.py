from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.upload import router as upload_router
from api.compare import router as compare_router
from api.reports import router as reports_router
from api.ai import router as ai_router

app = FastAPI(title="CTFT - Comparison Tool for Teachers", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(compare_router)
app.include_router(reports_router)
app.include_router(ai_router)


@app.get("/health")
def health():
    return {"status": "ok"}
