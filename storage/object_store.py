"""Object storage."""

import os
from typing import Any


class ObjectStore:
    """Local file object storage."""

    def __init__(self, base_path: str = "./data/raw"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def put(self, key: str, data: bytes) -> None:
        """Store object."""
        path = os.path.join(self.base_path, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)

    def get(self, key: str) -> bytes | None:
        """Get object."""
        path = os.path.join(self.base_path, key)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f.read()
        return None

    def delete(self, key: str) -> None:
        """Delete object."""
        path = os.path.join(self.base_path, key)
        if os.path.exists(path):
            os.remove(path)


object_store = ObjectStore()