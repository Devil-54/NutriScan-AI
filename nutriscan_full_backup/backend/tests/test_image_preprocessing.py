from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFilter

from app.infrastructure.ocr.image_preprocessor import (
    correct_brightness,
    deskew,
    enhance_contrast,
    preprocess_array,
    resize,
    rotate,
    sharpen,
    validate_quality,
)


def _sharp_text_image_bytes(w=800, h=400) -> bytes:
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    for y in range(20, h - 20, 30):
        draw.line([(20, y), (w - 20, y + 5)], fill=(0, 0, 0), width=4)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _blurry_image_bytes(w=800, h=400) -> bytes:
    img = Image.new("RGB", (w, h), color=(200, 200, 200))
    img = img.filter(ImageFilter.GaussianBlur(radius=15))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _to_ndarray(image_bytes: bytes) -> np.ndarray:
    import cv2

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


class TestBlurDetection:
    def test_sharp_image_not_blurry(self) -> None:
        img = _to_ndarray(_sharp_text_image_bytes())
        report = validate_quality(img)
        assert report.is_blurry is False
        assert report.is_acceptable is True

    def test_blurry_image_detected(self) -> None:
        img = _to_ndarray(_blurry_image_bytes())
        report = validate_quality(img)
        assert report.is_blurry is True
        assert report.is_acceptable is False
        assert "blurry" in (report.reason or "").lower()


class TestQualityValidation:
    def test_tiny_image_rejected(self) -> None:
        img = _to_ndarray(_sharp_text_image_bytes(w=50, h=50))
        report = validate_quality(img)
        assert report.is_acceptable is False
        assert "small" in (report.reason or "").lower()


class TestPreprocessingSteps:
    def test_resize_shrinks_large_image(self) -> None:
        img = _to_ndarray(_sharp_text_image_bytes(w=3000, h=1500))
        resized = resize(img, max_dim=1000)
        assert max(resized.shape[:2]) <= 1000

    def test_resize_leaves_small_image_unchanged(self) -> None:
        img = _to_ndarray(_sharp_text_image_bytes(w=400, h=200))
        resized = resize(img, max_dim=1000)
        assert resized.shape == img.shape

    def test_brightness_correction_runs(self) -> None:
        img = _to_ndarray(_sharp_text_image_bytes())
        out = correct_brightness(img)
        assert out.shape == img.shape

    def test_contrast_enhancement_runs(self) -> None:
        img = _to_ndarray(_sharp_text_image_bytes())
        out = enhance_contrast(img)
        assert out.shape == img.shape

    def test_sharpen_runs(self) -> None:
        img = _to_ndarray(_sharp_text_image_bytes())
        out = sharpen(img)
        assert out.shape == img.shape

    def test_deskew_runs_without_error(self) -> None:
        img = _to_ndarray(_sharp_text_image_bytes())
        out = deskew(img)
        assert out.shape == img.shape

    def test_rotate_90(self) -> None:
        img = _to_ndarray(_sharp_text_image_bytes(w=400, h=200))
        out = rotate(img, 90)
        assert out.shape[0] == img.shape[1]
        assert out.shape[1] == img.shape[0]

    def test_rotate_0_is_noop(self) -> None:
        img = _to_ndarray(_sharp_text_image_bytes())
        out = rotate(img, 0)
        assert out.shape == img.shape


class TestFullPipeline:
    def test_preprocess_array_returns_ndarray_and_quality(self) -> None:
        img, quality = preprocess_array(_sharp_text_image_bytes())
        assert isinstance(img, np.ndarray)
        assert quality.width > 0 and quality.height > 0

    def test_preprocess_array_raises_on_invalid_bytes(self) -> None:
        with pytest.raises(ValueError):
            preprocess_array(b"not-an-image")
