from typing import Literal, cast
from typy import ty, pyright, pyrefly, mypy
import typy
import typy.formats.gitlab
import rich

SAMPLE_FILE = 'test/files/sample_file.py'

type Engine = Literal['ty', 'pyright', 'pyrefly', 'mypy']

def report(engine: Engine):
    engine = getattr(typy, engine)
    result = cast(typy.formats.gitlab.Report,
                  engine.report(files=[SAMPLE_FILE]) # type: ignore
    )

    result.show()

    # rich.print(result.emitter)
    # for issue in result.issues:
    #     rich.print(issue.check_name)
    #     rich.print(issue.description)
    #     rich.print()
# 
    # rich.print(result.elapsed.microseconds / 1000, 'ms') # type: ignore
    # rich.print()

report('ty')
report('pyright')
report('pyrefly')
report('mypy')
