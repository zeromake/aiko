# -*- coding: utf-8 -*-
import asyncio
from typing import Any


__all__ = [
    "decode_bytes",
    "encode_str",
    "DEFAULT_CODING",
    "DEFAULT_REQUEST_CODING",
    "DEFAULT_RESPONSE_CODING",
    "DEFAULT_HTTP_VERSION",
]


DEFAULT_CODING = 'latin-1'
DEFAULT_HTTP_VERSION = "1.1"
DEFAULT_REQUEST_CODING = DEFAULT_CODING
DEFAULT_RESPONSE_CODING = "utf-8"


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


@asyncio.coroutine
def handle_async_gen(gen: Any, gen_obj: Any) -> Any:
    """
    处理异步生成器
    """
    if gen is None:
        return
    if asyncio.iscoroutine(gen):
        try:
            temp = yield from gen
            gen_obj.send(temp)
            return
        except Exception as e:
            try:
                gen = gen_obj.throw(e)
                return (yield from handle_async_gen(gen, gen_obj))
            except StopIteration:
                return None
    else:
        return gen
