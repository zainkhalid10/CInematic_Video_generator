"""
phase5_edit/filters.py
========================
OpenCV image filters for visual style editing.
"""

from __future__ import annotations
from pathlib import Path
import cv2
import numpy as np


def apply_filter(image_path: str, filter_name: str, output_path: str | None = None) -> str:
    """Apply a named filter to an image file. Returns the output path."""
    out = output_path or image_path
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    result = _dispatch(img, filter_name)
    cv2.imwrite(out, result)
    return out


def _dispatch(img: np.ndarray, name: str) -> np.ndarray:
    name = name.lower().replace("-", "_").replace(" ", "_")
    fn = FILTER_MAP.get(name)
    if fn is None:
        raise ValueError(f"Unknown filter '{name}'. Available: {list(FILTER_MAP.keys())}")
    return fn(img)


# ---------------------------------------------------------------------------
# Filter implementations
# ---------------------------------------------------------------------------

def _grayscale(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def _sepia(img):
    kernel = np.array([
        [0.272, 0.534, 0.131],
        [0.349, 0.686, 0.168],
        [0.393, 0.769, 0.189],
    ])
    sepia = cv2.transform(img.astype(np.float64), kernel)
    return np.clip(sepia, 0, 255).astype(np.uint8)


def _blur(img):
    return cv2.GaussianBlur(img, (15, 15), 0)


def _sharpen(img):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)


def _edge_detect(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def _brightness_up(img):
    return cv2.convertScaleAbs(img, alpha=1.2, beta=30)


def _brightness_down(img):
    return cv2.convertScaleAbs(img, alpha=0.8, beta=-20)


def _vintage(img):
    sepia = _sepia(img)
    vignette = _vignette(sepia)
    return cv2.addWeighted(vignette, 0.85, np.full_like(vignette, [20, 10, 30]), 0.15, 0)


def _vignette(img):
    rows, cols = img.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, cols * 0.6)
    kernel_y = cv2.getGaussianKernel(rows, rows * 0.6)
    mask = kernel_y * kernel_x.T
    mask = mask / mask.max()
    output = img.copy().astype(np.float64)
    for i in range(3):
        output[:, :, i] *= mask
    return np.clip(output, 0, 255).astype(np.uint8)


def _cartoon(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon


def _invert(img):
    return cv2.bitwise_not(img)


FILTER_MAP = {
    "grayscale":      _grayscale,
    "sepia":          _sepia,
    "blur":           _blur,
    "sharpen":        _sharpen,
    "edge_detect":    _edge_detect,
    "brightness_up":  _brightness_up,
    "brightness_down":_brightness_down,
    "vintage":        _vintage,
    "vignette":       _vignette,
    "cartoon":        _cartoon,
    "invert":         _invert,
}
