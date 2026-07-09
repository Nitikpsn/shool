import os, uuid
from fastapi import APIRouter, UploadFile, File
from app.config import settings
from services.excel_parser import parse_excel
from services.validator import validate_records

router = APIRouter(prefix="/api")

UPLOAD_DIR = settings.upload_dir
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    path1 = os.path.join(session_dir, file1.filename or "school.xlsx")
    path2 = os.path.join(session_dir, file2.filename or "portal.xlsx")

    with open(path1, "wb") as f:
        f.write(await file1.read())
    with open(path2, "wb") as f:
        f.write(await file2.read())

    school_records = parse_excel(path1, "school")
    portal_records = parse_excel(path2, "portal")

    errors = validate_records(school_records) + validate_records(portal_records)

    return {
        "session_id": session_id,
        "school_rows": len(school_records),
        "portal_rows": len(portal_records),
        "columns_mapped": list(school_records[0].keys()) if school_records else [],
        "errors": errors,
        "school_sample": school_records[:3] if school_records else [],
        "portal_sample": portal_records[:3] if portal_records else [],
    }