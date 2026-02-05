import hashlib
import struct

# Adapted from 
# https://github.com/astral-sh/ruff/blob/8d4d782e16b126d89a2a6d43bdcaa5450d67b804/crates/ruff_db/src/diagnostic/render/gitlab.rs#L158
def fingerprint(string: str, salt: int = 0):
    # pack salt as unsigned 64-bit little-endian (choose endianness and stick with it)
    m = hashlib.sha256()
    m.update(struct.pack('<Q', salt))
    m.update(string.encode('utf8'))
    # take first 8 bytes and turn into a hex string (same shape as Rust's "{:x}" for a u64)
    val = int.from_bytes(m.digest()[:8], 'little')
    return format(val, 'x')