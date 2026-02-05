#import json
from datetime import datetime, timedelta
import json
from typing import Any, cast
from argbuilder import Command, Field # pyright: ignore[reportMissingTypeStubs]
from pathlib import Path
from typy.formats import gitlab, report as Report
from typy.utils.path import resolve_paths
from typy.utils import subprocess

class Ty(Command):
    class check(Command):
        files: list[Path] = Field('{value}', resolve_paths)
        output_format: str = Field('--output-format={value}', default='gitlab')
    
    class version(Command): pass

def _get_ty():
    import os
    from ty.__main__ import find_ty_bin
    ty = os.fsdecode(find_ty_bin())
    return ty

def version():
    args = Ty().version().build(with_self=True)
    assert args[0] == 'ty'
    args[0] = _get_ty()
    result = subprocess.run(
        args,
        text=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    result = cast('subprocess.CompletedProcess[bytes]', result)
    return result.stdout.decode().strip()
    

def _run(**kwargs: Any):
    args = Ty().check.from_dict(kwargs)
    cl_args = args.build(with_self=False)

    ty = _get_ty()
    cl_args = [ty, 'check', *cl_args]

    result, elapsed = subprocess.time_run(
        cl_args,
        text=False, # pyright: ignore[reportArgumentType]
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    result = cast('subprocess.CompletedProcess[bytes]', result)
    return result, elapsed

def run(**kwargs: Any):
    result, _ = _run(**kwargs)
    stdout = result.stdout.decode('utf8')
    stdout = stdout.replace('\xa0', ' ')
    data = json.loads(stdout.strip())
    return [
        gitlab.Issue.model_validate(x)
        for x in data
    ]
    #return gitlab.Report.model_validate_json(f'{{"issues":{stdout}}}')

def report(**kwargs: Any):
    now = datetime.now()
    result, elapsed = _run(**kwargs)
    stdout = result.stdout.decode('utf8')
    stdout = stdout.replace('\xa0', ' ')
    data = json.loads(stdout.strip())
    issues = [
        gitlab.Issue.model_validate(x)
        for x in data
    ]
    
    return gitlab.Report(
        issues=issues,
        elapsed=timedelta(microseconds=elapsed / 1000),
        time=now,
        emitter=Report.Emitter(name='ty', version=version())
    )