from typy.common import NULL, Null, cli_argument
import pyright.cli as pyright
from .models import Analysis
from subprocess import PIPE
from typing import Literal
import pathlib

# --createstub <IMPORT>              Create type stub file(s) for import
# --dependencies                     Emit import dependency information
# --ignoreexternal                   Ignore external imports for --verifytypes
# --level <LEVEL>                    Minimum diagnostic level (error or warning)
# --outputjson                       Output results in JSON format
# -p,--project <FILE OR DIRECTORY>   Use the configuration file at this location
# --pythonplatform <PLATFORM>        Analyze for a specific platform (Darwin, Linux, Windows)
# --pythonpath <FILE>                Path to the Python interpreter
# --pythonversion <VERSION>          Analyze for a specific version (3.3, 3.4, etc.)
# --skipunannotated                  Skip analysis of functions with no type annotations
# --stats                            Print detailed performance stats
# -t,--typeshedpath <DIRECTORY>      Use typeshed type stubs at this location
# --threads <optional COUNT>         Use separate threads to parallelize type checking 
# -v,--venvpath <DIRECTORY>          Directory that contains virtual environments
# --verbose                          Emit verbose diagnostics
# --verifytypes <PACKAGE>            Verify type completeness of a py.typed package
# --version                          Print Pyright version and exit
# --warnings                         Use exit code of 1 if warnings are reported
# -w,--watch                         Continue to run and watch for changes
# -                                  Read files from stdin

ARGMAP = {
    'dependencies': '--dependencies',
    'ignore_external': '--ignoreexternal',
    'level': '--level',
    'output_json': '--outputjson',
    'project': '--project',
    'python_platform': '--pythonplatform',
    'python_version': '--pythonversion',
    'skip_unannotated': '--skipunannotated',
    'stats': '--stats',
    'typeshed_path': '--typeshedpath',
    'threads': '--threads',
    'venv_path': '--venvpath',
    'verbose': '--verbose',
    'verify_types': '--verifytypes',
    'warnings': '--warnings',
}

def execute(
    path: str | pathlib.Path,
    *,
    dependencies: bool                                     = False,
    ignore_external: bool                                  = False,
    level: Literal['error', 'warning']                     = 'error',
    output_json: bool                                      = True,
    project: str | pathlib.Path                            = NULL,
    python_platform: Literal['Darwin', 'Linux', 'Windows'] = NULL,
    python_version: str                                    = NULL,
    skip_unannotated: bool                                 = False,
    stats: bool                                            = False,
    typeshed_path: Null | str | pathlib.Path               = NULL,
    threads: Null | int                                    = NULL,
    venv_path: Null | str | pathlib.Path                   = NULL,
    verbose: bool                                          = False,
    verify_types: Null | str                               = NULL,
    warnings: bool                                         = False,
):
    args = locals()
    path = args.pop('path')
    
    args = {
        k : cli_argument.convert(v, ARGMAP[k], with_value=isinstance(v, str)) 
        for k,v in args.items() 
        if v is not NULL
        if bool(v)
    }

    for k, v in args.items():
        print(k,v)

    result = pyright.run(
        path, 
        *args.values(), 
        text=True,
        encoding='utf-8',
        stdout=PIPE, 
        stderr=PIPE
    )

    return result

def run(path: str | pathlib.Path):
    result = execute(path, output_json=True)
    return Analysis.model_validate_json(result.stdout)