from typing import Final, Literal

import typy
from typy.engine.base import EngineModule

Engine = Literal['ty', 'pyright', 'pyrefly', 'mypy']

from .ty import Module as ty
from .pyright import Module as pyright
from .pyrefly import Module as pyrefly
from .mypy import Module as mypy

available: Final[list[Engine]] = Engine.__args__
modules: Final[list[EngineModule]] = [
    ty,
    pyright,
    pyrefly,
    mypy,
]

NoSuchEngineException = lambda name: ValueError(
f"""
Engine '{name}' not found. Available engines: {Engine.__args__}
""")

def get(name: Engine) -> EngineModule:
    if name not in Engine.__args__:
        raise NoSuchEngineException(name)
    
    result = getattr(typy.engine, name)
    assert isinstance(result, type)
    assert issubclass(result, EngineModule)
    return result