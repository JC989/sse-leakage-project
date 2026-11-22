# What Can Encrypted Searches Reveal?

A Python project investigating whether a server can guess search keywords from encrypted search result counts and separate reference data.

We will compare guessing accuracy with and without padding and measure the extra storage and bandwidth.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The crypto module requires `cryptography`. Keep dependencies in `requirements.txt` and add `.venv/` to `.gitignore`.

## Generate the Data

Place `generate.py` and `vocab.json` in the same folder. From that folder, run:

```bash
python generate.py
```

The script creates or overwrites:

| File | Contents |
|---|---|
| `private.json` | 500 private records for the search system |
| `reference.json` | 500 separately generated records for the attacker |
| `vocabulary.json` | Candidate words, sampling weights and generation settings |

Each record contains 5–15 unique words. The private and reference collections use the same sampling distribution but different saved random seeds.

Running the same code with the same settings reproduces the data.

**Note:** `vocab.json` is the input vocabulary. `vocabulary.json` is a generated output. Keep the input file.

## Data Format

Each dataset contains metadata and a `records` field:

```python
import json

with open("private.json") as file:
    private_records = json.load(file)["records"]
```

Each record is a list of words. Its position in the list can serve as its record ID for the initial prototype.

Sampling weights determine how likely words are to be selected. They are not the fraction of records containing each word.

The attack calculates that fraction from the reference records:

```text
word occurrence rate =
    number of reference records containing the word
    / total number of reference records
```

Some vocabulary words may not appear in a collection. Their occurrence count is zero.

## Cryptographic Helpers

`crypto.py` provides:

| Function | Purpose |
|---|---|
| `generate_master_key()` | Generates a random 32-byte master key |
| `derive_keys(master_key)` | Derives separate token and encryption keys |
| `make_token(token_key, keyword)` | Creates an HMAC-SHA256 search token |
| `encrypt(encryption_key, plaintext, associated_data)` | Encrypts bytes using AES-GCM |
| `decrypt(encryption_key, blob, associated_data)` | Authenticates and decrypts bytes |

Normalize keywords consistently before creating tokens. The same keyword and token key produce the same token.

Encryption uses a fresh random nonce and returns:

```text
nonce || ciphertext || authentication tag
```

Decryption requires the same encryption key and associated data. Associated data is authenticated but not encrypted.

Keep secret keys on the client.

## Planned Experiment

1. Generate the private and reference collections.
2. Build an encrypted index mapping search tokens to encrypted record IDs.
3. Run searches and collect token/result-count pairs.
4. Give the attack the reference records, candidate vocabulary, private record count and observed token/count pairs.
5. Guess keywords by comparing occurrence rates.
6. Score guesses against the true keywords in a separate evaluator.
7. Repeat with padding and compare accuracy, storage and bandwidth.

The guessing function must not receive secret keys, private records or the true token-to-keyword mapping.

For the baseline experiment, query each candidate once. A fixed keyword guess then achieves accuracy of `1 / number_of_candidates`.

## Current Scope

The data generator and crypto helpers are building blocks. A complete experiment also needs:

- Encrypted index construction and lookup
- Keyword guessing
- Accuracy evaluation
- An integration script

Padding and weighted rewards for guessing sensitive keywords are later extensions.

PIR and differential privacy are literature-review topics. They are not implemented by these files.

## Testing

Before reporting results:

- Confirm the expected record counts and no repeated words within a record.
- Check encrypted lookup against known matches in a small dataset.
- Verify encryption and decryption with matching keys and associated data.
- Confirm that tampered encrypted data fails authentication.
- Test scoring with deliberately correct and incorrect guesses.
- Save dataset settings, random seeds, candidate count and baseline with each result.

## Limitations

The records are synthetic. Results describe this experimental setup, not measured privacy risks for real medical or business records.