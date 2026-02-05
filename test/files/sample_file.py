from typing import Callable, assert_type, reveal_type, Protocol

class Foo(Protocol):
    def __call__(self, a: int, /, y: bool) -> str: ...

def foo(x: int, y: bool) -> str:
    return str(x)+str(y)

_: Foo = 1