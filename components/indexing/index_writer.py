"""Index writer component."""

import json
import os
from typing import Any


class IndexWriter:
    """Write indexes to storage."""

    def __init__(self, index_dir: str = "./data/indexes"):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)

    def write_vector_index(self, index_name: str, data: dict[str, Any]) -> None:
        """Write vector index."""
        path = os.path.join(self.index_dir, f"{index_name}_vector.json")
        with open(path, "w") as f:
            json.dump(data, f)

    def write_text_index(self, index_name: str, data: dict[str, Any]) -> None:
        """Write text index."""
        path = os.path.join(self.index_dir, f"{index_name}_bm25.json")
        with open(path, "w") as f:
            json.dump(data, f)


index_writer = IndexWriter()