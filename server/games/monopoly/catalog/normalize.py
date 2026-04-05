"""Normalize raw Monopoly instruction records into canonical artifacts."""

from .models import CanonicalCatalog, CanonicalEdition, RawInstructionRecord


def build_canonical_catalog(records: list[RawInstructionRecord]) -> CanonicalCatalog:
    """Build canonical editions and manual variants grouped by SKU."""
    by_sku: dict[str, list[RawInstructionRecord]] = {}
    for record in records:
        if not record.sku:
            continue
        by_sku.setdefault(record.sku, []).append(record)

    editions: list[CanonicalEdition] = []
    manual_variants: list[dict] = []

    for sku in sorted(by_sku):
        grouped = by_sku[sku]
        base = grouped[0]
        edition = CanonicalEdition.from_raw(base)
        editions.append(edition)

        for raw in grouped:
            for manual in raw.manuals:
                manual_variants.append(
                    {
                        "edition_id": edition.edition_id,
                        "sku": raw.sku,
                        "locale": raw.locale,
                        "instruction_url": raw.instruction_url,
                        "pdf_url": manual.pdf_url,
                        "filename": manual.filename,
                        "size_bytes": manual.size_bytes,
                    }
                )

    manual_variants.sort(
        key=lambda row: (
            row["edition_id"],
            row["locale"],
            row["filename"],
            row["pdf_url"],
        )
    )

    return CanonicalCatalog(editions=editions, manual_variants=manual_variants)

