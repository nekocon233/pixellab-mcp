"""Async WebSocket client for the PixelLab private API.

All tool modules call ``ws_client.call(endpoint, payload)`` to communicate
with ``ws://api.pixellab.ai/<endpoint>``.  Auth fields (secret/tier/version)
are injected automatically from environment variables or .env file.
"""
import json
import os

import websockets
from dotenv import load_dotenv

load_dotenv()

WS_BASE = "ws://api.pixellab.ai/"

# ── Auth ────────────────────────────────────────────────────────────────────
SECRET: str = os.getenv("PIXELLAB_SECRET", "")
TIER: int = int(os.getenv("PIXELLAB_TIER", "1"))
VERSION: str = os.getenv("PIXELLAB_VERSION", "0.5.0")

# ── Core call ────────────────────────────────────────────────────────────────

async def call(endpoint: str, payload: dict) -> dict:
    """Send *payload* to ``ws://api.pixellab.ai/<endpoint>`` and return the
    final response dict.

    * Auth fields are merged in automatically.
    * All messages are consumed; the last message that contains image data is
      returned (falls back to the very last non-trivial message if none had
      images).
    * Raises ``RuntimeError`` on API error messages.
    """
    if not SECRET:
        raise RuntimeError("PIXELLAB_SECRET is not set in .env")

    url = WS_BASE + endpoint
    full_payload = {
        "secret": SECRET,
        "tier": TIER,
        "version": VERSION,
        **payload,
    }

    async with websockets.connect(
        url,
        max_size=200 * 1024 * 1024,  # 200 MB – large spritesheets / animations
        open_timeout=30,
        ping_timeout=None,  # long-running generations shouldn't time out
    ) as ws:
        await ws.send(json.dumps(full_payload))

        last: dict = {}
        last_with_images: dict = {}

        async for raw_msg in ws:
            data: dict = json.loads(raw_msg)
            msg_type: str = data.get("type", "")

            if msg_type == "error":
                raise RuntimeError(
                    f"PixelLab API error [{endpoint}]: "
                    f"{data.get('detail', json.dumps(data))}"
                )

            if msg_type == "connected":
                continue  # handshake message, ignore

            last = data
            if "image" in data or "images" in data:
                last_with_images = data

    return last_with_images if last_with_images else last
