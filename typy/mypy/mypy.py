"""
from typing import Callable
from mypy.api import run
import json
from pydantic.types import _JSON_TYPES
import rich

import tempfile
import io
import os
import pathlib

def callback_on_tempscript(script: pathlib.Path, callback: Callable):
    with tempfile.TemporaryDirectory(
        delete=True
    ) as temp_dir:
        temp_file = pathlib.Path(temp_dir) / 'script.py'
        temp_file.write_text(script)
        result = callback(temp_file)
        
    return result

def run_mypy(script: pathlib.Path):
    stdout, stderr, exit_code = run(['--output=json', str(script.resolve())])    
    stdout = stdout.strip()

    if not stdout:
        return []
    
    stdout = stdout.split('\n')

    stdout = [
        json.loads(line)
        for line in stdout
    ]

    return stdout

rich.print(callback_on_tempscript("import pandas\na: int = 1\nreveal_type(pandas.DataFrame())", run_mypy))    
"""