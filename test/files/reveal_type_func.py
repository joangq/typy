from typing import reveal_type

def foo(x: int) -> str: ...

reveal_type(foo)