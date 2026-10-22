from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from app.core.config import settings


@dataclass(frozen=True)
class QualityReport:
    blur_score: float
    is_blurry: bool
    width: int
    height: int
    is_acceptable: bool
    reason: str | None = None


def _decode(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes")
    return img


def _encode(img: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", img)
    if not ok:
        raise ValueError("Could not encode image")
    return buf.tobytes()


def resize(img: np.ndarray, max_dim: int | None = None) -> np.ndarray:
    max_dim = max_dim or settings.OCR_TARGET_MAX_DIMENSION
    h, w = img.shape[:2]
    scale = max_dim / max(h, w)
    if scale >= 1:
        return img
    return cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)


def correct_brightness(img: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    mean_l = float(np.mean(l))
    if mean_l < 100:
        gain = 100 / max(mean_l, 1)
        l = cv2.convertScaleAbs(l, alpha=min(gain, 2.0), beta=0)
    elif mean_l > 180:
        l = cv2.convertScaleAbs(l, alpha=0.85, beta=0)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)


def enhance_contrast(img: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)


def denoise(img: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoisingColored(img, None, 6, 6, 7, 21)


def sharpen(img: np.ndarray) -> np.ndarray:
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)


def _detect_skew_angle(gray: np.ndarray) -> float:
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
    if lines is None:
        return 0.0
    angles = []
    for line in lines:
        # OpenCV may return either (N, 1, 4) or (N, 4), depending on the
        # installed build.  Normalising each segment avoids a preprocessing
        # crash before OCR can even begin.
        points = np.asarray(line).reshape(-1)
        if points.size != 4:
            continue
        x1, y1, x2, y2 = points
        if x2 - x1 == 0:
            continue
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if -45 < angle < 45:
            angles.append(angle)
    if not angles:
        return 0.0
    return float(np.median(angles))


def deskew(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    angle = _detect_skew_angle(gray)
    if abs(angle) < 0.5:
        return img
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def rotate(img: np.ndarray, degrees: int) -> np.ndarray:
    degrees = degrees % 360
    if degrees == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if degrees == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    if degrees == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img


def blur_score(img: np.ndarray) -> float:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def validate_quality(img: np.ndarray) -> QualityReport:
    h, w = img.shape[:2]
    score = blur_score(img)
    is_blurry = score < settings.OCR_BLUR_THRESHOLD

    if w < 100 or h < 100:
        return QualityReport(score, is_blurry, w, h, False, "Image dimensions too small for OCR")
    if is_blurry:
        return QualityReport(score, is_blurry, w, h, False, "Image is too blurry for reliable OCR")
    return QualityReport(score, is_blurry, w, h, True, None)


# Alias used by ocr_service.py
assess_quality = validate_quality


def decode(image_bytes: bytes) -> np.ndarray:
    return _decode(image_bytes)


def preprocess(image_bytes: bytes) -> tuple[bytes, QualityReport]:
    """Pipeline: decode -> resize -> brightness -> contrast -> denoise -> sharpen -> deskew -> encode."""
    img, quality = preprocess_array(image_bytes)
    return _encode(img), quality


def preprocess_array(image_bytes: bytes) -> tuple[np.ndarray, QualityReport]:
    """Same pipeline as preprocess(), but returns the ndarray directly (no re-encode) - used by OCR engines."""
    img = _decode(image_bytes)
    quality = validate_quality(img)

    img = resize(img)
    img = correct_brightness(img)
    img = enhance_contrast(img)
    img = denoise(img)
    img = sharpen(img)
    img = deskew(img)

    return img, quality
