import httpx
import asyncio
from typing import Dict, List

ESCO_BASE = "https://ec.europa.eu/esco/api"

_skill_cache: Dict[str, List[str]] = {}
_skill_labels: List[str] = []


async def fetch_esco_skills(limit: int = 500) -> None:
    global _skill_cache, _skill_labels
    print("[ESCO] Fetching skills from ESCO API...")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{ESCO_BASE}/search",
                params={
                    "type": "skill",
                    "language": "en",
                    "limit": limit,
                    "offset": 0,
                    "full": "false",
                },
            )
            response.raise_for_status()
            data = response.json()

        skills = data.get("_embedded", {}).get("results", [])

        cache = {}
        labels = []

        for skill in skills:
            title = skill.get("title", "").strip().lower()
            if not title:
                continue
            key = title.replace(" ", "_").replace("/", "_")
            aliases = [title]

            # add alternate labels if available
            for alt in skill.get("alternativeLabel", {}).get("en", []):
                aliases.append(alt.strip().lower())

            cache[key] = aliases
            labels.append(title)

        _skill_cache = cache
        _skill_labels = labels
        print(f"[ESCO] Loaded {len(_skill_cache)} skills successfully.")

    except Exception as e:
        print(f"[ESCO] Failed to fetch skills: {e}. Falling back to local skill map.")
        _skill_cache = {}
        _skill_labels = []


def get_skill_cache() -> Dict[str, List[str]]:
    return _skill_cache


def get_skill_labels() -> List[str]:
    return _skill_labels


def add_custom_skills(skills: List[str]) -> None:
    """Dynamically add HR-entered skills so they are always matchable."""
    for skill in skills:
        skill = skill.strip().lower()
        if not skill:
            continue
        key = skill.replace(" ", "_").replace("/", "_")
        if key not in _skill_cache:
            _skill_cache[key] = [skill]
            _skill_labels.append(skill)