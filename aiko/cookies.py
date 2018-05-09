from http.cookies import BaseCookie
from typing import Any, cast, List, Optional


class Cookies(BaseCookie):
    """
    重载 BaseCookie 保持 koa api
    """

    def __delitem__(self, key: str) -> None:
        """
        删除cookie 内容设置为空，并把超时设置为0
        """
        self[key] = ""
        self[key]["max-age"] = "0"
        # super().__delitem__(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        BaseCookie 会自动创建一个 cookie 对象，设置到 value
        """
        super().__setitem__(key, value)

    def __getitem__(self, key: str) -> Any:
        """
        获取一个 cookie 对象
        """
        return super().__getitem__(key)

    def get(self, key: Any, default: Any = None) -> Any:
        """
        获取 cookie 中的 value
        """
        if key in self:
            return self[key].value
        return default

    def set(self, key: str, value: str, opt: dict = None) -> None:
        """
        设置 cookie.value 并设置属性
        """
        self[key] = value
        if opt is not None:
            self[key].update(opt)

    def __iter__(self) -> Any:
        """
        mypy 不重载会检查不通过
        """
        return super().__iter__()

    def __len__(self) -> int:
        """
        mypy 不重载会检查不通过
        """
        return super().__len__()

    def headers(self) -> Optional[List[str]]:
        """
        生成 headers
        """
        if len(self) == 0:
            return None
        headers = cast(List[str], [])
        for cookie in self.values():
            headers.append(cookie.OutputString())
        return headers
