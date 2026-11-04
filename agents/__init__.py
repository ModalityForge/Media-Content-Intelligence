"""Public agent package for the MCI orchestration runtime.

The package initializer deliberately avoids importing concrete agent modules.
Callers import the orchestrator, validator, protocol, or state from their
own modules so importing :mod:`agents` cannot pull local-only experimental
graphs into a clean public installation.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

__all__ = ["a2a_protocol", "evidence_validator", "media_orchestrator", "state"]
