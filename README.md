# 🔐 CryptoLab — Algorithm Comparison (Path 2)

A Streamlit application that encrypts real data using **AES** and **DES** side-by-side, then compares ciphertext output, execution time, key size, block size, and security notes.

---

## Project Structure

```
crypto_project/
├── main.py            # Streamlit UI
├── crypto_utils.py    # Encryption/decryption logic
├── requirements.txt   # Python dependencies
└── README.md
```

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the app
```bash
streamlit run main.py
```

---

## Features

- **Path 2: Algorithm Comparison** — AES vs DES on the same data
- Supports **AES-128 / AES-192 / AES-256** with CBC, CFB, OFB, CTR modes
- Supports **DES** with CBC, CFB, OFB modes
- Three input options: upload a file, paste text, or use a generated sample CSV
- Displays ciphertext side-by-side in Base64 preview
- SHA-256 hash verification of decrypted vs original data
- Visual timing bar charts (encryption & decryption speed)
- Download buttons for ciphertexts and decrypted files
- Security notes explaining why DES is deprecated

---

## Algorithms Used

| Property       | AES                        | DES                     |
|---------------|---------------------------|-------------------------|
| Key size      | 128 / 192 / 256 bits       | 56 bits (64-bit w/ parity) |
| Block size    | 128 bits (16 bytes)        | 64 bits (8 bytes)       |
| Status        | ✅ Modern standard (NIST)  | ⚠️ Deprecated (2005)    |
| Library       | PyCryptodome               | PyCryptodome            |

---

## Security Note

DES is included **for educational comparison only**. Its 56-bit key is vulnerable to brute-force attacks. AES is the recommended algorithm for all modern applications.

---

## Deliverables Covered

- ✅ Source code (main.py, crypto_utils.py)
- ✅ Sample input data (generated CSV or file upload)
- ✅ Encrypted output (downloadable .bin files)
- ✅ Decrypted output (downloadable recovered files)
- ✅ Verification message ("Decryption successful: original data matched")
- ✅ Algorithm comparison (ciphertext size, timing, key details)
