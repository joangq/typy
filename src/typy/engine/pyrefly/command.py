from datetime import datetime, timedelta
from hashlib import sha1
import re
import warnings
from argbuilder import Command, Field # pyright: ignore[reportMissingTypeStubs]
from argbuilder.builder import NOT_SET # pyright: ignore[reportMissingTypeStubs]
from pathlib import Path
from typing import Literal, cast

from typy.engine.base import EngineModule, RevealType
from typy.utils.types import AnyDict
from typy.utils.path import resolve_paths, resolve_path
from .models import Analysis
from typy.formats import gitlab, issue, report as Report
from typy.utils import fingerprint, subprocess

type PyreflyAnalysis = Analysis

def threads_param(x: None|int): return '' if x is None else f' {x}'

type OutputFormat = Literal['min-text', 'full-text', 'json', 'github', 'omit-errors']

class Module(EngineModule):
    SEVERITY: dict[str, issue.Severity] = {
        'info': 'info',
        'error': 'major'
    }

    class pyrefly(Command):
        version: bool = Field('--version')

        class check(Command):
            files: list[str|Path] = Field('{value}', resolve_paths)
            threads: int = Field('--threads {value}', default=NOT_SET)
            output_format: OutputFormat = Field('--output-format={value}', default='json')
            verbose: bool = Field('--verbose', default=True)

    @staticmethod
    def _get_pyrefly():
        from pyrefly.__main__ import get_pyrefly_bin
        return get_pyrefly_bin()

    @staticmethod
    def _run(**kwargs: AnyDict):
        pyrefly = Module._get_pyrefly()
        args = Module.pyrefly().check.from_dict(kwargs)
        cl_args = args.build(with_self=False)
        cl_args = [pyrefly, 'check', *cl_args]

        return cast(
            'tuple[subprocess.CompletedProcess[bytes], int]',
            subprocess.time_run(
            cl_args, 
            text=False, # pyright: ignore[reportArgumentType]
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        ))

    @staticmethod
    def version():
        cl_args = Module.pyrefly(version=True).build(with_self=True)
        assert cl_args[0] == 'pyrefly'
        cl_args[0] = Module._get_pyrefly()
        result = subprocess.run(
            cl_args,
            text = False,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
        )

        return result.stdout.decode().strip()

    @staticmethod
    def run(**kwargs: AnyDict) -> PyreflyAnalysis:
        result, _ = Module._run(**kwargs)
        stdout = result.stdout.decode('utf8')
        return Analysis.model_validate_json(stdout)

    @staticmethod
    def report(**kwargs: AnyDict) -> gitlab.Report:
        now = datetime.now()
        result, elapsed = Module._run(**kwargs)
        stdout = result.stdout.decode('utf8')
        analysis = Analysis.model_validate_json(stdout)
        issues = list[gitlab.Issue]()

        for error in analysis.errors:
            severity = Module.SEVERITY.get(error.severity, None)
            if not severity:
                warnings.warn(f'unmapped severity {error.severity}')

            positions=issue.PositionRange(
                begin=issue.LineColumnPosition(
                    line=error.line,
                    column=error.column
                ),
                end=issue.LineColumnPosition(
                    line=error.line,
                    column=error.column
                )
            )

            location = issue.Location(
                path=resolve_path(error.path),
                lines=None,
                positions=positions
            )

            issues.append(gitlab.Issue(
                check_name=error.name,
                description=error.description,
                severity=severity,
                location=location,
                fingerprint=fingerprint(error.model_dump_json(indent=0)),
            ))

        return gitlab.Report(
            issues=issues,
            elapsed=timedelta(microseconds=elapsed / 1000),
            time=now,
            emitter=Report.Emitter(name='pyrefly', version=Module.version()),
        )

    REVEAL_TYPE_PATTERN = re.compile(
        r'revealed type: (.*)'
    )

    @staticmethod
    def parse_reveal_type(x: str) -> None | RevealType:
        match = Module.REVEAL_TYPE_PATTERN.search(x)
        if not match:
            return None
        
        return RevealType(
            typ=match.group(1),
            sym=None
        )