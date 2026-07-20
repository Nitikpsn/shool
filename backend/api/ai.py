import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import settings
from services.excel_parser import parse_excel
from services.gemini_service import gemini_service
from api.utils import resolve_file

router = APIRouter(prefix="/api")
UPLOAD_DIR = settings.upload_dir


class ChatRequest(BaseModel):
    session_id: str
    query: str


@router.post("/chat")
def ai_chat(req: ChatRequest):
    """Process a natural language query about the uploaded data."""
    session_dir = os.path.join(UPLOAD_DIR, req.session_id)
    if not os.path.exists(session_dir):
        raise HTTPException(404, "Session not found")

    portal_path = resolve_file(session_dir, "portal")
    portal_records = parse_excel(portal_path, "portal", ai_fallback=gemini_service)

    # Normalize the query and extract filters
    normalized = gemini_service.normalize_query(req.query)
    classes = sorted(set(r["class_name"] for r in portal_records if r.get("class_name")))
    filter_dict = gemini_service.query_to_filter(req.query, classes)

    # Apply filters to portal records
    filtered = _apply_filters(portal_records, filter_dict)

    return {
        "original_query": req.query,
        "normalized_query": normalized,
        "filter_applied": filter_dict,
        "total_records": len(filtered),
        "records": filtered[:50],
    }


def _apply_filters(records: list[dict], filters: dict) -> list[dict]:
    """Filter records by gender, category, and/or class."""
    result = records
    if filters.get("gender"):
        result = [r for r in result if r.get("gender", "").lower() == filters["gender"].lower()]
    if filters.get("category"):
        result = [r for r in result if r.get("category", "").upper() == filters["category"].upper()]
    if filters.get("class_name"):
        result = [r for r in result if r.get("class_name", "") == str(filters["class_name"])]
    return result
