"""Extract structured Monopoly records from instruction page HTML payloads."""

import json
import re

from .models import RawInstructionRecord, RawManual


_NEXT_DATA_RE = re.compile(
    r"<script[^>]*id=['\"]?__NEXT_DATA__['\"]?[^>]*"
    r"type=['\"]?application/json['\"]?[^>]*>(.*?)</script>",
    re.DOTALL,
)


def extract_next_data_json(html: str) -> dict:
    """Extract and parse the Next.js `__NEXT_DATA__` payload from HTML."""
    match = _NEXT_DATA_RE.search(html)
    if not match:
        raise ValueError("No __NEXT_DATA__ payload found in instruction HTML")
    return json.loads(match.group(1))


def extract_raw_records(payload: dict, instruction_url: str) -> list[RawInstructionRecord]:
    """Extract raw instruction records from a parsed `__NEXT_DATA__` payload."""
    page_props = payload.get("props", {}).get("pageProps", {})
    locale = str(page_props.get("locale", ""))
    rows = page_props.get("instructions", {}).get("filtered_instructions", [])

    records: list[RawInstructionRecord] = []
    for row in rows:
        if not row:
            continue
        item = row[0]
        manuals = [
            RawManual(
                pdf_url=pdf.get("url", ""),
                filename=pdf.get("url", "").rsplit("/", 1)[-1],
                size_bytes=pdf.get("size"),
            )
            for pdf in item.get("pdf", [])
            if pdf.get("url")
        ]
        records.append(
            RawInstructionRecord(
                locale=locale,
                instruction_url=instruction_url,
                sku=str(item.get("sku", "")),
                slug=str(item.get("slug", "")),
                name=str(item.get("name", "")),
                brand=str(item.get("brand", "")),
                manuals=manuals,
            )
        )
    return records
