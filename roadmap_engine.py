import json
from typing import Any, Dict, List

from college_data import COLLEGES
from ai_client import call_ai_model
from prompts import build_dynamic_roadmap_prompt


def generate_dynamic_roadmap(profile: Dict[str, Any], user_input: str) -> Dict[str, Any] | None:
    """
    Call Groq in JSON mode to generate a structured roadmap object.
    """
    system_prompt = "You are a structured JSON generator for career roadmaps."
    user_prompt = build_dynamic_roadmap_prompt(profile, user_input)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = call_ai_model(messages, response_format="json_object")
    if not isinstance(response, str):
        return None

    try:
        return json.loads(response)
    except Exception:
        # Fallback: try to recover JSON if model added extra text
        try:
            start = response.find("{")
            end = response.rfind("}")
            if start != -1 and end != -1:
                return json.loads(response[start : end + 1])
        except Exception:
            return None
    return None


def get_matching_colleges(roadmap_json: Dict[str, Any]) -> List[dict]:
    matches: List[dict] = []

    if not roadmap_json:
        return matches

    keywords = [k.lower() for k in roadmap_json.get("college_keywords", [])]
    budget = (roadmap_json.get("budget_preference") or "").lower()

    for college in COLLEGES:
        course = college["course"].lower()
        if keywords and not any(keyword in course for keyword in keywords):
            continue

        if budget and college["budget"].lower() != budget:
            continue

        matches.append(college)

    return matches
