import os
import glob
from fastapi import HTTPException

VALID_EXTENSIONS = (".xlsx", ".xls", ".csv")


def resolve_file(session_dir: str, prefix: str) -> str:
    """Find a file in the session directory by prefix (e.g., 'school' or 'portal')."""
    matches = glob.glob(os.path.join(session_dir, f"{prefix}.*"))
    if not matches:
        raise HTTPException(400, f"No file found for '{prefix}' in session")
    return matches[0]
