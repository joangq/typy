from typing import Literal, cast
import typy.engine
import typy.formats.gitlab
import rich

SAMPLE_FILE = 'test/files/sample_file.py'

for engine in typy.engine.available:
    engine = typy.engine.get(engine)
    result = engine.report(files=[SAMPLE_FILE])
    # result.show()
    for issue in result.issues:
        print(engine.parse_reveal_type(issue.description))

