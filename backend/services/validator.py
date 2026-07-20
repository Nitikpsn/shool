from typing import Any


def validate_records(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Check each record for required fields and return any errors found."""
    errors = []
    for i, record in enumerate(records):
        adm = record.get("admission_no", "")
        name = record.get("student_name", "")

        if not adm:
            errors.append({"row": i + 1, "field": "admission_no", "message": "Missing admission number"})
        elif len(str(adm)) > 30:
            errors.append({"row": i + 1, "field": "admission_no", "message": "Admission number too long"})

        if not name:
            errors.append({"row": i + 1, "field": "student_name", "message": "Missing student name"})

    return errors


def validate_columns(columns: list[str]) -> list[str]:
    """Check if column headers suggest required fields are present."""
    lower_cols = [c.strip().lower() for c in columns]
    required_hints = ["admission", "name"]
    return [hint for hint in required_hints if not any(hint in c for c in lower_cols)]
