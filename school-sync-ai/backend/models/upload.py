from pydantic import BaseModel
from typing import Optional


class UploadResponse(BaseModel):
    session_id: str
    school_rows: int
    portal_rows: int
    columns_mapped: list[str]


class CompareResponse(BaseModel):
    matched: int
    missing: int
    modified: int
    new: int


class StatsResponse(BaseModel):
    boys: int
    girls: int
    sc: int
    obc: int
    st: int
    ews: int
    gen: int
    total: int


class ChatRequest(BaseModel):
    session_id: str
    query: str


class ChatResponse(BaseModel):
    query: str
    sql: Optional[str] = None
    result: str


class ReportRequest(BaseModel):
    session_id: str
    format: str = "xlsx"