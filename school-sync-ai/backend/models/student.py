from pydantic import BaseModel
from typing import Optional


class StudentRecord(BaseModel):
    admission_no: str
    student_name: Optional[str] = None
    class_name: Optional[str] = None
    gender: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = None
    source_sheet: str

    class Config:
        from_attributes = True


class ComparisonRow(BaseModel):
    admission_no: str
    student_name: Optional[str] = None
    class_name: Optional[str] = None
    gender: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = None
    difference_type: str

    class Config:
        from_attributes = True