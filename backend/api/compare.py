import os, glob
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import settings
from services.excel_parser import parse_excel
from services.comparator import compare
from services.stats_engine import compute_stats
from services.gemini_service import gemini_service

router = APIRouter(prefix="/api")

UPLOAD_DIR = settings.upload_dir

VALID_EXTENSIONS = (".xlsx", ".xls", ".csv")


def _resolve(session_dir: str, prefix: str) -> str:
    pattern = os.path.join(session_dir, f"{prefix}.*")
    matches = glob.glob(pattern)
    if not matches:
        raise HTTPException(400, f"No file found for '{prefix}' in session")
    return matches[0]


class CompareRequest(BaseModel):
    session_id: str


@router.post("/compare")
async def run_comparison(req: CompareRequest):
    session_dir = os.path.join(UPLOAD_DIR, req.session_id)
    if not os.path.exists(session_dir):
        raise HTTPException(404, "Session not found")

    school_path = _resolve(session_dir, "school")
    portal_path = _resolve(session_dir, "portal")

    school_records = parse_excel(school_path, "school", ai_fallback=gemini_service)
    portal_records = parse_excel(portal_path, "portal", ai_fallback=gemini_service)

    result = compare(school_records, portal_records)

    return result


@router.get("/stats/{session_id}")
def get_stats(session_id: str):
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    if not os.path.exists(session_dir):
        raise HTTPException(404, "Session not found")

    portal_path = _resolve(session_dir, "portal")
    portal_records = parse_excel(portal_path, "portal", ai_fallback=gemini_service)
    stats = compute_stats(portal_records)

    return stats