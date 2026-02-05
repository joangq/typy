from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

class Message(BaseModel):
    file: Path
    line: int
    column: int
    message: str
    hint: object
    code: str
    severity: str

class Analysis(BaseModel):
    messages: list[Message]