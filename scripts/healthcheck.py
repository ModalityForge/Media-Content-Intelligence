"""Healthcheck script."""

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