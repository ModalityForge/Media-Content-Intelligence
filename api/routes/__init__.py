"""Route modules shipped in the public MCI application.

Only implemented, demonstrable routes are exported. Placeholder ingestion,
clip-generation, and alert routes remain local and are intentionally excluded
from the public application contract.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from api.routes import feedback, health, search, videos

__all__ = ["feedback", "health", "search", "videos"]
