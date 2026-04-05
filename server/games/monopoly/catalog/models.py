"""Dataclass models used by the Monopoly catalog pipeline."""

from dataclasses import dataclass, field


@dataclass
class RawManual:
    """Manual metadata directly extracted from instruction payloads."""

    pdf_url: str
    filename: str
    size_bytes: int | None = None


@dataclass
class RawInstructionRecord:
    """Raw record extracted from a locale instruction page payload."""

    locale: str
    instruction_url: str
    sku: str
    slug: str
    name: str
    brand: str
    manuals: list[RawManual] = field(default_factory=list)
    source_lastmod: str = ""


@dataclass
class CanonicalEdition:
    """Normalized, deduplicated Monopoly edition record."""

    edition_id: str
    sku: str
    canonical_slug: str
    display_name: str
    brand: str
    categories: list[str] = field(default_factory=list)
    first_seen_at: str = ""
    last_seen_at: str = ""

    @classmethod
    def from_raw(cls, raw: RawInstructionRecord) -> "CanonicalEdition":
        """Create a canonical edition shell from a raw extracted record."""
        return cls(
            edition_id=f"monopoly-{raw.sku.lower()}",
            sku=raw.sku,
            canonical_slug=raw.slug,
            display_name=raw.name,
            brand=raw.brand,
        )


@dataclass
class CanonicalCatalog:
    """Canonical output artifacts produced by the normalizer."""

    editions: list[CanonicalEdition] = field(default_factory=list)
    manual_variants: list[dict] = field(default_factory=list)
