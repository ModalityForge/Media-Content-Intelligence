"""Generate deterministic HyDE-style text for catalog retrieval.

The public implementation expands a query into an idealized media description
without calling a private language model. The result gives retrieval code a
richer textual representation while remaining reproducible offline.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from typing import Any


def generate_hyde(query: str) -> str:
    """Generate a hypothetical ideal document for the query.

    This creates a description of an ideal matching video clip
    that can be embedded and used for retrieval.
    """
    hyde_paragraph = f"A video clip that shows "

    if "messi" in query.lower() or "ronaldo" in query.lower():
        hyde_paragraph += "a famous football player "

        if "pepsi" in query.lower():
            hyde_paragraph += "drinking from a Pepsi bottle with visible branding, "
        if "adidas" in query.lower():
            hyde_paragraph += "wearing Adidas jersey with the logo clearly visible, "

    elif "lebron" in query.lower():
        hyde_paragraph += "LeBron James basketball player "

        if "pepsi" in query.lower():
            hyde_paragraph += "holding a Pepsi product, "

    else:
        hyde_paragraph += "the subject performing the described action "

    if "drinking" in query.lower():
        hyde_paragraph += "in the act of consuming a beverage, "

    if "celebrating" in query.lower():
        hyde_paragraph += "celebrating or showing emotion after a key moment, "

    if "scoring" in query.lower():
        hyde_paragraph += "scoring a goal or making a successful play, "

    hyde_paragraph += "with clear visibility of any brand logos, "
    hyde_paragraph += "suitable for broadcast or digital use, "
    hyde_paragraph += "with proper rights clearance for the specified territory."

    if "germany" in query.lower():
        hyde_paragraph += " Specifically cleared for German digital highlights usage."

    if "30-second" in query.lower() or "30s" in query.lower():
        hyde_paragraph += " Limited to 30 seconds duration."

    return hyde_paragraph


def generate_hyde_from_intent(intent: dict[str, Any]) -> str:
    """Generate HyDE from parsed intent."""
    query = intent.get("query", "")
    return generate_hyde(query)
