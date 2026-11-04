"""Storage package for the deterministic public video catalog.

Importing this package has no side effects. The runnable application imports
``storage.video_catalog`` explicitly, while experimental database and cache
adapters remain local-only.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

__all__ = ["video_catalog"]
