from typing import Literal, cast
import typy.engine
import typy.formats.gitlab
import rich

SAMPLE_FILE = 'test/files/sample_file.py'

def report(name: typy.Engine):
    engine = typy.engine.get(name)
    result = engine.report(files=[SAMPLE_FILE])
    result.show()

report('ty')
report('pyright')
report('pyrefly')
report('mypy')
