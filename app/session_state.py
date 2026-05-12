"""Session-state defaults and initialization helpers."""

from __future__ import annotations

from typing import Any


DEFAULT_SESSION_STATE: dict[str, Any] = {
    "plaintext": None,
    "filename": "data.bin",
    "aes_enc": None,
    "des_enc": None,
    "aes_key": None,
    "des_key": None,
    "aes_meta": None,
    "des_meta": None,
    "aes_enc_t": 0.0,
    "des_enc_t": 0.0,
    "aes_dec": None,
    "des_dec": None,
    "aes_dec_t": 0.0,
    "des_dec_t": 0.0,
    "aes_ok": None,
    "des_ok": None,
    "stage_encrypted": False,
    "stage_decrypted": False,
    "stage_verified": False,
    "aes_key_size": 256,
    "aes_mode": "CBC",
    "des_mode": "CBC",
    "saved_enc_aes": None,
    "saved_enc_des": None,
    "saved_dec_aes": None,
    "saved_dec_des": None,
    "scroll_to": None,
}


def init_session_state(session_state: Any) -> None:
    """Populate Streamlit session_state with project defaults if missing."""
    for key, value in DEFAULT_SESSION_STATE.items():
        if key not in session_state:
            session_state[key] = value
