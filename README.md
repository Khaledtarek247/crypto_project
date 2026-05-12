# CryptoLab: Algorithm Comparison (Path 2)

CryptoLab is a Streamlit app that encrypts the same input with AES and DES, then compares output size, speed, and integrity verification results.

This project is intended for education and demonstration.

## What This Project Does

- Encrypts one input with AES and DES side by side
- Decrypts both ciphertexts
- Verifies decrypted data against the original
- Shows timing and algorithm/security comparison in a visual UI
- Saves encrypted and decrypted files in the output folder

## Algorithms and Modes

### AES
- Key sizes: 128, 192, 256 bits
- Modes: CBC, CFB, OFB, CTR, GCM

### DES
- Effective key size: 56 bits
- Modes: CBC, CFB, OFB

## Important Security Note

DES is deprecated and included only for learning comparison.
AES is the modern secure option.

GCM mode in AES provides both:
- confidentiality (encryption)
- integrity (tamper detection through authentication tag)

## Professional Project Structure

The project has been restructured to keep architecture clearer without changing cryptographic behavior.

```text
crypto_project/
├─ main.py                  # Streamlit app entry point
├─ app/
│  ├─ __init__.py
│  ├─ session_state.py      # Session defaults and initialization
│  └─ storage.py            # Output directory and file persistence helpers
├─ core/
│  ├─ __init__.py
│  └─ crypto_utils.py       # Core encryption/decryption and hashing logic
├─ output/                  # Generated encrypted/decrypted files
├─ requirements.txt
└─ README.md
```

## Why This Structure Is Better

- Clear separation of concerns:
	- UI workflow in main.py
	- app-level utilities in app/
	- cryptography engine in core/
- Easier future testing and maintenance

## Installation

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the App

```bash
streamlit run main.py
```

## App Workflow

1. Choose input source:
	 - Upload a file, or
	 - Enter text manually
2. Select AES key size and mode
3. Select DES mode
4. Click Encrypt
5. Click Decrypt
6. Click Verify

## Output Files

Generated files are saved in output/.

Examples:
- input_aes_encrypted.bin
- input_des_encrypted.bin
- input_aes_decrypted.txt
- input_des_decrypted.txt

## Verification Logic

The app validates decryption in two ways:
- byte-for-byte comparison
- SHA-256 hash comparison

For AES-GCM, tampering is also detected during decryption via tag verification.

## Dependencies

- streamlit
- pycryptodome

See requirements.txt for versions.

## Current Scope

- Built for learning, benchmarking, and comparison reports
- Not a production key-management system
- Performance values depend on local machine and run conditions

## License / Usage

Use this project for academic and educational purposes.
