import streamlit as st
import time
import base64
import hashlib
import os
from pathlib import Path
from crypto_utils import (
    encrypt_aes, decrypt_aes,
    encrypt_aes_gcm, decrypt_aes_gcm,
    encrypt_des, decrypt_des,
    generate_aes_key, generate_des_key,
    verify_files,
    key_fingerprint,
    compute_sha256,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CryptoLab — AES vs DES",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg: #0a0c10; --surface: #111318; --surface2: #1a1d25;
    --border: #2a2d38; --accent-aes: #00e5ff; --accent-des: #ff6b35;
    --accent-ok: #39ff14; --text: #e8eaf0; --muted: #6b7280; --danger: #ff4444;
    --accent-gcm: #c084fc;
}
html, body, [class*="css"] { font-family: 'Syne', sans-serif; background: var(--bg); color: var(--text); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1100px; }
[data-testid="stSidebar"] { display: none; }

h1 { font-size: 2.3rem !important; font-weight: 800 !important; letter-spacing: -0.02em; }

/* ── Input card ── */
.input-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.5rem;
}
.input-card-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; letter-spacing: 0.2em;
    text-transform: uppercase; color: var(--muted);
    margin-bottom: 1rem;
}

/* ── Config row ── */
.config-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1rem;
}

/* ── Step indicator ── */
.steps-row { display: flex; align-items: center; gap: 0; margin: 1.4rem 0 1.6rem 0; }
.step-item { display: flex; flex-direction: column; align-items: center; gap: 0.3rem; flex: 1; }
.step-circle {
    width: 2.4rem; height: 2.4rem; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; font-weight: 700;
    border: 2px solid var(--border); background: var(--surface2); color: var(--muted); z-index: 1;
}
.step-circle.active { border-color: var(--accent-aes); background: rgba(0,229,255,0.12); color: var(--accent-aes); box-shadow: 0 0 14px rgba(0,229,255,0.25); }
.step-circle.done   { border-color: var(--accent-ok);  background: rgba(57,255,20,0.1);  color: var(--accent-ok); }
.step-label { font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--muted); }
.step-label.active { color: var(--accent-aes); }
.step-label.done   { color: var(--accent-ok); }
.step-connector { flex: 1; height: 2px; background: var(--border); margin-top: -1.7rem; }
.step-connector.done { background: var(--accent-ok); }

/* ── Action buttons ── */
div.stButton > button {
    font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; letter-spacing: 0.1em;
    border-radius: 8px; padding: 0.6rem 1.2rem; transition: all 0.2s; width: 100%;
    border: 1px solid var(--border); background: transparent; color: var(--text);
}
[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-color:rgba(0,229,255,0.5); color:var(--accent-aes); background:rgba(0,229,255,0.07); }
[data-testid="stHorizontalBlock"] > div:nth-child(1) button:hover { background:rgba(0,229,255,0.15); }
[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-color:rgba(255,107,53,0.5); color:var(--accent-des); background:rgba(255,107,53,0.07); }
[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover { background:rgba(255,107,53,0.15); }
[data-testid="stHorizontalBlock"] > div:nth-child(3) button { border-color:rgba(57,255,20,0.5); color:var(--accent-ok); background:rgba(57,255,20,0.07); }
[data-testid="stHorizontalBlock"] > div:nth-child(3) button:hover { background:rgba(57,255,20,0.15); }
[data-testid="stHorizontalBlock"] > div:nth-child(4) button { border-color:rgba(107,114,128,0.4); color:var(--muted); }

/* ── Misc ── */
.metric-card { background: var(--surface2); border: 1px solid var(--border); border-radius: 12px; padding: 1.1rem 1.3rem; margin-bottom: 0.75rem; }
.metric-label { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.25rem; }
.metric-value { font-size: 1.8rem; font-weight: 800; letter-spacing: -0.02em; }
.aes-color { color: var(--accent-aes); } .des-color { color: var(--accent-des); } .ok-color { color: var(--accent-ok); } .gcm-color { color: var(--accent-gcm); }

.info-table { width: 100%; border-collapse: collapse; }
.info-table td { padding: 0.5rem 0.7rem; font-size: 0.83rem; border-bottom: 1px solid var(--border); }
.info-table td:first-child { font-family: 'JetBrains Mono', monospace; color: var(--muted); font-size: 0.72rem; width: 42%; }

.cipher-box { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 0.9rem 1.1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; word-break: break-all; color: #a5b4fc; max-height: 130px; overflow-y: auto; line-height: 1.6; }

.badge { display: inline-block; padding: 0.15rem 0.55rem; border-radius: 999px; font-size: 0.68rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
.badge-aes  { background: rgba(0,229,255,0.12); color: var(--accent-aes); border: 1px solid rgba(0,229,255,0.3); }
.badge-des  { background: rgba(255,107,53,0.12); color: var(--accent-des); border: 1px solid rgba(255,107,53,0.3); }
.badge-ok   { background: rgba(57,255,20,0.1);  color: var(--accent-ok);  border: 1px solid rgba(57,255,20,0.25); }
.badge-fail { background: rgba(255,68,68,0.1);  color: var(--danger);     border: 1px solid rgba(255,68,68,0.3); }
.badge-warn { background: rgba(255,200,0,0.1);  color: #ffc800;           border: 1px solid rgba(255,200,0,0.3); }
.badge-gcm  { background: rgba(192,132,252,0.12); color: var(--accent-gcm); border: 1px solid rgba(192,132,252,0.3); }

.bar-wrap  { display: flex; align-items: center; gap: 0.6rem; margin: 0.4rem 0; }
.bar-label { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: var(--muted); min-width: 3.5rem; }
.bar-track { flex: 1; background: var(--border); border-radius: 4px; height: 8px; overflow: hidden; }
.bar-fill  { height: 100%; border-radius: 4px; }
.bar-val   { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; min-width: 5rem; text-align: right; }

.section-header { display: flex; align-items: center; gap: 0.75rem; margin: 1.6rem 0 1rem 0; }
.section-line   { flex: 1; height: 1px; background: var(--border); }
.section-title  { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--muted); white-space: nowrap; }

.verify-banner { border-radius: 12px; padding: 1.4rem 1.8rem; margin: 0.5rem 0; }
.verify-ok   { background: rgba(57,255,20,0.07);  border: 1px solid rgba(57,255,20,0.35); }
.verify-fail { background: rgba(255,68,68,0.07);  border: 1px solid rgba(255,68,68,0.35); }
.verify-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.3rem; }
.verify-sub   { font-size: 0.78rem; color: var(--muted); font-family: 'JetBrains Mono', monospace; line-height: 1.8; }

.saved-path { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: var(--accent-ok); background: rgba(57,255,20,0.07); border: 1px solid rgba(57,255,20,0.2); border-radius: 6px; padding: 0.3rem 0.7rem; display: inline-block; margin-top: 0.4rem; word-break: break-all; }

.stSuccess { background: rgba(57,255,20,0.07) !important; border: 1px solid rgba(57,255,20,0.3) !important; }
.stError   { background: rgba(255,68,68,0.07) !important; border: 1px solid rgba(255,68,68,0.3) !important; }
.stInfo    { background: rgba(0,229,255,0.05) !important; border: 1px solid rgba(0,229,255,0.2) !important; }
.stWarning { background: rgba(255,200,0,0.06) !important; border: 1px solid rgba(255,200,0,0.25) !important; }
.hint-box  { margin:1.5rem 0; padding:1rem 1.4rem; border-radius:10px; font-family:'JetBrains Mono',monospace; font-size:0.8rem; letter-spacing:0.06em; }

/* fingerprint pill */
.fp-pill { display:inline-block; font-family:'JetBrains Mono',monospace; font-size:0.68rem;
           letter-spacing:0.12em; padding:0.2rem 0.7rem; border-radius:999px;
           background:rgba(255,255,255,0.04); border:1px solid var(--border); color:#9ca3af; }

/* GCM tag pill */
.tag-pill { font-family:'JetBrains Mono',monospace; font-size:0.66rem; color:var(--accent-gcm);
            background:rgba(192,132,252,0.08); border:1px solid rgba(192,132,252,0.25);
            border-radius:6px; padding:0.25rem 0.6rem; word-break:break-all; display:inline-block; }

/* Selectbox / radio styling */
[data-testid="stSelectbox"] label,
[data-testid="stRadio"] label { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; }
[data-testid="stFileUploader"] { background: var(--surface2); border: 1px dashed var(--border); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Auto-scroll JS helper ─────────────────────────────────────────────────────
def inject_scroll(anchor_id: str):
    """Inject JS that scrolls the page to the element with the given id."""
    st.components.v1.html(
        f"""<script>
        window.parent.document.getElementById('{anchor_id}')
            ?.scrollIntoView({{behavior:'smooth', block:'start'}});
        </script>""",
        height=0,
    )

# ── Helpers ───────────────────────────────────────────────────────────────────
def section(label, anchor_id=None):
    anchor_html = f'<span id="{anchor_id}" style="position:relative;top:-80px"></span>' if anchor_id else ""
    st.markdown(
        f'{anchor_html}<div class="section-header">'
        f'<div class="section-line"></div>'
        f'<div class="section-title">{label}</div>'
        f'<div class="section-line"></div></div>',
        unsafe_allow_html=True,
    )

def badge(text, kind="aes"):
    return f'<span class="badge badge-{kind}">{text}</span>'

def metric_card(label, value, color_class=""):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value {color_class}">{value}</div></div>',
        unsafe_allow_html=True,
    )

def cipher_preview(b, n=96):
    return base64.b64encode(b[:n]).decode() + ("…" if len(b) > n else "")

def fmt_time(t):
    if t < 0.001: return f"{t*1_000_000:.1f} µs"
    if t < 1:     return f"{t*1000:.3f} ms"
    return f"{t:.4f} s"

def bar_chart(la, va, ca, lb, vb, cb):
    mx = max(va, vb, 1e-12)
    st.markdown(
        f'<div class="bar-wrap"><div class="bar-label">{la}</div>'
        f'<div class="bar-track"><div class="bar-fill" style="width:{va/mx*100:.1f}%;background:{ca}"></div></div>'
        f'<div class="bar-val" style="color:{ca}">{fmt_time(va)}</div></div>'
        f'<div class="bar-wrap"><div class="bar-label">{lb}</div>'
        f'<div class="bar-track"><div class="bar-fill" style="width:{vb/mx*100:.1f}%;background:{cb}"></div></div>'
        f'<div class="bar-val" style="color:{cb}">{fmt_time(vb)}</div></div>',
        unsafe_allow_html=True,
    )

def step_indicator(enc, dec, ver):
    def sc(done, active): return "done" if done else ("active" if active else "")
    st.markdown(f"""
    <div class="steps-row">
      <div class="step-item">
        <div class="step-circle {sc(enc, not enc)}">{"✓" if enc else "1"}</div>
        <div class="step-label {sc(enc, not enc)}">Encrypt</div>
      </div>
      <div class="step-connector {"done" if enc else ""}"></div>
      <div class="step-item">
        <div class="step-circle {sc(dec, enc and not dec)}">{"✓" if dec else "2"}</div>
        <div class="step-label {sc(dec, enc and not dec)}">Decrypt</div>
      </div>
      <div class="step-connector {"done" if dec else ""}"></div>
      <div class="step-item">
        <div class="step-circle {sc(ver, dec and not ver)}">{"✓" if ver else "3"}</div>
        <div class="step-label {sc(ver, dec and not ver)}">Verify</div>
      </div>
    </div>""", unsafe_allow_html=True)

def copy_button(label: str, text: str):
    """Render a small copy-to-clipboard button using st.code trick."""
    with st.expander(f"📋 Copy {label} (Base64)"):
        st.code(base64.b64encode(text).decode() if isinstance(text, bytes) else text, language="text")

def save_to_output(filename: str, data: bytes) -> Path:
    path = OUTPUT_DIR / filename
    path.write_bytes(data)
    return path


def load_from_disk(path_str: str | None) -> bytes | None:
    """
    Option A — Re-read ciphertext from disk immediately before decrypting.

    This makes on-disk tampering detectable:
      • Non-GCM modes: decrypted bytes won't match the original, so
        verify_files() will return False and the Verify step flags a mismatch.
      • GCM mode: decrypt_aes_gcm() raises ValueError on tag failure
        before Verify is even reached.

    Returns None (with a Streamlit error) if the file is missing.
    """
    if not path_str:
        st.error("⚠️ No saved ciphertext path found — please re-encrypt first.")
        return None
    p = Path(path_str)
    if not p.exists():
        st.error(f"⚠️ Ciphertext file not found on disk: `{p}`")
        return None
    return p.read_bytes()

# ── Session state ─────────────────────────────────────────────────────────────
_def = dict(
    plaintext=None, filename="data.bin",
    aes_enc=None, des_enc=None, aes_key=None, des_key=None,
    aes_meta=None, des_meta=None, aes_enc_t=0.0, des_enc_t=0.0,
    aes_dec=None, des_dec=None, aes_dec_t=0.0, des_dec_t=0.0,
    aes_ok=None, des_ok=None,
    stage_encrypted=False, stage_decrypted=False, stage_verified=False,
    aes_key_size=256, aes_mode="CBC", des_mode="CBC",
    saved_enc_aes=None, saved_enc_des=None,
    saved_dec_aes=None, saved_dec_des=None,
    # new: which step to auto-scroll to after rerun
    scroll_to=None,
)
for k, v in _def.items():
    if k not in st.session_state:
        st.session_state[k] = v
S = st.session_state

# ═════════════════════════════════════════════════════════════════════════════
# HEADER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="display:flex;align-items:baseline;gap:1rem;margin-bottom:0.15rem">
  <h1 style="margin:0">🔐 CryptoLab</h1>
  <span style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#6b7280;
        letter-spacing:.15em;text-transform:uppercase">AES vs DES · v2</span>
</div>
<p style="color:#9ca3af;margin:0 0 1rem 0;font-size:0.87rem">
  Step through <b style="color:#00e5ff">Encrypt</b> →
  <b style="color:#ff6b35">Decrypt</b> →
  <b style="color:#39ff14">Verify</b> and compare both algorithms side by side.
  New: <b style="color:#c084fc">AES-GCM</b> authenticated encryption + key fingerprints.
</p>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# INPUT & CONFIG
# ═════════════════════════════════════════════════════════════════════════════
section("Input Data & Configuration")

inp_col, cfg_col = st.columns([3, 2], gap="large")

with inp_col:
    st.markdown('<div class="input-card-title">📄 Input source</div>', unsafe_allow_html=True)
    source = st.radio(
        "source", ["Upload a file", "Enter text manually"],
        label_visibility="collapsed", horizontal=True,
    )
    st.markdown("<div style='margin-top:0.7rem'></div>", unsafe_allow_html=True)

    uploaded    = None
    custom_text = None

    if source == "Upload a file":
        uploaded = st.file_uploader(
            "Drop a file here or click to browse",
            type=["txt", "csv", "json", "png", "jpg", "pdf"],
            label_visibility="collapsed",
        )
        if uploaded:
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:0.75rem;'
                f'color:#00e5ff;margin-top:0.4rem">📎 {uploaded.name} '
                f'({uploaded.size:,} bytes)</div>',
                unsafe_allow_html=True,
            )
    else:
        custom_text = st.text_area(
            "text", height=150,
            placeholder="Paste or type any text you want to encrypt…",
            label_visibility="collapsed",
        )

with cfg_col:
    st.markdown('<div class="input-card-title">⚙ Algorithm settings</div>', unsafe_allow_html=True)
    aes_key_size = st.selectbox("AES Key Size", [128, 192, 256], index=2,
                                help="256-bit is the strongest and recommended.")
    aes_mode = st.selectbox(
        "AES Mode", ["CBC", "CFB", "OFB", "CTR", "GCM"], index=0,
        help="GCM = Authenticated Encryption (recommended for production). CBC is the classic block mode.",
    )
    des_mode = st.selectbox("DES Mode", ["CBC", "CFB", "OFB"], index=0,
                            help="DES is legacy — included for comparison only.")
    if aes_mode == "GCM":
        st.markdown(
            '<div style="font-family:JetBrains Mono,monospace;font-size:0.7rem;'
            'color:#c084fc;margin-top:0.4rem;line-height:1.7">'
            '🔏 <b>GCM</b> provides both encryption <i>and</i> integrity.<br>'
            'The 128-bit auth tag detects any tampering.</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f'<div style="font-family:JetBrains Mono,monospace;font-size:0.68rem;'
        f'color:#6b7280;margin-top:0.5rem;line-height:1.8">'
        f'Output folder:<br>'
        f'<span style="color:#ffc800">{OUTPUT_DIR}</span></div>',
        unsafe_allow_html=True,
    )

# ═════════════════════════════════════════════════════════════════════════════
# STEP INDICATOR + ACTION BUTTONS
# ═════════════════════════════════════════════════════════════════════════════
step_indicator(S.stage_encrypted, S.stage_decrypted, S.stage_verified)

b1, b2, b3, b4 = st.columns([1, 1, 1, 0.5])
with b1: encrypt_btn = st.button("🔒  Encrypt",  use_container_width=True)
with b2: decrypt_btn = st.button("🔓  Decrypt",  use_container_width=True, disabled=not S.stage_encrypted)
with b3: verify_btn  = st.button("✅  Verify",   use_container_width=True, disabled=not S.stage_decrypted)
with b4: reset_btn   = st.button("↺ Reset",     use_container_width=True)

st.markdown("---")

# ── Reset ─────────────────────────────────────────────────────────────────────
if reset_btn:
    for k, v in _def.items():
        st.session_state[k] = v
    st.rerun()

# ── Plaintext resolver ────────────────────────────────────────────────────────
def get_plaintext():
    if source == "Upload a file" and uploaded:
        return uploaded.read(), uploaded.name
    if source == "Enter text manually" and custom_text and custom_text.strip():
        return custom_text.encode(), "input.txt"
    return None, None

# ════════════════════════════════════════════════════════════════════
# ENCRYPT
# ════════════════════════════════════════════════════════════════════
if encrypt_btn:
    plain, fn = get_plaintext()
    if not plain:
        st.warning("⚠️  Please provide input: upload a file or enter some text first.")
    else:
        with st.spinner("Generating keys and encrypting with AES and DES…"):
            aes_key = generate_aes_key(aes_key_size)
            t0 = time.perf_counter()
            if aes_mode == "GCM":
                aes_enc, aes_meta = encrypt_aes_gcm(plain, aes_key)
            else:
                aes_enc, aes_meta = encrypt_aes(plain, aes_key, aes_mode)
            aes_enc_t = time.perf_counter() - t0

            des_key = generate_des_key()
            t0 = time.perf_counter()
            des_enc, des_meta = encrypt_des(plain, des_key, des_mode)
            des_enc_t = time.perf_counter() - t0

            fn_stem = Path(fn).stem
            saved_enc_aes = save_to_output(f"{fn_stem}_aes_encrypted.bin", aes_enc)
            saved_enc_des = save_to_output(f"{fn_stem}_des_encrypted.bin", des_enc)

        S.plaintext=plain; S.filename=fn
        S.aes_key=aes_key; S.des_key=des_key
        S.aes_enc=aes_enc; S.des_enc=des_enc
        S.aes_meta=aes_meta; S.des_meta=des_meta
        S.aes_enc_t=aes_enc_t; S.des_enc_t=des_enc_t
        S.aes_key_size=aes_key_size; S.aes_mode=aes_mode; S.des_mode=des_mode
        S.aes_dec=None; S.des_dec=None; S.aes_ok=None; S.des_ok=None
        S.saved_enc_aes=str(saved_enc_aes); S.saved_enc_des=str(saved_enc_des)
        S.saved_dec_aes=None; S.saved_dec_des=None
        S.stage_encrypted=True; S.stage_decrypted=False; S.stage_verified=False
        S.scroll_to = "step1"   # ← signal scroll target
        st.rerun()

# ════════════════════════════════════════════════════════════════════
# DECRYPT  (Option A — re-read ciphertext from disk before decrypting)
# ════════════════════════════════════════════════════════════════════
if decrypt_btn and S.stage_encrypted:
    # ── Re-read ciphertext bytes fresh from disk ──────────────────────
    # Any on-disk edit is picked up here instead of using stale
    # in-memory bytes from session state.
    aes_enc_disk = load_from_disk(S.saved_enc_aes)
    des_enc_disk = load_from_disk(S.saved_enc_des)

    if aes_enc_disk is None or des_enc_disk is None:
        st.stop()   # load_from_disk already showed the error

    with st.spinner("Decrypting both ciphertexts…"):
        t0 = time.perf_counter()
        try:
            if S.aes_mode == "GCM":
                # GCM will raise ValueError itself if the tag doesn't
                # match — tampering is caught here, before Verify.
                aes_dec = decrypt_aes_gcm(aes_enc_disk, S.aes_key, S.aes_meta)
            else:
                aes_dec = decrypt_aes(aes_enc_disk, S.aes_key, S.aes_meta)
        except ValueError as exc:
            st.error(f"🔴 AES decryption failed — ciphertext may have been tampered with.\n\n`{exc}`")
            st.stop()
        S.aes_dec_t = time.perf_counter() - t0

        t0 = time.perf_counter()
        des_dec = decrypt_des(des_enc_disk, S.des_key, S.des_meta)
        S.des_dec_t = time.perf_counter() - t0

        fn_stem = Path(S.filename).stem
        fn_ext  = Path(S.filename).suffix or ".txt"
        saved_dec_aes = save_to_output(f"{fn_stem}_aes_decrypted{fn_ext}", aes_dec)
        saved_dec_des = save_to_output(f"{fn_stem}_des_decrypted{fn_ext}", des_dec)

    S.aes_dec=aes_dec; S.des_dec=des_dec
    S.saved_dec_aes=str(saved_dec_aes); S.saved_dec_des=str(saved_dec_des)
    S.aes_ok=None; S.des_ok=None
    S.stage_decrypted=True; S.stage_verified=False
    S.scroll_to = "step2"   # ← signal scroll target
    st.rerun()

# ════════════════════════════════════════════════════════════════════
# VERIFY
# ════════════════════════════════════════════════════════════════════
if verify_btn and S.stage_decrypted:
    S.aes_ok = verify_files(S.plaintext, S.aes_dec)
    S.des_ok = verify_files(S.plaintext, S.des_dec)
    S.stage_verified = True
    S.scroll_to = "step3"   # ← signal scroll target
    st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# DISPLAY RESULTS
# ═════════════════════════════════════════════════════════════════════════════

if not S.stage_encrypted:
    st.markdown("""
    <div style="text-align:center;padding:3.5rem 2rem;color:#6b7280">
        <div style="font-size:3.2rem;margin-bottom:1rem">🔑</div>
        <div style="font-size:1rem;font-weight:600;color:#9ca3af;margin-bottom:0.4rem">Ready to begin</div>
        <div style="font-size:0.84rem">
            Provide your input above, then press <b style="color:#00e5ff">🔒 Encrypt</b>.
        </div>
    </div>""", unsafe_allow_html=True)

# ── STEP 1 ────────────────────────────────────────────────────────
if S.stage_encrypted:
    section("Step 1 — Encryption Results", anchor_id="step1")

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Original Size",  f"{len(S.plaintext):,} B")
    with c2: metric_card("AES Ciphertext", f"{len(S.aes_enc):,} B", "aes-color")
    with c3: metric_card("DES Ciphertext", f"{len(S.des_enc):,} B", "des-color")
    with c4: metric_card("Size Δ", f"{abs(len(S.aes_enc)-len(S.des_enc))} B", "ok-color")

    el, er = st.columns(2, gap="large")
    for col, label, color, bk, enc_bytes, enc_t, key_bytes, meta, ks, bs, mode, saved_path in [
        (el, "AES", "#00e5ff", "aes" if S.aes_mode != "GCM" else "gcm",
         S.aes_enc, S.aes_enc_t, S.aes_key, S.aes_meta,
         f"{S.aes_key_size} bits", "128 bits (16 B)", S.aes_mode, S.saved_enc_aes),
        (er, "DES", "#ff6b35", "des", S.des_enc, S.des_enc_t, S.des_key, S.des_meta,
         "56 bits eff.", "64 bits (8 B)", S.des_mode, S.saved_enc_des),
    ]:
        with col:
            iv_hex = (meta.get("iv","") or meta.get("nonce","") or "").upper()
            fp = key_fingerprint(key_bytes)
            gcm_tag = meta.get("tag", "")
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.9rem">
                <span style="font-size:1.3rem;font-weight:800;color:{color}">{label}</span>
                {badge(mode, bk)}
            </div>
            <table class="info-table">
                <tr><td>Key size</td><td>{ks}</td></tr>
                <tr><td>Block size</td><td>{bs}</td></tr>
                <tr><td>Mode</td><td>{mode}</td></tr>
                <tr><td>Key fingerprint</td>
                    <td><span class="fp-pill">{fp}</span></td></tr>
                <tr><td>Key (hex)</td>
                    <td style="font-family:'JetBrains Mono',monospace;font-size:0.66rem;word-break:break-all">
                    {key_bytes.hex().upper()[:48]}…</td></tr>
                <tr><td>IV / Nonce</td>
                    <td style="font-family:'JetBrains Mono',monospace;font-size:0.66rem;word-break:break-all">
                    {(iv_hex[:48]+"…") if iv_hex else "—"}</td></tr>
                {"<tr><td>Auth tag (GCM)</td><td><span class='tag-pill'>" + gcm_tag[:32] + "…</span></td></tr>" if gcm_tag else ""}
                <tr><td>Encryption time</td><td style="color:{color}">{fmt_time(enc_t)}</td></tr>
                <tr><td>Ciphertext size</td><td>{len(enc_bytes):,} bytes</td></tr>
            </table>
            <div style="margin:0.8rem 0 0.3rem;font-size:0.7rem;color:#6b7280;
                font-family:JetBrains Mono,monospace;letter-spacing:.1em;text-transform:uppercase">
                Ciphertext — Base64 preview</div>""", unsafe_allow_html=True)
            st.markdown(f'<div class="cipher-box">{cipher_preview(enc_bytes)}</div>', unsafe_allow_html=True)
            copy_button(f"{label} ciphertext", enc_bytes)

            if saved_path:
                st.markdown(
                    f'<div style="margin-top:0.6rem;font-size:0.72rem;color:#6b7280;'
                    f'font-family:JetBrains Mono,monospace">💾 Saved to:</div>'
                    f'<div class="saved-path">{saved_path}</div>',
                    unsafe_allow_html=True,
                )

    section("Encryption Time")
    t1, t2 = st.columns([1, 2])
    with t1: bar_chart("AES", S.aes_enc_t, "#00e5ff", "DES", S.des_enc_t, "#ff6b35")
    with t2:
        faster = "AES" if S.aes_enc_t < S.des_enc_t else "DES"
        ratio  = max(S.aes_enc_t, S.des_enc_t) / max(min(S.aes_enc_t, S.des_enc_t), 1e-12)
        st.info(f"⚡ **{faster}** was faster at encryption by ×{ratio:.1f}\n\n"
                f"AES: {fmt_time(S.aes_enc_t)} · DES: {fmt_time(S.des_enc_t)}")

    if not S.stage_decrypted:
        st.markdown(
            '<div class="hint-box" style="border:1px dashed rgba(255,107,53,0.35);color:#ff6b35;">'
            '▶ Press <b>🔓 Decrypt</b> to recover the original data from both ciphertexts.</div>',
            unsafe_allow_html=True,
        )

# ── STEP 2 ────────────────────────────────────────────────────────
if S.stage_decrypted:
    section("Step 2 — Decryption Results", anchor_id="step2")

    dl, dr = st.columns(2, gap="large")
    for col, label, color, dec_bytes, dec_t, saved_path in [
        (dl, "AES", "#00e5ff", S.aes_dec, S.aes_dec_t, S.saved_dec_aes),
        (dr, "DES", "#ff6b35", S.des_dec, S.des_dec_t, S.saved_dec_des),
    ]:
        with col:
            size_ok = len(dec_bytes) == len(S.plaintext)
            orig_hash = compute_sha256(S.plaintext)
            dec_hash  = compute_sha256(dec_bytes)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.9rem">
                <span style="font-size:1.2rem;font-weight:700;color:{color}">{label} — Decrypted</span>
            </div>
            <table class="info-table">
                <tr><td>Decrypted size</td><td>{len(dec_bytes):,} bytes</td></tr>
                <tr><td>Decryption time</td><td style="color:{color}">{fmt_time(dec_t)}</td></tr>
                <tr><td>Original size</td><td>{len(S.plaintext):,} bytes</td></tr>
                <tr><td>Size match</td>
                    <td>{badge("✓ MATCH","ok") if size_ok else badge("✗ MISMATCH","fail")}</td></tr>
                <tr><td>SHA-256 (orig)</td>
                    <td style="font-family:'JetBrains Mono',monospace;font-size:0.66rem">{orig_hash[:24]}…</td></tr>
                <tr><td>SHA-256 (dec)</td>
                    <td style="font-family:'JetBrains Mono',monospace;font-size:0.66rem;
                        color:{'#39ff14' if orig_hash==dec_hash else '#ff4444'}">{dec_hash[:24]}…</td></tr>
            </table>
            <div style="margin:0.8rem 0 0.3rem;font-size:0.7rem;color:#6b7280;
                font-family:JetBrains Mono,monospace;letter-spacing:.1em;text-transform:uppercase">
                Decrypted content preview</div>""", unsafe_allow_html=True)
            try:
                st.code(dec_bytes.decode("utf-8")[:300], language="text")
            except Exception:
                st.markdown(f'<div class="cipher-box">{cipher_preview(dec_bytes)}</div>',
                            unsafe_allow_html=True)

            if saved_path:
                st.markdown(
                    f'<div style="margin-top:0.4rem;font-size:0.72rem;color:#6b7280;'
                    f'font-family:JetBrains Mono,monospace">💾 Saved to:</div>'
                    f'<div class="saved-path">{saved_path}</div>',
                    unsafe_allow_html=True,
                )

    section("Decryption Time")
    t1, t2 = st.columns([1, 2])
    with t1: bar_chart("AES", S.aes_dec_t, "#00e5ff", "DES", S.des_dec_t, "#ff6b35")
    with t2:
        faster = "AES" if S.aes_dec_t < S.des_dec_t else "DES"
        ratio  = max(S.aes_dec_t, S.des_dec_t) / max(min(S.aes_dec_t, S.des_dec_t), 1e-12)
        st.info(f"⚡ **{faster}** was faster at decryption by ×{ratio:.1f}\n\n"
                f"AES: {fmt_time(S.aes_dec_t)} · DES: {fmt_time(S.des_dec_t)}")

    if not S.stage_verified:
        st.markdown(
            '<div class="hint-box" style="border:1px dashed rgba(57,255,20,0.35);color:#39ff14;">'
            '▶ Press <b>✅ Verify</b> to confirm the decrypted data matches the original exactly.</div>',
            unsafe_allow_html=True,
        )

# ── STEP 3 ────────────────────────────────────────────────────────
if S.stage_verified:
    section("Step 3 — Verification", anchor_id="step3")

    vc1, vc2 = st.columns(2, gap="large")
    for col, label, ok, dec_bytes in [
        (vc1, "AES", S.aes_ok, S.aes_dec),
        (vc2, "DES", S.des_ok, S.des_dec),
    ]:
        with col:
            cls   = "verify-ok" if ok else "verify-fail"
            color = "#39ff14" if ok else "#ff4444"
            icon  = "✅" if ok else "❌"
            msg   = "Decryption successful: original data matched" if ok else "Decryption FAILED: data mismatch"
            orig_hash = compute_sha256(S.plaintext)
            dec_hash  = compute_sha256(dec_bytes)
            st.markdown(f"""
            <div class="verify-banner {cls}">
                <div class="verify-title" style="color:{color}">{icon} {label} — {msg}</div>
                <div class="verify-sub">
                    Original SHA-256 &nbsp;&nbsp;: {orig_hash[:36]}…<br>
                    Decrypted SHA-256: {dec_hash[:36]}…<br>
                    Hash match &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {"✓ YES — byte-identical" if ok else "✗ NO — mismatch detected"}
                </div>
            </div>""", unsafe_allow_html=True)

    # Full summary table
    section("Full Comparison Summary")
    st.markdown(f"""
    <table class="info-table" style="font-size:0.85rem">
        <tr style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#6b7280;text-transform:uppercase">
            <td>Property</td>
            <td style="color:#00e5ff">AES</td>
            <td style="color:#ff6b35">DES</td>
        </tr>
        <tr><td>Key size</td>       <td>{S.aes_key_size} bits</td>  <td>56 bits (eff.)</td></tr>
        <tr><td>Block size</td>     <td>128 bits</td>                <td>64 bits</td></tr>
        <tr><td>Mode</td>           <td>{S.aes_mode}</td>            <td>{S.des_mode}</td></tr>
        <tr><td>Authenticated</td>  <td>{"✓ Yes (GCM tag)" if S.aes_mode=="GCM" else "✗ No (use GCM)"}</td><td>✗ No</td></tr>
        <tr><td>Original size</td>  <td colspan="2">{len(S.plaintext):,} bytes</td></tr>
        <tr><td>Ciphertext size</td><td>{len(S.aes_enc):,} B</td>   <td>{len(S.des_enc):,} B</td></tr>
        <tr><td>Encryption time</td>
            <td style="color:#00e5ff">{fmt_time(S.aes_enc_t)}</td>
            <td style="color:#ff6b35">{fmt_time(S.des_enc_t)}</td></tr>
        <tr><td>Decryption time</td>
            <td style="color:#00e5ff">{fmt_time(S.aes_dec_t)}</td>
            <td style="color:#ff6b35">{fmt_time(S.des_dec_t)}</td></tr>
        <tr><td>Verification</td>
            <td>{badge("✓ PASSED","ok")  if S.aes_ok else badge("✗ FAILED","fail")}</td>
            <td>{badge("✓ PASSED","ok")  if S.des_ok else badge("✗ FAILED","fail")}</td></tr>
        <tr><td>Security status</td>
            <td>{badge("✓ Secure","ok")}</td>
            <td>{badge("⚠ Deprecated","warn")}</td></tr>
    </table>""", unsafe_allow_html=True)

    # Saved files summary
    section("Saved Output Files")
    files = [
        (S.saved_enc_aes, "AES ciphertext"),
        (S.saved_enc_des, "DES ciphertext"),
        (S.saved_dec_aes, "AES decrypted"),
        (S.saved_dec_des, "DES decrypted"),
    ]
    for path, label in files:
        if path:
            exists = Path(path).exists()
            size   = Path(path).stat().st_size if exists else 0
            icon   = "✅" if exists else "❌"
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:0.7rem;margin:0.4rem 0;'
                f'font-family:JetBrains Mono,monospace;font-size:0.75rem">'
                f'<span>{icon}</span>'
                f'<span style="color:#9ca3af;min-width:130px">{label}</span>'
                f'<span class="saved-path" style="margin-top:0">{path}</span>'
                f'<span style="color:#6b7280;margin-left:auto">{size:,} B</span>'
                f'</div>', unsafe_allow_html=True)

    # Security notes
    section("Security Notes")
    sn1, sn2 = st.columns(2)
    with sn1:
        gcm_note = ("<li><b>GCM mode</b>: authenticated — detects tampering via 128-bit tag</li>"
                    if S.aes_mode == "GCM" else
                    "<li>Consider <b>GCM mode</b> for authenticated encryption in production</li>")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">AES {badge(S.aes_mode, 'aes' if S.aes_mode!='GCM' else 'gcm')}</div>
            <ul style="font-size:0.83rem;line-height:1.9;margin:0.5rem 0 0 1rem;color:#d1d5db">
                <li>NIST standard since 2001</li>
                <li>{S.aes_key_size}-bit key — brute-force infeasible</li>
                <li>Resistant to all known practical attacks</li>
                {gcm_note}
                <li>Random IV/nonce generated fresh per encryption</li>
            </ul>
        </div>""", unsafe_allow_html=True)
    with sn2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">DES {badge(S.des_mode,'des')} {badge('⚠ Legacy','fail')}</div>
            <ul style="font-size:0.83rem;line-height:1.9;margin:0.5rem 0 0 1rem;color:#d1d5db">
                <li>56-bit key — crackable in &lt;24 hours today</li>
                <li>Deprecated by NIST in 2005</li>
                <li><b>Not secure</b> for real-world use</li>
                <li>Included for <em>educational comparison only</em></li>
                <li>Use 3DES or AES in production</li>
            </ul>
        </div>""", unsafe_allow_html=True)

# ── Auto-scroll after action ──────────────────────────────────────────────────
if S.scroll_to:
    inject_scroll(S.scroll_to)
    S.scroll_to = None   # consume the scroll signal