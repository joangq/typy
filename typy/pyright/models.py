from datetime import datetime, timedelta
import pathlib
from typing import Annotated
from pydantic import BaseModel, BeforeValidator

class Summary(BaseModel):
    filesAnalyzed: int
    errorCount: int
    warningCount: int
    informationCount: int
    timeInSec: timedelta

class FilePosition(BaseModel):
    line: int
    character: int

class Range(BaseModel):
    start: FilePosition
    end: FilePosition

class GeneralDiagnostic(BaseModel):
    file: pathlib.Path
    severity: str
    message: str
    range: Range
    rule: None | str = None

class Version(BaseModel):
    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, value: object):
        if not isinstance(value, str):
            raise TypeError(f'Expected str, got {type(value)}')

        versiones = value.split('.')

        if len(versiones) != 3:
            raise ValueError(f'Invalid version: {value}')
        
        return cls(
            major=int(versiones[0]),
            minor=int(versiones[1]),
            patch=int(versiones[2])
        )


class Analysis(BaseModel):
    version: Annotated[Version, BeforeValidator(Version.from_string)]
    time: datetime
    generalDiagnostics: list[GeneralDiagnostic]
    summary: Summary
