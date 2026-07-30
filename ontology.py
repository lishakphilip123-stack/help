"""
Loads the emergency-response ontology (v2, keyword-enriched) and provides
keyword-based retrieval, used as static-FAQ grounding context for the GenAI
model and to populate the scenario quick-reply buttons.

Data source: emergency_ontology_v2.csv
"""

import csv
import os

_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY_PATH = os.path.join(_PROJECT_DIR, "emergency_ontology_v2.csv")

ALL_CATEGORIES_LABEL = "All / Auto-detect"

# Broad terms are categories, not enough detail for safe scenario guidance.
# Specific descriptions (for example, "house fire") still go through normal
# scenario matching and therefore receive immediate, targeted advice.
# Ambiguous terms that could map to multiple subcategories.
# Each entry maps a keyword phrase to a clarifying question + candidate subcategories.
# The bot will ask the clarifying question and present the options as buttons.
DISAMBIGUATION_MAP = [
    {
        "keywords": ["road block", "road blocked", "road closed", "traffic block", "traffic blockage", "road jam", "blocked road"],
        "question": "What is causing the road blockage?",
        "options": [
            {"label": "Rising water / flooding", "category": "Flash Flooding and Infrastructure Failure", "subcategory": "Road or Bridge Washout"},
            {"label": "Landslide or mudslide", "category": "Flash Flooding and Infrastructure Failure", "subcategory": "Landslide or Mudslide"},
            {"label": "Bridge or road collapse", "category": "Utility and Infrastructure Emergency", "subcategory": "Bridge or Road Structural Failure"},
            {"label": "Vehicle accident", "category": "Major Public Transit Disaster", "subcategory": "Major Bus Crash"},
            {"label": "Other / not sure", "category": "Flash Flooding and Infrastructure Failure", "subcategory": "Road or Bridge Washout"},
        ],
    },
    {
        "keywords": ["vehicle drowned", "car drowned", "drowned vehicle", "vehicle sank", "car sank", "vehicle in water", "car in water", "car submerged", "vehicle submerged"],
        "question": "Is this a private vehicle or a public transport vehicle (bus/van with passengers)?",
        "options": [
            {"label": "Private car / small vehicle", "category": "Flash Flooding and Infrastructure Failure", "subcategory": "People or Vehicles Stranded in Water"},
            {"label": "Bus / van with passengers", "category": "Major Public Transit Disaster", "subcategory": "Transit Vehicle in Water"},
        ],
    },
]


def find_disambiguation(query):
    """Return a disambiguation entry if the query matches an ambiguous term."""
    normalized = " ".join(query.casefold().split())
    for entry in DISAMBIGUATION_MAP:
        if any(kw in normalized for kw in entry["keywords"]):
            return entry
    return None


CATEGORY_ALIASES = {
    "flood": "Flash Flooding and Infrastructure Failure",
    "flooding": "Flash Flooding and Infrastructure Failure",
    "fire": "Structural Collapse or Severe Fire",
    "building collapse": "Structural Collapse or Severe Fire",
    "structural collapse": "Structural Collapse or Severe Fire",
    "chemical emergency": "Hazardous Chemical Leak or Toxic Gas Release",
    "chemical leak": "Hazardous Chemical Leak or Toxic Gas Release",
    "toxic gas": "Hazardous Chemical Leak or Toxic Gas Release",
    "transport emergency": "Major Public Transit Disaster",
    "transit disaster": "Major Public Transit Disaster",
    "marine emergency": "Marine and Coastal Emergency",
    "coastal emergency": "Marine and Coastal Emergency",
    "natural disaster": "Natural Disaster",
    "utility emergency": "Utility and Infrastructure Emergency",
    "infrastructure emergency": "Utility and Infrastructure Emergency",
    "mass casualty": "Mass Casualty and Public Safety Incident",
    "public safety incident": "Mass Casualty and Public Safety Incident",
}

# A keyword-phrase match is a much stronger relevance signal than plain word
# overlap with the free-text description, so it's weighted higher.
KEYWORD_MATCH_WEIGHT = 5

# Excluded from word-overlap scoring so common filler words don't create
# false matches (e.g. "the"/"and" coincidentally appearing in a description).
STOPWORDS = {
    "the", "and", "are", "was", "were", "has", "have", "had", "for", "with",
    "from", "that", "this", "into", "near", "over", "your", "you", "its",
    "there", "here", "not", "but", "all", "can", "will", "just", "our",
    "out", "about", "who", "what", "when", "where", "why", "how",
}


def _parse_keywords(raw):
    return [kw.strip().lower() for kw in raw.split(",") if kw.strip()]


def _load_rows():
    if not os.path.exists(ONTOLOGY_PATH):
        return []
    rows = []
    with open(ONTOLOGY_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["_keywords"] = _parse_keywords(row.get("keywords", ""))
            rows.append(row)
    return rows


_ROWS = _load_rows()


def list_categories():
    return sorted({row["category"] for row in _ROWS if row.get("category")})


def get_subcategories(category):
    """Return the subcategories directly related to an ontology category."""
    return sorted({
        row["subcategory"] for row in _ROWS
        if row.get("category", "").casefold() == category.casefold()
    })


def get_scenario(category, subcategory):
    """Return the exact ontology row for a category/subcategory relation."""
    for row in _ROWS:
        if (row.get("category", "").casefold() == category.casefold()
                and row.get("subcategory", "").casefold() == subcategory.casefold()):
            return row
    return None


def find_scenario_in_query(query):
    """Return an explicitly named subcategory before using fuzzy matching."""
    normalized = " ".join(query.casefold().split())
    matches = [
        row for row in _ROWS
        if row.get("subcategory", "").casefold() in normalized
    ]
    return max(matches, key=lambda row: len(row["subcategory"])) if matches else None


def find_keyword_scenario(query, category=None):
    """Return the scenario with the strongest explicit keyword phrase match.

    This is intentionally stricter than fuzzy word overlap.  It prevents a
    vague phrase from being silently assigned to an unrelated ontology row.
    """
    query_normalized = " ".join(query.casefold().split())
    candidates = []
    for row in _ROWS:
        if category and row.get("category") != category:
            continue
        matched_phrases = [phrase for phrase in row.get("_keywords", []) if phrase in query_normalized]
        if matched_phrases:
            candidates.append((max(map(len, matched_phrases)), row))
    return max(candidates, key=lambda item: item[0])[1] if candidates else None


def find_category(query):
    """Return a category for a broad category-only user prompt.

    The full category name may be embedded in a sentence.  Short aliases such
    as ``fire`` and ``flood`` are deliberately accepted only when the input is
    itself a broad category, so a specific report like ``house fire`` is not
    interrupted with an unnecessary clarification.
    """
    normalized = " ".join(query.casefold().split())
    for category in list_categories():
        category_normalized = " ".join(category.casefold().split())
        if normalized == category_normalized:
            return category
        if category_normalized in normalized:
            # A category plus a known subtype is a concrete scenario, not a
            # category-only request; it must proceed to guided follow-ups.
            if any(subcategory.casefold() in normalized for subcategory in get_subcategories(category)):
                continue
            return category
    return CATEGORY_ALIASES.get(normalized)


def find_matches(query, category=None, limit=3):
    """Return the best-matching ontology rows for a free-text query.

    Scoring combines exact keyword-phrase hits (strong signal, from the
    `keywords` column) with plain word overlap against the subcategory and
    description (weaker signal, catches phrasing not covered by keywords).
    """
    query_lower = query.lower()
    query_words = {
        w.strip(".,?!") for w in query_lower.split() if len(w) > 2
    } - STOPWORDS

    scored = []
    for row in _ROWS:
        if category and category != ALL_CATEGORIES_LABEL and row.get("category") != category:
            continue

        score = sum(
            KEYWORD_MATCH_WEIGHT for phrase in row.get("_keywords", []) if phrase in query_lower
        )

        haystack = f"{row.get('subcategory', '')} {row.get('description', '')}".lower()
        score += sum(1 for word in query_words if word in haystack)

        if category and category != ALL_CATEGORIES_LABEL:
            score += 1  # scenario selection alone should still surface its rows

        if score > 0:
            scored.append((score, row))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in scored[:limit]]


def get_escalation_triggers(rows):
    """Return a flat set of escalation trigger keywords from matched rows."""
    triggers = set()
    for row in rows:
        for t in row.get("escalation_triggers", "").split(","):
            t = t.strip().lower()
            if t:
                triggers.add(t)
    return triggers


def get_max_followup(rows):
    """Return the minimum max_followup_questions across matched rows (most urgent wins)."""
    values = []
    for row in rows:
        try:
            values.append(int(row.get("max_followup_questions", 3)))
        except ValueError:
            values.append(3)
    return min(values) if values else 3


def get_cascades(rows):
    """Return ontology rows for any cascading scenarios referenced by matched rows."""
    cascade_names = set()
    for row in rows:
        for name in row.get("cascade_to", "").split(";"):
            name = name.strip()
            if name:
                cascade_names.add(name)
    return [r for r in _ROWS if r.get("subcategory") in cascade_names]


def format_context(rows, cascade_rows=None):
    if not rows:
        return ""

    lines = ["Reference emergency-response data (static ontology):"]
    for row in rows:
        lines.append(
            f"- {row.get('category')} / {row.get('subcategory')}: {row.get('description')} "
            f"| Primary team: {row.get('primary_response_team')} "
            f"| Supporting: {row.get('supporting_response_teams')} "
            f"| Severity: {row.get('default_severity')} "
            f"| Evacuation: {row.get('requires_evacuation')} "
            f"| Primary contact: {row.get('dummy_primary_contact_number', '')} "
            f"| Support contact: {row.get('dummy_support_contact_number', '')} "
            f"| Follow-up questions: {row.get('follow_up_questions', '')} "
            f"| Immediate actions: {row.get('immediate_actions', '')}"
        )
    if cascade_rows:
        lines.append("\nCascading emergency scenarios also apply:")
        for row in cascade_rows:
            lines.append(
                f"- ALSO: {row.get('subcategory')}: "
                f"| Primary team: {row.get('primary_response_team')} "
                f"| Immediate actions: {row.get('immediate_actions', '')}"
            )
    return "\n".join(lines)
