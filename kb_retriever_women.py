import json
import os
from typing import List, Dict, Any


def load_women_programs_kb(path: str = "women_programs_kb.json") -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_women_programs(
    kb: List[Dict[str, Any]],
    interests: str = "",
    education_level: str = "",
    category: str | None = None,
) -> List[Dict[str, Any]]:
    interests_lower = (interests or "").lower()
    edu_lower = (education_level or "").lower()

    results: list[tuple[int, Dict[str, Any]]] = []

    for item in kb:
        if category and item.get("category") != category:
            continue

        text = (
            item.get("summary", "")
            + " "
            + item.get("focus", "")
            + " "
            + item.get("good_for", "")
        ).lower()

        score = 0
        for word in interests_lower.split():
            if word in text:
                score += 1

        if edu_lower and edu_lower in text:
            score += 1

        if score > 0:
            results.append((score, item))

    # fallback to show all items in that category even if interests don't match
    if not results and category:
        for item in kb:
            if item.get("category") == category:
                results.append((0, item))

    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results]


def format_women_programs_for_display(programs: List[Dict[str, Any]]) -> str:
    if not programs:
        return (
            "No women-focused opportunities available right now. "
            "You can still ask HerPath Mentor for general guidance."
        )

    lines: list[str] = []

    for p in programs:
        lines.append(f"### {p.get('name')}")
        lines.append(f"**Who it's for:** {p.get('who')}")
        lines.append(f"**Summary:** {p.get('summary')}")
        lines.append(f"**Focus:** {p.get('focus')}")
        lines.append(f"**Activities:** {p.get('activities')}")
        lines.append(f"**Good for:** {p.get('good_for')}")

        if p.get("link"):
            lines.append(f"🔗 [Click here to apply or learn more]({p.get('link')})")

        lines.append("\n---\n")

    return "\n".join(lines)
