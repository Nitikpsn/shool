from pydantic import BaseModel
from typing import Optional


class ReportData(BaseModel):
    class_wise: dict
    category_wise: dict
    gender_wise: dict
    language_wise: dict
    missing_records: list
    mismatch_report: list