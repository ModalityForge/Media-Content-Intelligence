"""Preprocessing tests."""

import pytest
from components.preprocessing.frame_extractor import FrameExtractor
from components.preprocessing.scene_detector import SceneDetector
from components.preprocessing.ocr_processor import OCRProcessor


def test_frame_extractor_extract_frames():
    """Test frame extraction."""
    extractor = FrameExtractor()
    frames = extractor.extract_frames("video.mp4", interval_seconds=1.0)
    assert len(frames) > 0


def test_scene_detector_detect_scenes():
    """Test scene detection."""
    detector = SceneDetector()
    scenes = detector.detect_scenes("video.mp4")
    assert len(scenes) > 0
    assert "scene_id" in scenes[0]


def test_ocr_processor_process_frame():
    """Test OCR processing."""
    processor = OCRProcessor()
    results = processor.process_frame("frame.jpg")
    assert isinstance(results, list)