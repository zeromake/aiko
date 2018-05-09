from typing import Any, cast

import pytest

from aiko.utils import ProxyAttr


class A(object):
    def __init__(self) -> None:
        self._test1 = 1

    @property
    def test1(self) -> int:
        return self._test1

    @test1.setter
    def test1(self, val: int) -> None:
        self._test1 = val

    def test(self) -> int:
        return 0


class B(object):
    def __init__(self, a: A) -> None:
        self._a = a


def test_get_proxy() -> None:
    c_cls = type('C', (B, ), {})
    proxy = ProxyAttr(c_cls, '_a')\
        .getter('test1')
    a = A()
    c = c_cls(a)
    assert c.test1 == 1 == a.test1
    with pytest.raises(AttributeError):
        c.test1 = 5
    proxy.setter('test1')
    assert c.test1 == 1 == a.test1
    c.test1 = 5
    assert c.test1 == 5 == a.test1

    proxy.access('test1', 'test2')
    # reuse property
    assert cast(Any, c_cls).test2 is cast(Any, c_cls).test1
    assert c.test2 == 5 == a.test1
    c.test2 = 1
    assert c.test2 == 1 == a.test1

    proxy.method('test')
    assert c.test is not a.test
    assert c.test() == a.test()

    proxy.method('test', 'test3')
    # reuse proxy method
    assert cast(Any, c_cls).test is cast(Any, c_cls).test3
    # assert test3 == test
    assert c.test3 is not a.test
    assert c.test3() == a.test()
