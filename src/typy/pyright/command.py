from datetime import timedelta
from typing import Any, Concatenate, Generic, Literal, NamedTuple, ParamSpec, Callable, TypeVar, cast
from pathlib import Path
import warnings
from argbuilder import Command, Field # pyright: ignore[reportMissingTypeStubs]
import json
from typy.formats import gitlab, issue, report as Report
from hashlib import sha1
from typy.utils import fingerprint
from typy.utils.path import resolve_path, resolve_paths

from .models import Analysis
type PyrightAnalysis = Analysis

P = ParamSpec('P')
R = TypeVar('R')

def signature_of(cls_init: Callable[Concatenate[Any, P], Any]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to copy a class __init__ signature minus the 'self' argument."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        return func
    return decorator

# --createstub <IMPORT>              Create type stub file(s) for import
# --dependencies                     Emit import dependency information
# --ignoreexternal                   Ignore external imports for --verifytypes
# --level <LEVEL>                    Minimum diagnostic level (error or warning)
# --outputjson                       Output results in JSON format
# --project <FILE OR DIRECTORY>   Use the configuration file at this location
# --pythonplatform <PLATFORM>        Analyze for a specific platform (Darwin, Linux, Windows)
# --pythonpath <FILE>                Path to the Python interpreter
# --pythonversion <VERSION>          Analyze for a specific version (3.3, 3.4, etc.)
# --skipunannotated                  Skip analysis of functions with no type annotations
# --stats                            Print detailed performance stats
# --typeshedpath <DIRECTORY>      Use typeshed type stubs at this location
# --threads <optional COUNT>         Use separate threads to parallelize type checking 
# --venvpath <DIRECTORY>          Directory that contains virtual environments
# --verbose                          Emit verbose diagnostics
# --verifytypes <PACKAGE>            Verify type completeness of a py.typed package
# --version                          Print Pyright version and exit
# --warnings                         Use exit code of 1 if warnings are reported
# --watch                         Continue to run and watch for changes
# -                                  Read files from stdin

class Version(NamedTuple):
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f'{self.major}.{self.minor}.{self.patch}'
    
    def __repr__(self):
        return f'Version(major={self.major}, minor={self.minor}, patch={self.patch})'

    def to_str(self):
        return self.__str__()

def threads_param(x: None|int): return '' if x is None else f' {x}'

# https://peps.python.org/pep-0681/#field-specifier-parameters
from typing import dataclass_transform

@dataclass_transform(
        field_specifiers=(Field,),
        kw_only_default=True,
    )
def my_custom_model[T: type](x: T) -> T: return x

from argbuilder.builder import NOT_SET # pyright: ignore[reportMissingTypeStubs]

@my_custom_model
class Pyright(Command, Generic[P]):
    files: list[str|Path] = Field('{value}', resolve_paths)
    create_stub: Path = Field('--createstub {value}', serializer=resolve_path, default=NOT_SET)
    dependencies: bool = Field('--dependencies', default=NOT_SET)
    ignore_external: bool = Field('--ignoreexternal', default=NOT_SET)
    level: Literal['error',  'warning'] = Field('--level {value}', default=NOT_SET)
    output_json: bool = Field('--outputjson', default=True)
    project: Path = Field('--project {value}', default=NOT_SET)
    python_platform: Literal['Windows', 'Darwin', 'Linux', 'All'] = Field('--pythonplatform {value}', default=NOT_SET)
    python_path: Path = Field('--pythonpath {value}', serializer=resolve_path, default=NOT_SET)
    python_version: Path = Field('--pythonversion {value}', serializer=Version.to_str, default=NOT_SET)
    skip_unannotated: bool = Field('--skipunannotated', default=NOT_SET)
    stats: bool = Field('--stats', default=NOT_SET)
    typeshed_path: Path = Field('--typeshedpath {value}', serializer=resolve_path, default=NOT_SET)
    threads: None|int = Field('--threads{value}', serializer=threads_param, default=NOT_SET)
    venv_path: Path = Field('--venvpath {value}', serializer=resolve_path, default=NOT_SET)
    verbose: bool = Field('--verbose', default=NOT_SET)
    verify_types: str = Field('--verifytypes {value}', default=NOT_SET)
    version: bool = Field('--version', default=NOT_SET)
    warnings: bool = Field('--warnings', default=NOT_SET)
    watch: bool = Field('--watch', default=NOT_SET)


def _run(**kwargs):
    args = Pyright.from_dict(kwargs)
    cl_args = args.build(with_self=False)

    import pyright.cli
    import subprocess

    result = cast(
        'subprocess.CompletedProcess[bytes]',
        pyright.cli.run(
        *cl_args,
        text=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ))

    return result

def version():
    result = _run(version=True)
    stdout = result.stdout.decode('utf8')
    return stdout

@signature_of(Pyright.__init__)
def run(*pargs: Any, **kwargs: Any):
    argc = len(pargs)
    if argc > 0:
        raise TypeError(f"'run' takes 0 positional arguments but {argc} was given.")
    
    result = _run(**kwargs)
    stdout = result.stdout.decode('utf8')
    stdout = stdout.replace('\xa0', ' ')
    data = json.loads(stdout)
    return Analysis.model_validate(data)


SEVERITY_MAP: dict[str, issue.Severity] = {
    'information': 'info',
    'error': 'major'
}
@signature_of(Pyright.__init__)
def report(**kwargs: Any):
    result = run(**kwargs)
    issues = list[gitlab.Issue]()

    for diagnostic in result.generalDiagnostics:
        check_name = diagnostic.rule or 'misc'
        severity = SEVERITY_MAP.get(diagnostic.severity, None)
        if not severity:
            warnings.warn(f'unmapped severity {diagnostic.severity}')
        
        range = issue.PositionRange(
            begin=issue.LineColumnPosition(
                line=diagnostic.range.start.line, 
                column=diagnostic.range.start.character
            ),
            end=issue.LineColumnPosition(
                line=diagnostic.range.end.line, 
                column=diagnostic.range.end.character,
            )
        )

        issues.append(gitlab.Issue(
            check_name=check_name,
            description=diagnostic.message,
            severity=severity,
            fingerprint=fingerprint(diagnostic.model_dump_json(indent=0)),
            location=issue.Location(
                path=str(diagnostic.file.resolve()),
                positions=range,
                lines=None, # TODO
            )
        ))
    
    return gitlab.Report(
        issues=issues,
        elapsed=timedelta(microseconds=result.summary.timeInSec.microseconds),
        time=result.time,
        emitter=Report.Emitter(name='pyright', version=version())
    )