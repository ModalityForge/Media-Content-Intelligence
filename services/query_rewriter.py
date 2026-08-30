"""Query rewriting service."""

import re
from typing import Any


def rewrite_query(query: str) -> str:
    """Rewrite query for better semantic search."""
    rewritten = query

    abbreviations = {
        r"\bAI\b": "Artificial Intelligence",
        r"\bML\b": "Machine Learning",
        r"\bDL\b": "Deep Learning",
        r"\bCV\b": "Computer Vision",
        r"\bNLP\b": "Natural Language Processing",
    }

    for abbr, full in abbreviations.items():
        rewritten = re.sub(abbr, full, rewritten, flags=re.IGNORECASE)

    if "messi" in rewritten.lower():
        rewritten += " Lionel Messi football soccer player"

    if "pepsi" in rewritten.lower():
        rewritten += " beverage brand logo"

    if "adidas" in rewritten.lower() or "nike" in rewritten.lower():
        rewritten += " sports brand logo apparel"

    if "drinking" in rewritten.lower():
        rewritten += " consuming beverage hydration"

    if "germany" in rewritten.lower():
        rewritten += " German territory EU"

    return rewritten


def extract_subqueries(query: str) -> list[str]:
    """Extract subqueries from compound query."""
    subqueries = []

    if " and " in query.lower():
        parts = query.lower().split(" and ")
        subqueries.extend(parts)
    elif " with " in query.lower():
        parts = query.lower().split(" with ")
        subqueries.extend(parts)
    else:
        subqueries.append(query)

    return [s.strip() for s in subqueries if s.strip()]


def extract_filters(query: str) -> dict[str, Any]:
    """Extract filters from query."""
    filters = {}

    if "germany" in query.lower():
        filters["territory"] = "Germany"
    elif "us" in query.lower() or "usa" in query.lower():
        filters["territory"] = "USA"

    if "30-second" in query.lower() or "30s" in query.lower():
        filters["max_duration"] = 30

    brands = re.findall(r"\b(Adidas|Nike|Pepsi|Coke|Apple|Samsung)\b", query, re.IGNORECASE)
    if brands:
        filters["brands"] = list(set(brands))

    return filters


def rewrite_compound_query(query: str) -> dict[str, Any]:
    """Rewrite a compound query."""
    return {
        "rewritten_query": rewrite_query(query),
        "subqueries": extract_subqueries(query),
        "filters": extract_filters(query),
    }