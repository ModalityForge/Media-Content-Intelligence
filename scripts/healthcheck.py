"""Command-line health probe for the locally running public MCI API.

The script requests the aggregate health endpoint with a bounded timeout and
maps the outcome to a boolean and process exit status suitable for containers,
deployment probes, and local smoke verification.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

import httpx
import sys


def healthcheck(url: str = "http://localhost:8000/health") -> bool:
    """Check service health."""
    try:
        response = httpx.get(url, timeout=5.0)
        if response.status_code == 200:
            print(f"Service is healthy: {response.json()}")
            return True
    except Exception as e:
        print(f"Health check failed: {e}")
    return False


if __name__ == "__main__":
    sys.exit(0 if healthcheck() else 1)
