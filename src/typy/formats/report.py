from datetime import datetime, timedelta
from pydantic import BaseModel

from rich.console import Console
from . import issue
from pathlib import Path
import tokenize

class Emitter(BaseModel):
    name: str
    version: None|str

class ReportBase[T: issue.GitlabIssue](BaseModel):
    issues: list[T]
    elapsed: timedelta
    time: datetime
    emitter: Emitter

    def show(
            self, 
            rich_colors: bool = True, 
            console: None|Console = None,
            code_theme: str = 'one-dark'
    ):
        console = console or Console(no_color=not rich_colors)

        CACHE = dict[str, list[str]]()
        def get_file_lines(file: str|Path):
            file = Path(file).resolve()

            cached = CACHE.get(str(file), None)
            if cached:
                result = cached

            with tokenize.open(str(file)) as f:
                src = f.read()
            
            result = CACHE[str(file)] = src.splitlines()

            return result

        for i,issue in enumerate(self.issues):
            is_last_issue = i == len(self.issues)-1

            srclines = get_file_lines(issue.location.path)

            issue.show(
                srclines=srclines,
                console=console,
                code_theme=code_theme
            )

            issue_description = f'{self.emitter.name}\\[{issue.check_name}]: {issue.description}'
            issue_description = f'[red]{issue_description}[/red]'

            console.print(issue_description)

            if not is_last_issue:
                console.print()