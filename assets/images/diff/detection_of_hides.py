"""
detect_circles.py
-----------------
Detects red-outlined circles in an image and saves their positions to a text file.

Usage:
    python detect_circles.py <image_path>
    python detect_circles.py <image_path> <output_txt_path>

Output file format:
    /full/path/to/image.jpeg
    "diffs": [(x,y,radius), ...]

Dependencies:
    pip install opencv-python-headless numpy
"""

import cv2
import numpy as np
import os
import sys


def detect_and_save_circles(image_path, output_path=None, min_area=200):
    """
    Detect red-outlined circles in an image and save results to a text file.

    Args:
        image_path  (str): Path to the input image.
        output_path (str): Where to write the .txt result file.
                           Defaults to <image_stem>_circles.txt in the
                           same folder as the image (falls back to cwd
                           if that folder is read-only).
        min_area    (int): Minimum contour pixel area to suppress noise
                           (default: 200).

    Returns:
        str: Absolute path to the saved text file.
    """
    # ── Load ──────────────────────────────────────────────────────────────
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not open image: {image_path}")

    # ── Red mask (HSV) ────────────────────────────────────────────────────
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.bitwise_or(
        cv2.inRange(hsv, np.array([0,   50, 80]), np.array([10,  255, 255])),
        cv2.inRange(hsv, np.array([160, 50, 80]), np.array([180, 255, 255])),
    )

    # Close small gaps in thick ring outlines
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # ── Contour → circle ──────────────────────────────────────────────────
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    circles = []
    for cnt in contours:
        if cv2.contourArea(cnt) < min_area:
            continue

        # Bounding rect spans the full circle (even when the interior is hollow)
        x, y, w, h = cv2.boundingRect(cnt)
        cx     = x + w // 2
        cy     = y + h // 2
        radius = (w + h) // 4   # mean of half-width and half-height

        circles.append((cx, cy, radius))

    # Sort top-to-bottom, then left-to-right
    circles.sort(key=lambda c: (c[1], c[0]))

    # ── Format output ─────────────────────────────────────────────────────
    abs_image_path = os.path.abspath(image_path)
    formatted      = ", ".join(f"({x},{y},{r})" for x, y, r in circles)
    output_text    = f'{abs_image_path}\n"diffs": [{formatted}]\n'

    # ── Resolve output path ───────────────────────────────────────────────
    if output_path is None:
        stem      = os.path.splitext(image_path)[0]
        candidate = stem + "_circles.txt"
        try:
            with open(candidate, "w") as f:
                f.write(output_text)
            output_path = os.path.abspath(candidate)
        except OSError:
            # Image directory is read-only → fall back to cwd
            fallback = os.path.splitext(os.path.basename(image_path))[0] + "_circles.txt"
            with open(fallback, "w") as f:
                f.write(output_text)
            output_path = os.path.abspath(fallback)
    else:
        with open(output_path, "w") as f:
            f.write(output_text)

    print(f"Detected {len(circles)} circle(s).")
    print(f"Saved to: {output_path}")
    print(f"\n{output_text}")

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python detect_circles.py <image_path> [output_txt_path]")
        sys.exit(1)

    img_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) >= 3 else None
    detect_and_save_circles(img_path, out_path)