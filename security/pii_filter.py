"""PII filter for personal information."""

import re
from typing import Any


PII_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
}


class PIIFilter:
    """Filter personally identifiable information."""

    def __init__(self):
        self.patterns = {k: re.compile(v) for k, v in PII_PATTERNS.items()}

    def redact(self, text: str) -> str:
        """Redact PII from text."""
        for name, pattern in self.patterns.items():
            text = pattern.sub(f"[{name.upper()}]", text)
        return text

    def scan(self, text: str) -> dict[str, Any]:
        """Scan for PII."""
        findings = {}
        for name, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                findings[name] = len(matches)
        return findings


pii_filter = PIIFilter()