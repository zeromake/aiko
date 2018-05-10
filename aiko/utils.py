# -*- coding: utf-8 -*-
"""
各种工具
"""
import asyncio
from datetime import datetime
from typing import Any, cast, Dict, List, Optional, Set, Union

__all__ = [
    "decode_bytes",
    "encode_str",
    "DEFAULT_CODING",
    "DEFAULT_REQUEST_CODING",
    "DEFAULT_RESPONSE_CODING",
    "DEFAULT_HTTP_VERSION",
    "HEADER_TYPE",
    "ISO_DATE_FORMAT",
    "STATIC_METHODS",
]


DEFAULT_CODING = 'latin-1'
DEFAULT_HTTP_VERSION = "1.1"
DEFAULT_REQUEST_CODING = DEFAULT_CODING
DEFAULT_RESPONSE_CODING = "utf-8"
HEADER_TYPE = Dict[str, Union[str, List[str]]]
ISO_DATE_FORMAT = r"%a, %d %b %Y %H:%M:%S %Z"
STATIC_METHODS = ('GET', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'TRACE')


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
        return None
    if asyncio.iscoroutine(gen):
        try:
            temp = yield from gen
            gen_obj.send(temp)
            return
        except Exception as error:
            try:
                gen = gen_obj.throw(error)
                return (yield from handle_async_gen(gen, gen_obj))
            except StopIteration:
                return None
    else:
        return gen


def parse_http_date(date: str) -> int:
    """
    解析http时间到 timestamp
    """
    try:
        return int(
            datetime.strptime(
                date,
                ISO_DATE_FORMAT,
            ).timestamp(),
        )
    except ValueError:
        return 0


def fresh(req_headers: HEADER_TYPE, res_headers: HEADER_TYPE) -> bool:
    """
    根据 req_headers, res_headers 判断改消息是否为 304
    """
    modified_since = cast(
        Optional[str],
        req_headers.get('if-modified-since'),
    )
    none_match = cast(
        Optional[str],
        req_headers.get('if-none-match'),
    )
    if not modified_since and not none_match:
        return False
    cache_control = req_headers.get('cache-control')
    if cache_control is not None:
        if isinstance(cache_control, list):
            for control in cache_control:
                if control.strip() == "no-cache":
                    return False
        elif cache_control.strip() == "no-cache":
            return False
    if none_match is not None and none_match != "*":
        etag = cast(
            Optional[str],
            res_headers.get('ETag') or res_headers.get('etag'),
        )
        if etag is None:
            return False
        if etag.startswith("W/"):
            etag = etag[2:]
        if none_match.startswith("W/"):
            none_match = none_match[2:]
        etag_stale = True
        matches = none_match.split(",")
        for match in matches:
            match = match.strip()
            if match == etag:
                etag_stale = False
                break
        if etag_stale:
            return False
    if modified_since:
        last_modified = cast(
            Optional[str],
            res_headers.get('Last-Modified') or res_headers.get('last-modified'),
        )
        modified_stale = True
        if last_modified is not None:
            last_date = parse_http_date(last_modified)
            modified_date = parse_http_date(modified_since)
            if last_date != 0 and modified_date != 0 and last_date <= modified_date:
                modified_stale = False
        if modified_stale:
            return False
    return True


class ProxyAttr(object):
    """
    代理属性工具
    """
    def __init__(self, proto: Any, target: str) -> None:
        self._proto = proto
        self._target = target
        self._method = cast(Dict[str, Set[str]], {})
        self._getter = cast(Dict[str, Set[str]], {})
        self._setter = cast(Dict[str, Set[str]], {})
        self._func_map = cast(Dict[str, Any], {})

    @property
    def method_map(self) -> Dict[str, Set[str]]:
        """
        代理的method map
        """
        return self._method

    @property
    def getter_map(self) -> Dict[str, Set[str]]:
        """
        代理的getter map
        """
        return self._getter

    @property
    def setter_map(self) -> Dict[str, Set[str]]:
        """
        代理的setter map
        """
        return self._setter

    def reuse_handle(
            self,
            name: str,
            rename: str,
            pmap: Dict[str, Set[str]],
    ) -> bool:
        """
        判断是否复用之前的
        """
        if name in pmap:
            name_map = pmap[name]
            if rename not in name_map:
                name_map.add(rename)
                func = self._func_map[name]
                setattr(self._proto, rename, func)
            return True
        return False

    def method(self, name: str, rename: Optional[str] = None) -> 'ProxyAttr':
        """
        为类设置代理 method
        """
        if rename is None:
            rename = name
        if self.reuse_handle(name, rename, self._method):
            return self

        def proxy_method(self2: Any, *args: Any, **kwargs: Any) -> Any:
            """
            代理 method
            """
            return getattr(getattr(self2, self._target), name)(*args, **kwargs)
        self._func_map[name] = proxy_method
        setattr(self._proto, name, proxy_method)
        self._method[name] = {rename}
        return self

    def getter(self, name: str, rename: Optional[str] = None) -> 'ProxyAttr':
        """
        为类设置代理 getattr
        """
        if rename is None:
            rename = name
        if self.reuse_handle(name, rename, self._getter):
            return self

        def proxy_get(this: Any) -> None:
            """
            代理 getattr
            """
            proxy_target = getattr(this, self._target)
            return getattr(proxy_target, name)

        if name in self._setter:
            func = self._func_map[name]
            func = func.getter(proxy_get)
        else:
            func = property(proxy_get)
            self._func_map[name] = func
        setattr(self._proto, rename, func)
        self._getter[name] = {rename}
        return self

    def setter(self, name: str, rename: Optional[str] = None) -> 'ProxyAttr':
        """
        为类设置代理 setter
        """
        if rename is None:
            rename = name
        if self.reuse_handle(name, rename, self._setter):
            return self

        def proxy_set(this: Any, val: Any) -> None:
            """
            代理 setattr
            """
            proxy_target_ = getattr(this, self._target)
            setattr(proxy_target_, name, val)
        if name in self._getter:
            func = self._func_map[name]
            func = func.setter(proxy_set)
        else:
            func = property(None, proxy_set)
        self._func_map[name] = func
        setattr(self._proto, rename, func)
        self._setter[name] = {rename}
        return self

    def access(self, name: str, rename: Optional[str] = None) -> 'ProxyAttr':
        """
        为类设置代理 getter, setter
        """
        self.getter(name, rename)
        self.setter(name, rename)
        return self

    def __str__(self) -> str:
        return "<method: %s; getattr: %s; setattr: %s>" % (
            self._method,
            self._getter,
            self._setter
        )
