"""The xz seal: canonical compression for a finished phext.

Ported 1:1 from libphext-rs 0.6.0 (src/seal.rs). Python's `lzma` is
stdlib — no new dependency.

Compression is a seal, not a working format. A phext is authored,
edited, and queried as plain text; when a phext is finished — archived,
published, or transported — it may be sealed: xz-compressed as a whole.
Unsealing restores the exact original bytes.

Seal specification:
* The seal is a standard xz stream (liblzma) over the phext's exact
  bytes. Decoders in any implementation must accept any valid xz stream.
* This implementation encodes at preset 6. The preset is an encoder
  choice, not a format requirement; seals produced at other presets
  unseal identically.
* Sealing is deterministic for a given encoder and preset: the same
  phext bytes seal to the same sealed bytes.
"""

import lzma

SEAL_PRESET = 6


def seal(text: str) -> bytes:
    """Seals a phext: xz-compresses its full UTF-8 bytes."""
    return seal_bytes(text.encode("utf-8"))


def seal_bytes(data: bytes) -> bytes:
    """Seals raw phext bytes (see `seal`)."""
    return lzma.compress(data, format=lzma.FORMAT_XZ, preset=SEAL_PRESET)


def unseal(data: bytes) -> bytes:
    """Unseals a sealed phext back to its exact original bytes. Raises
    `lzma.LZMAError` when the data is not a valid xz stream."""
    return lzma.decompress(data, format=lzma.FORMAT_XZ)


def unseal_string(data: bytes) -> str:
    """Unseals directly to text. Raises when the unsealed bytes are not
    valid UTF-8; to unseal foreign content that may carry non-UTF-8
    scrolls, `unseal` to bytes and pass them through
    `phext.binary.ingest`, which applies the base64-verbatim ingestion
    rule instead of failing."""
    return unseal(data).decode("utf-8")
