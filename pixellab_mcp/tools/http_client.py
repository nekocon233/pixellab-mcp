"""Async REST HTTP client for the PixelLab V2 API.

All tool modules call ``http_client.call(...)``,
``http_client.call_async(...)``, ``http_client.get(...)``, etc. to
communicate with ``https://api.pixellab.ai/v2/<endpoint>``.

Auth is via the ``Authorization: Bearer TOKEN`` header, read from the
``PIXELLAB_SECRET`` environment variable (or ``.env`` file).
"""
import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.pixellab.ai/v2/"
SECRET: str = os.getenv("PIXELLAB_SECRET", "")

# Polling defaults
POLL_INTERVAL = 2.0  # seconds between polls
POLL_TIMEOUT = 300.0  # max seconds to wait for an async job


class PixelLabError(RuntimeError):
    """Raised when the PixelLab V2 API returns an error."""


def _headers() -> dict:
    return {"Authorization": f"Bearer {SECRET}"}


def _parse_response(resp: httpx.Response) -> dict:
    """Parse a V2 API response and return the ``data`` field.

    Raises ``PixelLabError`` on non-200 status or ``{"success": false}``.
    """
    if resp.status_code == 202:
        # Async job accepted — return the raw body so the caller can
        # extract ``background_job_id``.
        body = resp.json()
        if not body.get("success", True):
            raise PixelLabError(
                f"PixelLab API error: {body.get('error', body)}"
            )
        return body.get("data", body)

    if resp.status_code >= 400:
        try:
            body = resp.json()
            raise PixelLabError(
                f"PixelLab API error [{resp.status_code}]: "
                f"{body.get('error', body)}"
            )
        except (ValueError, AttributeError):
            raise PixelLabError(
                f"PixelLab API error [{resp.status_code}]: {resp.text}"
            )

    body = resp.json()
    if not body.get("success", True):
        raise PixelLabError(
            f"PixelLab API error: {body.get('error', body)}"
        )
    return body.get("data", body)


# ── Sync call (POST → immediate result) ──────────────────────────────────

async def call(endpoint: str, payload: dict) -> dict:
    """Send a POST to ``/v2/<endpoint>`` and return the ``data`` dict.

    Use for endpoints that return results immediately (200).
    """
    if not SECRET:
        raise RuntimeError("PIXELLAB_SECRET is not set in .env")

    url = BASE_URL + endpoint
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, json=payload, headers=_headers())
        return _parse_response(resp)


# ── Async call (POST → 202 → poll until done) ───────────────────────────

async def call_async(
    endpoint: str,
    payload: dict,
    poll_interval: float = POLL_INTERVAL,
    poll_timeout: float = POLL_TIMEOUT,
) -> dict:
    """Send a POST that returns a ``background_job_id``, then poll
    ``GET /background-jobs/{job_id}`` until the job completes.

    Returns the job's ``last_response`` dict on success.
    """
    if not SECRET:
        raise RuntimeError("PIXELLAB_SECRET is not set in .env")

    url = BASE_URL + endpoint
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, json=payload, headers=_headers())
        data = _parse_response(resp)

    job_id = data.get("background_job_id") or data.get("id")
    if not job_id:
        # Some "async" endpoints actually return data directly —
        # handle that gracefully.
        return data

    return await _poll_job(job_id, poll_interval, poll_timeout)


async def _poll_job(
    job_id: str,
    interval: float = POLL_INTERVAL,
    timeout: float = POLL_TIMEOUT,
) -> dict:
    """Poll ``GET /background-jobs/{job_id}`` until status is
    ``completed`` or ``failed``.
    """
    url = BASE_URL + f"background-jobs/{job_id}"
    elapsed = 0.0

    async with httpx.AsyncClient(timeout=30.0) as client:
        while elapsed < timeout:
            resp = await client.get(url, headers=_headers())
            data = _parse_response(resp)

            status = data.get("status", "processing")
            if status == "completed":
                return data.get("last_response", data)
            if status == "failed":
                raise PixelLabError(
                    f"PixelLab async job {job_id} failed: "
                    f"{data.get('error', data)}"
                )

            await asyncio.sleep(interval)
            elapsed += interval

    raise PixelLabError(
        f"PixelLab async job {job_id} timed out after {timeout}s"
    )


# ── GET / DELETE helpers ─────────────────────────────────────────────────

async def get(endpoint: str, params: dict | None = None) -> dict:
    """Send a GET request and return parsed data."""
    if not SECRET:
        raise RuntimeError("PIXELLAB_SECRET is not set in .env")

    url = BASE_URL + endpoint
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params, headers=_headers())
        return _parse_response(resp)


async def delete(endpoint: str) -> dict:
    """Send a DELETE request and return parsed data."""
    if not SECRET:
        raise RuntimeError("PIXELLAB_SECRET is not set in .env")

    url = BASE_URL + endpoint
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.delete(url, headers=_headers())
        return _parse_response(resp)


async def patch(endpoint: str, payload: dict) -> dict:
    """Send a PATCH request and return parsed data."""
    if not SECRET:
        raise RuntimeError("PIXELLAB_SECRET is not set in .env")

    url = BASE_URL + endpoint
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.patch(url, json=payload, headers=_headers())
        return _parse_response(resp)
