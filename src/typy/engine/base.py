from abc import ABC, abstractmethod
import stat

from argbuilder import Command
from pydantic import BaseModel

from typy.formats import report

type Analysis = BaseModel

class RevealType(BaseModel):
    typ: str
    sym: None|str

class EngineModule(ABC):
    @staticmethod
    @abstractmethod
    def run(**kwargs: object) -> Analysis: ...

    @staticmethod
    @abstractmethod
    def report(**kwargs: object) -> report.ReportBase: ...

    @staticmethod
    @abstractmethod
    def parse_reveal_type(x: str) -> None|RevealType: ...

    @staticmethod
    def is_reveal_type(x: str) -> bool:
        return EngineModule.parse_reveal_type(x) is not None

    def __init_subclass__(cls) -> None:
        variables = vars(cls)
        commands = [
            v
            for v in variables.values()
            if isinstance(v, type)
            if issubclass(v, Command)
        ]

        abstract_methods = [
            v
            for v in vars(EngineModule).values()
            if isinstance(v, staticmethod)
            if v.__isabstractmethod__
            if v.__name__ not in variables
        ]

        def MissingMethodsError(cls, methods: list[str]) -> ValueError:
            methods = (f"'{method}'" for method in methods)
            return ValueError(f'{cls.__qualname__} is subclass of {EngineModule.__name__} and must implement the following methods: {", ".join(methods)}')

        if abstract_methods:
            raise MissingMethodsError(cls, [v.__name__ for v in abstract_methods])

        if not commands:
            raise ValueError(f'{cls.__name__} must have at least one command')

        if (len(commands) == 1) and ('command' not in variables):
            setattr(cls, 'command', commands[0])

        super().__init_subclass__()
