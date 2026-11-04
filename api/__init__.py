"""HTTP boundary for the public Media Content Intelligence service.

Route modules are assembled by :mod:`app.main`; middleware experiments are not
imported automatically, keeping API startup deterministic and dependency-light.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

__all__ = ["routes", "middleware"]
