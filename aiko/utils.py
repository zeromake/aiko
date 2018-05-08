# -*- coding: utf-8 -*-
import asyncio
from typing import Any, Set


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


class ProxyAttr(object):
    def __init__(self, proto: Any, target: str) -> None:
        self._proto = proto
        self._target = target
        self._method: Set[str] = set()
        self._getter: Set[str] = set()
        self._setter: Set[str] = set()

    def method(self, name: str) -> 'ProxyAttr':
        def method_(self2: Any, *args: Any, **kwargs: Any) -> Any:
            return getattr(getattr(self2, self._target), name)(*args, **kwargs)

        setattr(self._proto, name, method_)
        self._method.add(name)
        return self

    def getter(self, name: str) -> 'ProxyAttr':
        def get(self2: Any) -> None:
            target_ = getattr(self2, self._target)
            return getattr(target_, name)

        setattr(self._proto, name, property(get))
        self._getter.add(name)
        return self

    def setter(self, name: str) -> 'ProxyAttr':
        def set(self2: Any, val: Any) -> None:
            target_ = getattr(self2, self._target)
            setattr(target_, name, val)

        setattr(self._proto, name, property(None, set))
        self._setter.add(name)
        return self

    def access(self, name: str) -> 'ProxyAttr':
        def get(self2: Any) -> Any:
            target_ = getattr(self2, self._target)
            return getattr(target_, name)

        def set(self2: Any, val: Any) -> None:
            target_ = getattr(self2, self._target)
            setattr(target_, name, val)

        setattr(self._proto, name, property(get, set))
        self._getter.add(name)
        self._setter.add(name)
        return self
