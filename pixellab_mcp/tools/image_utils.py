"""Image encoding/decoding helpers for PixelLab MCP server."""
import base64
import io
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from PIL import Image

OUTPUT_DIR = Path(__file__).parent / "assets" / "output"
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def path_to_png_b64(path: str) -> str:
    """Read an image file and return base64-encoded PNG bytes (string)."""
    img = Image.open(path).convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def path_to_rgba_b64(path: str) -> Tuple[str, int, int]:
    """Read an image file and return (base64 raw-RGBA bytes, width, height).

    Required by the generate-consistent-style endpoint which encodes images
    as raw RGBA bytes rather than compressed PNG.
    """
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    return base64.b64encode(img.tobytes()).decode(), w, h


def save_response_images(
    images_data: list,
    fallback_width: int,
    fallback_height: int,
    prefix: str,
) -> List[str]:
    """Save API response images and return a list of saved file paths.

    Handles both PNG bytes and raw RGBA bytes transparently by inspecting
    the PNG magic bytes header.
    """
    ensure_output_dir()
    paths: List[str] = []
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")

    for i, img in enumerate(images_data):
        if isinstance(img, dict):
            b64 = img.get("base64", "")
            w = img.get("width", fallback_width)
            h = img.get("height", fallback_height)
        elif isinstance(img, str):
            b64 = img
            w, h = fallback_width, fallback_height
        else:
            continue

        if not b64:
            continue

        raw = base64.b64decode(b64)
        out_path = OUTPUT_DIR / f"{prefix}_{ts}_{i}.png"

        if raw[:8] == _PNG_MAGIC:
            out_path.write_bytes(raw)
        else:
            # Raw RGBA bytes – reconstruct with PIL
            Image.frombytes("RGBA", (w, h), raw).save(out_path)

        paths.append(str(out_path))

    return paths


def extract_images(result: dict) -> list:
    """Pull image list from an API response dict."""
    if "images" in result:
        return [img for img in result["images"] if img is not None]
    if "image" in result and result["image"] is not None:
        return [result["image"]]
    return []
