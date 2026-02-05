# https://github.com/codeclimate/platform/blob/master/spec/analyzers/SPEC.md

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import ClassVar, Literal

from rich.syntax import Syntax
from rich.console import Console

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

    def show(
        self,
        srclines: list[str],
        highlight_char: str = '^', # '~'
        rich_colors: bool = True,
        console: None|Console = None,
        code_theme: str = 'one-dark',
    ):
        console = console or Console(no_color=not rich_colors)
        #for i,issue in enumerate(report.issues):
        #    is_last_issue = i == len(report.issues)-1

        location = self.location

        if not location.positions:
            return

        if not (
            isinstance(location.positions.begin, LineColumnPosition)
            and isinstance(location.positions.end, LineColumnPosition)
        ):
            return
        
        begin_line: int = location.positions.begin.line-1
        end_line: int = location.positions.end.line
        lines = srclines[begin_line-1:end_line+1]
        lines = [*filter(bool, lines)]
        begin_col: int = location.positions.begin.column-1
        end_col: int = location.positions.end.column
        
        highlight = highlight_char*abs(begin_col-end_col)

        #print(begin_line, end_line)
        
        if (sep := lines[-1].strip()):
            highlight = (
                lines[-1].rsplit(sep, 1)[0]
                + highlight
            )

        location_str = f'>>> {location.path}:{begin_line+1}:{end_line+1}'
        
        original_width = console.width

        location_str = f'[blue]{location_str}[/blue]'
        console.print(location_str)

        for j, line in enumerate(lines):
            is_last = j == len(lines)-1
            
            highlight = f'[bold][red]{highlight}[/bold][/red]'
            block = f'[black]| [/black]'
            n = len(line)
            line = Syntax(
                line, 
                'python', 
                theme=code_theme,
                background_color='default'
            )
            
            console.print(block, end=' ')
            console.width = n
            console.print(line, end='')
            console.width = original_width

            if is_last:
                console.print(block, end=' ')
                console.print(highlight)

        console.width = original_width

        # issue_description = f'{report.emitter.name}\\[{issue.check_name}]: {issue.description}'
        # issue_description = f'[red]{issue_description}[/red]'
        
        # console.print(issue_description)
        
        # if not is_last_issue:
        #     console.print()

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