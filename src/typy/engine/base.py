from abc import ABC, abstractmethod

from argbuilder import Command
from pydantic import BaseModel

from typy.formats import report

type Analysis = BaseModel

class EngineModule(ABC):
    @staticmethod
    @abstractmethod
    def run(**kwargs: object) -> Analysis: ...

    @staticmethod
    @abstractmethod
    def report(**kwargs: object) -> report.ReportBase: ...

    def __init_subclass__(cls) -> None:
        variables = vars(cls)
        commands = [
            v
            for v in variables.values()
            if isinstance(v, type)
            if issubclass(v, Command)
        ]

        if not commands:
            raise ValueError(f'{cls.__name__} must have at least one command')

        if (len(commands) == 1) and ('command' not in variables):
            setattr(cls, 'command', commands[0])
            
        super().__init_subclass__()
