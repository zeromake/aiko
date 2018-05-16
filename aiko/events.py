from functools import partial
from typing import Any, Callable, cast, Dict, List

LISTENER_TYPE = Callable[..., None]


class WrapperTarget(object):
    def __init__(
        self,
        target: 'EventEmitter',
        type: str,
        listener: LISTENER_TYPE,
    ) -> None:
        self.fired = False
        self.wrap_fn = None
        self.target = target
        self.type = type
        self.listener = listener


def once_wrapper(target: WrapperTarget, *args: Any, **kwargs: Any) -> None:
    if not target.fired:
        target.target.remove_listener(
            target.type,
            cast(LISTENER_TYPE, target.wrap_fn),
        )
        target.fired = True
        target.listener(*args, **kwargs)


class EventEmitter(object):
    defaultMaxListeners = 10

    def __init__(self) -> None:
        self._listeners: Dict[str, List[LISTENER_TYPE]] = {}
        self._default_max_listeners = EventEmitter.defaultMaxListeners

    def add_listerner(self, event_name: str, listener: LISTENER_TYPE) -> 'EventEmitter':
        """
        添加一个事件监听
        """
        if event_name in self._listeners:
            listeners: List[LISTENER_TYPE] = self._listeners[event_name]
            if len(listeners) >= self._default_max_listeners:
                return self
            listeners.append(listener)
        else:
            if event_name != "newListener":
                self.emit("newListener")
            self._listeners[event_name] = [listener]
        return self

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> bool:
        """
        触发一个事件
        """
        if event_name in self._listeners:
            listeners: List[LISTENER_TYPE] = self._listeners[event_name]
            for listener in listeners:
                listener(*args, **kwargs)
            return True
        return False

    def event_names(self) -> List[str]:
        """
        获得所有事件名列表
        """
        return cast(List[str], self._listeners.keys())

    def get_max_listeners(self) -> int:
        """
        获得事件数限制
        """
        return self._default_max_listeners

    def listener_count(self, event_name: str) -> int:
        """
        获得事件数量
        """
        return len(self._listeners.get(event_name, ()))

    def listeners(self, event_name: str) -> List[LISTENER_TYPE]:
        """
        获得某个事件的所有事件
        """
        return self._listeners.get(event_name, [])

    def off(self, event_name: str, listener: LISTENER_TYPE) -> 'EventEmitter':
        """
        remove_listener 别名
        """
        return self.remove_listener(event_name, listener)

    def on(self, event_name: str, listener: LISTENER_TYPE) -> 'EventEmitter':
        """
        add_listerner 别名但是返回 self
        """
        return self.add_listerner(event_name, listener)

    def _once_wrapper(self, name: str, listener: LISTENER_TYPE) -> LISTENER_TYPE:
        """
        生成单次调用的事件
        """
        args = WrapperTarget(self, name, listener)
        func = partial(once_wrapper, args)
        args.wrap_fn = cast(Any, func)
        cast(Any, func).listener = listener
        return func

    def once(self, event_name: str, listener: LISTENER_TYPE) -> 'EventEmitter':
        """
        设置单次调用事件
        """
        func = self._once_wrapper(event_name, listener)
        return self.add_listerner(event_name, func)

    def prepend_listener(self, event_name: str, listener: LISTENER_TYPE) -> 'EventEmitter':
        """
        添加事件到最前面
        """
        if event_name in self._listeners:
            listeners = self._listeners[event_name]
            listeners.insert(0, listener)
        else:
            self._listeners[event_name] = [listener]
        return self

    def prepend_once_listener(self, event_name: str, listener: LISTENER_TYPE) -> 'EventEmitter':
        """
        添加单次事件到最前面
        """
        func = self._once_wrapper(event_name, listener)
        return self.prepend_listener(event_name, func)

    def remove_all_listeners(self, event_name: str = None) -> 'EventEmitter':
        if event_name is None:
            self._listeners = {}
        elif event_name in self._listeners:
            self._listeners[event_name] = []
        return self

    def remove_listener(self, event_name: str, listener: LISTENER_TYPE) -> 'EventEmitter':
        if event_name != "removeListener":
            self.emit("removeListener")
        if event_name in self._listeners:
            listeners = self._listeners[event_name]
            listeners.remove(listener)
        return self

    def set_max_listeners(self, n: int) -> 'EventEmitter':
        self._default_max_listeners = n
        return self

    def raw_listeners(self, event_name: str) -> List[LISTENER_TYPE]:
        events = self.listeners(event_name)
        res = []
        for event in events:
            if hasattr(event, 'listener'):
                res.append(cast(Any, event).listener)
            else:
                res.append(event)
        return res
