"""
ByteC - A simple byte encoding/decoding utility.
"""


def to_hex(data: bytes) -> str:
    """Convert bytes to a hex string."""
    return data.hex()


def from_hex(hex_str: str) -> bytes:
    """Convert a hex string back to bytes."""
    return bytes.fromhex(hex_str)


def to_binary(data: bytes) -> str:
    """Convert bytes to a space-separated binary string."""
    return " ".join(format(b, "08b") for b in data)


def from_binary(binary_str: str) -> bytes:
    """Convert a space-separated binary string back to bytes."""
    return bytes(int(b, 2) for b in binary_str.split())


def encode(text: str, encoding: str = "utf-8") -> bytes:
    """Encode a string to bytes."""
    return text.encode(encoding)


def decode(data: bytes, encoding: str = "utf-8") -> str:
    """Decode bytes to a string."""
    return data.decode(encoding)
