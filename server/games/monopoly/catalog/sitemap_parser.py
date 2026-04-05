"""Helpers for parsing Hasbro sitemap XML documents."""

import xml.etree.ElementTree as ET


_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def parse_sitemap_index(xml_text: str) -> list[str]:
    """Return locale sitemap URLs from a sitemap index document."""
    root = ET.fromstring(xml_text)
    urls: list[str] = []
    for loc in root.findall(".//sm:sitemap/sm:loc", _NS):
        if loc.text:
            urls.append(loc.text.strip())
    return urls


def parse_monopoly_instruction_urls(xml_text: str) -> list[str]:
    """Return deduped Monopoly instruction URLs from a locale sitemap."""
    root = ET.fromstring(xml_text)
    urls: set[str] = set()
    for loc in root.findall(".//sm:url/sm:loc", _NS):
        if not loc.text:
            continue
        url = loc.text.strip()
        if "/instruction/" not in url:
            continue
        if "monopoly" in url.lower():
            urls.add(url)
    return sorted(urls)

