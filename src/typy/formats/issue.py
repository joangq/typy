# https://github.com/codeclimate/platform/blob/master/spec/analyzers/SPEC.md

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import ClassVar, Literal

class LineColumnPosition(BaseModel):
    line: int = Field(..., ge=1)
    column: int = Field(..., ge=1)

class OffsetPosition(BaseModel):
    offset: int = Field(..., ge=0)

Position = LineColumnPosition | OffsetPosition

class PositionRange(BaseModel):
    begin: Position
    end: Position

class LineRange(BaseModel):
    begin: int = Field(..., ge=1)
    end: int = Field(..., ge=1)

class Location(BaseModel):
    path: str
    lines: None | LineRange = None
    positions: None | PositionRange = None

    @model_validator(mode="after")
    def validate_range(self):
        if not self.lines and not self.positions:
            raise ValueError("Location must have either lines or positions")
        if self.lines and self.positions:
            raise ValueError("Location cannot have both lines and positions")
        return self

class Content(BaseModel):
    body: str

class Trace(BaseModel):
    locations: list[Location]
    stacktrace: bool = False

Severity = Literal[
    "info",
    "minor",
    "major",
    "critical",
    "blocker",
]

Category = Literal[
    "Bug Risk",
    "Clarity",
    "Compatibility",
    "Complexity",
    "Duplication",
    "Performance",
    "Security",
    "Style",
]

class GitlabIssue(BaseModel):
    model_config: ClassVar[ConfigDict] = {'extra': 'ignore'}
    check_name: str
    description: str
    location: Location
    severity: None | Severity = None
    fingerprint: None | str = None

class BaseIssue(GitlabIssue):
    categories: list[Category]
    content: None | Content = None
    trace: None | Trace = None
    
class Codeclimate(BaseIssue):
    type: Literal["issue"] = "issue"

    other_locations: None | list[Location] = None

    remediation_points: None | int = Field(None, ge=0)

    @model_validator(mode="after")
    def validate_categories(self):
        if not self.categories:
            raise ValueError("At least one category is required")
        return self