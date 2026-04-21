"""Client for the Audiveris OMR service."""

import json
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


@dataclass
class AudiverisResult:
    """Result from Audiveris OMR processing."""

    success: bool
    output_path: str = ""
    error: str = ""


def get_audiveris_url() -> str:
    """Return the Audiveris service URL."""
    return os.environ.get("AUDIVERIS_URL", "http://localhost:7070")


def process_notation(input_path: str, output_dir: str) -> AudiverisResult:
    """Send an image to the Audiveris service for OMR processing.

    Args:
        input_path: Absolute path to the notation image file.
        output_dir: Absolute path to the directory for MusicXML output.

    Returns:
        AudiverisResult with the output path or error message.

    """
    prepared_input_path = _prepare_notation_image_for_ocr(input_path=input_path, output_dir=output_dir)

    url = f"{get_audiveris_url()}/process"
    payload = json.dumps({"input_path": prepared_input_path, "output_dir": output_dir}).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=600) as response:
            data = json.loads(response.read())
            return AudiverisResult(success=True, output_path=data["output_path"])
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            data = json.loads(body)
            error_msg = data.get("error", body)
            details = data.get("stderr") or data.get("stdout") or ""
            if details:
                detail = _extract_audiveris_detail(details)
                if detail:
                    error_msg = f"{error_msg}: {detail}"
        except json.JSONDecodeError:
            error_msg = body
        return AudiverisResult(success=False, error=error_msg)
    except urllib.error.URLError as e:
        return AudiverisResult(success=False, error=f"Could not connect to Audiveris service: {e.reason}")


def _extract_audiveris_detail(output: str) -> str:
    """Extract the most actionable message from Audiveris output."""
    lines = output.splitlines()

    def normalize(line: str) -> str:
        return line.split("|", 1)[-1].strip() if "|" in line else line.strip()

    def is_noise(line: str) -> bool:
        lower = line.lower()
        if not line:
            return True
        if "at org." in line or "at java." in line:
            return True
        if "book{" in lower and "storing" in lower:
            return True
        if "book stored as" in lower and ".omr" in lower:
            return True
        if lower.startswith("stored ") or lower.startswith("storing "):
            return True
        if " stored /" in lower or " storing /" in lower:
            return True
        return False

    normalized = [normalize(line) for line in lines]

    # Priority 1: resolution/DPI warnings (most actionable)
    for line in normalized:
        if "too low" in line or "DPI" in line or "interline" in line:
            return line

    # Priority 2: generic stub failure + nearby cause line
    for index, line in enumerate(normalized):
        if "Error processing stub" in line:
            for candidate in normalized[index + 1 :]:
                if is_noise(candidate):
                    continue
                if "Exception" in candidate and "Caused by" not in candidate:
                    continue
                if "Error processing stub" in candidate:
                    continue
                return f"{line}. {candidate}"
            return line

    # Priority 2: WARN lines (excluding Java stack traces)
    for line in normalized:
        if "WARN" in line and not is_noise(line) and "Exception" not in line:
            return line

    # Priority 3: any non-empty line that is not a Java stack trace
    for line in normalized:
        if not is_noise(line):
            return line

    return ""


def _prepare_notation_image_for_ocr(input_path: str, output_dir: str) -> str:
    """Upscale and enhance low-resolution images before sending to Audiveris.

    This improves OCR success on screenshots that are too small or lack DPI metadata.
    Already adequate images are left unchanged.
    """
    target_dpi = 300
    target_min_width = 1800
    target_min_height = 1200
    max_scale_factor = 4.0

    try:
        with Image.open(input_path) as img:
            width, height = img.size
            raw_dpi = img.info.get("dpi", (0, 0))

            dpi_x = 0.0
            dpi_y = 0.0
            if isinstance(raw_dpi, tuple) and len(raw_dpi) == 2:
                dpi_x = float(raw_dpi[0] or 0)
                dpi_y = float(raw_dpi[1] or 0)

            scale_factor = 1.0
            min_dpi = min(dpi_x, dpi_y)
            # PNG stores DPI with limited precision, so treat near-300 as adequate.
            if min_dpi > 0 and min_dpi < (target_dpi - 1.0):
                scale_factor = max(scale_factor, target_dpi / min_dpi)
            if width < target_min_width:
                scale_factor = max(scale_factor, target_min_width / width)
            if height < target_min_height:
                scale_factor = max(scale_factor, target_min_height / height)

            scale_factor = min(scale_factor, max_scale_factor)
            if scale_factor <= 1.0:
                return input_path

            resized_width = max(1, int(round(width * scale_factor)))
            resized_height = max(1, int(round(height * scale_factor)))

            processed = img.convert("L")
            processed = ImageOps.autocontrast(processed)
            processed = processed.resize((resized_width, resized_height), Image.Resampling.LANCZOS)
            processed = processed.filter(ImageFilter.UnsharpMask(radius=1.5, percent=180, threshold=3))

            output_path = Path(output_dir) / f"{Path(input_path).stem}_ocr.png"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            processed.save(output_path, format="PNG", dpi=(target_dpi, target_dpi))
            return str(output_path)
    except OSError:
        return input_path
