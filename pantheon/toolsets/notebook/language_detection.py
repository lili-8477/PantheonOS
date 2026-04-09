"""Kernel spec constants and language helpers for notebook creation.

The agent decides the language upfront and passes it through the tool chain.
This module provides the kernel specs and metadata for each supported language.
"""

from typing import Literal

Language = Literal["python", "r"]

# ── Kernel spec constants ──────────────────────────────────────────

KERNEL_SPECS = {
    "python": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.12.0",
            "mimetype": "text/x-python",
            "file_extension": ".py",
        },
    },
    "r": {
        "kernelspec": {
            "display_name": "R",
            "language": "R",
            "name": "ir",
        },
        "language_info": {
            "name": "R",
            "mimetype": "text/x-r-source",
            "file_extension": ".r",
        },
    },
}

# Maps kernel spec names to language
KERNEL_NAME_TO_LANGUAGE = {
    "python3": "python",
    "python": "python",
    "ir": "r",
}


def normalize_language_name(language: str | None) -> Language:
    """Normalize notebook/frontend language identifiers to canonical values."""
    if not language:
        return "python"

    normalized = str(language).strip().lower()
    if normalized in {"r", "ir"}:
        return "r"
    if normalized in {"python", "python3"}:
        return "python"

    return "python"


def detect_notebook_language(metadata: dict | None) -> Language:
    """Detect notebook language from top-level metadata fields."""
    metadata = metadata or {}

    return normalize_language_name(
        metadata.get("language")
        or metadata.get("language_info", {}).get("name")
        or metadata.get("kernelspec", {}).get("language")
        or metadata.get("kernelspec", {}).get("name")
    )


def get_kernel_spec(language: Language) -> dict:
    """Get kernel spec dict for a language."""
    return KERNEL_SPECS[language]["kernelspec"].copy()


def get_language_info(language: Language) -> dict:
    """Get language_info metadata dict for a language."""
    return KERNEL_SPECS[language]["language_info"].copy()


def kernel_name_for_language(language: Language) -> str:
    """Get jupyter kernel name for a language."""
    return "ir" if language == "r" else "python3"


def language_from_kernel_name(kernel_name: str) -> Language:
    """Get language from a jupyter kernel name."""
    return normalize_language_name(KERNEL_NAME_TO_LANGUAGE.get(kernel_name) or kernel_name)
