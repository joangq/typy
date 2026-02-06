from datetime import datetime, timedelta
import warnings
from typy.engine.base import EngineModule
from typy.utils.types import AnyDict
from .models import Analysis
from argbuilder import Command, Field # pyright: ignore[reportMissingTypeStubs]
from pathlib import Path
from typy.utils.path import resolve_path, resolve_paths
from typy.utils import fingerprint
import json
from hashlib import sha1

from typy.formats import issue, gitlab, report as Report
type MypyAnalysis = Analysis

class Module(EngineModule):
    class mypy(Command):
        files: list[Path] = Field('{value}', serializer=resolve_paths)
        output: str = Field('--output={value}', default='json')
        version: bool = Field('--version')

    SEVERITY: dict[str, issue.Severity] = {
        'note': 'info',
        'error': 'major'
    }

    @staticmethod
    def _run(**kwargs: AnyDict):
        from time import perf_counter_ns

        args = Module.mypy.from_dict(kwargs)
        cl_args = args.build(with_self=False)

        import mypy.main as mypy
        import io

        stdout = io.StringIO()
        stderr = io.StringIO()

        start = perf_counter_ns()
        try:
            mypy.main(
                args=cl_args,
                stdout=stdout,
                stderr=stderr,
                clean_exit=True
            )
        except SystemExit: pass

        stdout = stdout.getvalue()
        stderr = stderr.getvalue()
        elapsed = perf_counter_ns() - start

        return stdout, stderr, elapsed

    @staticmethod
    def run(**kwargs: AnyDict) -> MypyAnalysis:
        stdout, _, _ = Module._run(**kwargs)
        objects = stdout.strip().split('\n')

        return Analysis.model_validate({
            'messages': [json.loads(x) for x in objects]
        })

    @staticmethod
    def version() -> str:
        output, _, _ = Module._run(version=True)
        return output.strip()

    @staticmethod
    def report(**kwargs: AnyDict):
        now = datetime.now()
        stdout, stderr, elapsed = Module._run(**kwargs)
        objects = stdout.strip().split('\n')

        try:
            analysis = Analysis.model_validate({
                'messages': [json.loads(x) for x in objects if x]
            })
        except json.JSONDecodeError as je:
            __args = ' '.join(Module.mypy.from_dict(kwargs).build())
            raise Exception(f'{__args} {stderr=!r}') from je

        issues = list[gitlab.Issue]()
        for message in analysis.messages:
            positions=issue.PositionRange(
                begin=issue.LineColumnPosition(
                    line=message.line,
                    column=message.column+1
                ),
                end=issue.LineColumnPosition(
                    line=message.line,
                    column=message.column+1
                )
            )

            location = issue.Location(
                path=resolve_path(message.file),
                lines=None,
                positions=positions
            )

            severity = Module.SEVERITY.get(message.severity, None)
            if not severity:
                warnings.warn(f'unmapped severity {message.severity}')
            
            issues.append(gitlab.Issue(
                check_name=message.code,
                description=message.message,
                location=location,
                severity=severity,
                fingerprint=fingerprint(message.model_dump_json(indent=0)),
            ))

        return gitlab.Report(
            issues=issues,
            elapsed=timedelta(microseconds=elapsed / 1000),
            time=now,
            emitter=Report.Emitter(name='mypy', version=Module.version())
        )