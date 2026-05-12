"""Output-path and file persistence helpers for the Streamlit app."""

from __future__ import annotations

import re
from pathlib import Path

import streamlit as st


def ensure_output_dir(base_dir: Path) -> Path:
    """Create output directory if needed and return it."""
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def _get_case_folder(filename: str) -> str:
    """Extract the original input stem used to group related outputs."""
    match = re.match(r"^(.*)_(aes|des)_(encrypted|decrypted)(?:\..*)?$", filename, re.IGNORECASE)
    if match:
        return match.group(1)
    return Path(filename).stem


def save_to_output(output_dir: Path, filename: str, data: bytes) -> Path:
    """Save bytes to a per-input subfolder inside the output directory."""
    subfolder = output_dir / _get_case_folder(filename)
    subfolder.mkdir(exist_ok=True)
    path = subfolder / filename
    path.write_bytes(data)
    return path


def load_from_disk(path_str: str | None) -> bytes | None:
    """Load ciphertext bytes from disk and show consistent UI errors."""
    if not path_str:
        st.error("⚠️ No saved ciphertext path found — please re-encrypt first.")
        return None

    path = Path(path_str)
    if not path.exists():
        st.error(f"⚠️ Ciphertext file not found on disk: `{path}`")
        return None

    return path.read_bytes()
