"""Index archive script."""


def index_archive(video_path: str):
    """Index a video archive."""
    print(f"Indexing archive: {video_path}")
    print("Mock indexing complete")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        index_archive(sys.argv[1])
    else:
        print("Usage: python index_archive.py <video_path>")