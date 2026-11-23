"""Unpadded encrypted keyword lookup for the generated private records.

    client = SearchClient()
    index = client.build_index(private_records)
    token = client.make_token(keyword)
    encrypted_ids = lookup(index, token)
    record_ids = client.decrypt_ids(encrypted_ids)
"""

from collections.abc import Iterable
from secrets import token_bytes

from cryptography.fernet import Fernet

from .crypto import make_token as make_hmac_token

EncryptedIndex = dict[bytes, list[bytes]]


class SearchClient:
    """Own the search key and the Fernet key for an encrypted index."""

    def __init__(self) -> None:
        self._search_key = token_bytes(32)
        self._fernet = Fernet(Fernet.generate_key())

    def make_token(self, keyword: str) -> bytes:
        """Create a search token after trimming whitespace and folding case."""
        return make_hmac_token(self._search_key, keyword.strip().casefold())

    def build_index(self, private_records: Iterable[Iterable[str]]) -> EncryptedIndex:
        """Encrypt each posting separately, using zero-based record positions as IDs."""
        index: EncryptedIndex = {}
        for record_id, record in enumerate(private_records):
            record_tokens = {self.make_token(word) for word in record}
            encoded_id = str(record_id).encode("ascii")
            for token in record_tokens:
                index.setdefault(token, []).append(self._fernet.encrypt(encoded_id))
        return index

    def decrypt_ids(self, encrypted_ids: Iterable[bytes]) -> list[int]:
        """Authenticate and decrypt the returned record IDs in lookup order."""
        return [int(self._fernet.decrypt(entry)) for entry in encrypted_ids]


def lookup(index: EncryptedIndex, token: bytes) -> list[bytes]:
    """Return the encrypted postings for a token using only server-side data."""
    return index.get(token, []).copy()
