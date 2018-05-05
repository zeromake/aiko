# -*- coding: utf-8 -*-

__all__ = [
    "decode_bytes",
    "encode_str",
]


DEFAULT_CODING = 'latin-1'


def decode_bytes(data: bytes, encoding: str = DEFAULT_CODING, errors: str = 'strict') -> str:
    """
    集中调用 decode
    """
    return data.decode(encoding, errors)


def encode_str(data: str, encoding: str = DEFAULT_CODING, errors: str = 'strict') -> bytes:
    """
    集中调用 encode
    """
    return data.encode(encoding, errors)
