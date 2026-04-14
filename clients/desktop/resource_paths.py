"""Helpers for resolving bundled desktop-client resources.

PyInstaller uses different runtime layouts across platforms:
- source checkout: resources live next to the Python files
- Windows/Linux onedir: resources may live beside the executable or under
  ``_internal/``
- macOS app bundles: resources may live under ``Contents/Resources`` or
  ``Contents/Frameworks/_internal``

These helpers let the client find assets without depending on the current
working directory.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _iter_resource_roots() -> list[Path]:
    """Return candidate directories that may contain bundled resources."""
    roots: list[Path] = [Path(__file__).resolve().parent]

    if not getattr(sys, "frozen", False):
        return roots

    exe_dir = Path(sys.executable).resolve().parent
    bundle_roots = [
        exe_dir,
        exe_dir / "_internal",
    ]

    if exe_dir.name == "MacOS":
        contents_dir = exe_dir.parent
        bundle_roots.extend(
            [
                contents_dir / "Resources",
                contents_dir / "Frameworks",
                contents_dir / "Frameworks" / "_internal",
            ]
        )

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        bundle_roots.append(Path(meipass))

    for candidate in bundle_roots:
        if candidate not in roots:
            roots.append(candidate)

    return roots


def find_resource_path(relative_path: str | Path) -> Path:
    """Find a resource path in source or bundled app layouts.

    Returns the first existing match. If nothing exists yet, returns the path
    under the first candidate root so callers still get a deterministic
    fallback.
    """
    rel = Path(relative_path)
    roots = _iter_resource_roots()
    for root in roots:
        candidate = root / rel
        if candidate.exists():
            return candidate
    return roots[0] / rel
