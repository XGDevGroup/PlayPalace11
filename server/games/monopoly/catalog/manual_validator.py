"""Validation utilities for official Monopoly manual PDF URLs."""

from datetime import datetime, UTC
import hashlib
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def validate_manual(pdf_url: str, timeout: float = 20.0) -> dict:
    """Validate a manual URL and compute a content checksum when downloadable."""
    request = Request(
        pdf_url,
        headers={
            "User-Agent": "PlayPalace-Monopoly-Catalog/1.0",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read()
            return {
                "pdf_url": pdf_url,
                "http_status": getattr(response, "status", 200),
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "verified_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "error": "",
            }
    except HTTPError as error:
        return {
            "pdf_url": pdf_url,
            "http_status": error.code,
            "size_bytes": None,
            "sha256": "",
            "verified_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "error": str(error),
        }
    except URLError as error:
        return {
            "pdf_url": pdf_url,
            "http_status": 0,
            "size_bytes": None,
            "sha256": "",
            "verified_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "error": str(error),
        }

