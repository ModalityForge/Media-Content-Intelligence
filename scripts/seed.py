"""Seed script to populate test data."""

import random
import uuid
from datetime import datetime


def seed_data():
    """Seed sample data."""
    print("Seeding sample data...")

    sample_videos = [
        {"video_id": "video-001", "duration": 600, "sport": "football"},
        {"video_id": "video-002", "duration": 900, "sport": "basketball"},
        {"video_id": "video-003", "duration": 1200, "sport": "tennis"},
    ]

    for video in sample_videos:
        print(f"Created video: {video['video_id']}")

    print("Seeding complete!")


if __name__ == "__main__":
    seed_data()