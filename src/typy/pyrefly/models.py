from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

class Error(BaseModel):
    line: int
    column: int
    stop_line: int
    stop_column: int
    path: Path
    code: int
    name: str
    description: str
    concise_description: str
    severity: str

class Analysis(BaseModel):
    errors: list[Error]