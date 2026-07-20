import json
import re
from google import genai
from config import settings


class GeminiService:
    """Google Gemini AI integration for column mapping, query processing, and diff analysis."""

    def __init__(self):
        self.client = None
        self.model = "gemini-2.5-flash-preview-05-07"
        if settings.ai_api_key:
            self.client = genai.Client(api_key=settings.ai_api_key)

    # ---- Column Mapping ----

    def column_mapping(self, columns: list[str]) -> dict[str, str]:
        """Ask AI to map arbitrary Excel column names to standard fields."""
        if not self.client:
            return self._fallback_mapping(columns)

        prompt = (
            "Map these Excel column names to standard fields: admission_no, student_name, "
            "class_name, gender, category, language. Return ONLY a JSON object like "
            '{"admission_no": "original_col", ...}. Skip unmappable columns.\n\n'
            f"Columns: {columns}"
        )
        return self._parse_json(self._ask(prompt))

    # ---- Query Processing ----

    def normalize_query(self, query_text: str) -> str:
        """Translate/normalize a natural language query to standard English terms."""
        if not self.client:
            return query_text

        prompt = (
            "Normalize this school query to English using standard terms "
            "(boy, girl, SC, ST, OBC, GEN, EWS, class 1-12). "
            "Return only the normalized query.\n\n"
            f"Query: {query_text}"
        )
        return self._ask(prompt).strip()

    def query_to_filter(self, query_text: str, classes: list[str]) -> dict:
        """Convert a natural language query into a structured filter dictionary."""
        if not self.client:
            return {}

        prompt = (
            "Convert this school query into a JSON filter object. "
            f"Available classes: {', '.join(classes)}. "
            'Return like: {"gender": "boy", "category": "SC", "class_name": "6"}. '
            "Skip fields not mentioned. Return ONLY valid JSON.\n\n"
            f"Query: {query_text}"
        )
        return self._parse_json(self._ask(prompt))

    # ---- Report Generation ----

    def generate_report_summary(self, stats: dict) -> str:
        """Generate a natural language summary of report data."""
        if not self.client:
            return "Report generated successfully."

        prompt = (
            "Summarize this school data report in simple English for a teacher:\n"
            f"{stats}"
        )
        return self._ask(prompt).strip()

    # ---- Difference Analysis ----

    def explain_difference(
        self, school_record: dict, portal_record: dict,
        field: str, old_val: str, new_val: str
    ) -> dict:
        """Classify a field change as correction, rename, reclassification, or error."""
        if not self.client:
            return {
                "type": "unknown",
                "explanation": "AI not configured. Manual review needed.",
                "confidence": 0.0,
                "action": "review",
            }

        prompt = (
            "You are a school data reconciliation expert. Analyze this change in a student record.\n\n"
            f"Student: {portal_record.get('student_name', '')} (ID: {portal_record.get('admission_no', '')})\n"
            f"Field changed: {field}\n"
            f"Old value (school record): {old_val}\n"
            f"New value (portal record): {new_val}\n\n"
            "Classify this change into one of:\n"
            "- 'correction': Fixing a data entry error (e.g. spelling fix, wrong class)\n"
            "- 'rename': Student name changed legitimately\n"
            "- 'reclassification': Category/gender changed (possible miscategorization)\n"
            "- 'data_entry_error': Likely someone typed wrong data\n"
            "- 'unknown': Cannot determine\n\n"
            "Return ONLY a JSON object with keys: type, explanation (1 sentence), confidence (0-1), action (accept/skip/review)."
        )

        try:
            result = self._parse_json(self._ask(prompt))
            if isinstance(result, dict) and result.get("type"):
                return result
        except Exception:
            pass

        return {"type": "unknown", "explanation": "Could not analyze.", "confidence": 0.0, "action": "review"}

    # ---- Record Matching ----

    def suggest_best_match(
        self, unmatched_record: dict, candidates: list[dict], top_n: int = 3
    ) -> list[dict]:
        """Find the best matching candidate record for an unmatched student."""
        if not self.client or not candidates:
            return []

        rec = (
            f"Record to match:\n"
            f"  Name: {unmatched_record.get('student_name', '')}\n"
            f"  Class: {unmatched_record.get('class_name', '')}\n"
            f"  Gender: {unmatched_record.get('gender', '')}\n"
            f"  Category: {unmatched_record.get('category', '')}\n"
        )
        cands = "\n".join(
            f"  {i+1}. Name: {c.get('student_name', '')} | Class: {c.get('class_name', '')} "
            f"| Gender: {c.get('gender', '')} | Category: {c.get('category', '')}"
            for i, c in enumerate(candidates[:10])
        )

        prompt = (
            "You are matching student records across two school data sources. "
            "The record below has no exact ID match in the other sheet. "
            "Find the best matches from the candidate list.\n\n"
            f"{rec}\nCandidates:\n{cands}\n\n"
            "Return ONLY a JSON array of objects with keys: candidate_index (0-based), score (0-1), reason (short). "
            f"Sort by score descending. Max {top_n} results."
        )

        try:
            result = self._parse_json(self._ask(prompt), allow_array=True)
            if isinstance(result, list):
                return result
            if isinstance(result, dict) and "matches" in result:
                return result["matches"]
        except Exception:
            pass

        return []

    # ---- Internal Helpers ----

    def _ask(self, prompt: str) -> str:
        """Send a prompt to Gemini and return the response text."""
        response = self.client.models.generate_content(model=self.model, contents=prompt)
        return response.text or ""

    def _fallback_mapping(self, columns: list[str]) -> dict[str, str]:
        """Simple keyword-based column mapping when AI is unavailable."""
        mapping = {}
        for raw in columns:
            lower = raw.strip().lower()
            if any(kw in lower for kw in ("admission", "roll", "id")):
                mapping["admission_no"] = raw
            elif "name" in lower:
                mapping["student_name"] = raw
            elif any(kw in lower for kw in ("class", "grade", "standard")):
                mapping["class_name"] = raw
            elif any(kw in lower for kw in ("gender", "sex")):
                mapping["gender"] = raw
            elif any(kw in lower for kw in ("category", "caste")):
                mapping["category"] = raw
            elif any(kw in lower for kw in ("language", "medium")):
                mapping["language"] = raw
        return mapping

    def _parse_json(self, text: str, allow_array: bool = False) -> dict | list:
        """Extract and parse JSON from AI response text (handles markdown code blocks)."""
        if not text:
            return [] if allow_array else {}

        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
            text = text.strip()

        if allow_array:
            array_match = re.search(r"\[.*\]", text, re.DOTALL)
            if array_match:
                try:
                    return json.loads(array_match.group())
                except json.JSONDecodeError:
                    pass

        obj_match = re.search(r"\{.*\}", text, re.DOTALL)
        if obj_match:
            try:
                return json.loads(obj_match.group())
            except json.JSONDecodeError:
                pass

        return [] if allow_array else {}


gemini_service = GeminiService()
