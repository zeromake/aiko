from http.cookies import BaseCookie
from typing import Any, List, Optional


class Cookies(BaseCookie):

    def __delitem__(self, key: str) -> None:
        self[key] = ""
        self[key]["max-age"] = "0"
        # super().__delitem__(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        super().__setitem__(key, value)

    def __getitem__(self, key: str) -> Any:
        return super().__getitem__(key)

    def get(self, key: Any, default: Any = None) -> Any:
        if key in self:
            return self[key].value
        else:
            return default

    def __iter__(self) -> Any:
        return super().__iter__()

    def __len__(self) -> int:
        return super().__len__()

    def headers(self) -> Optional[List[str]]:
        if len(self) == 0:
            return None
        headers: List[str] = []
        for cookie in self.values():
            headers.append(cookie.OutputString())
        return headers
