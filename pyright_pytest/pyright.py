from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Literal
import pyright.cli as pyright
from subprocess import PIPE
import pathlib
import json

# result = pyright.run(path, '--outputjson', stdout=PIPE, stderr=PIPE)

#stdout = result.stdout

# if isinstance(stdout, bytes):
#     stdout = stdout.decode('utf-8')

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

@dataclass
class CliArgument:
    value: object
    argname: str
    
    def convert(
        self, 
        with_value: bool = True, 
        with_equals: bool = True, 
        mapper: Callable[[object], str] = (lambda x: str(x)),
        is_truth: Callable[[object], bool] = (lambda x: (x is None) or bool(x))
    ) -> None|str:
        value = mapper(self.value)
        
        if not is_truth(value):
            return None

        if not with_value:
            return self.argname
        
        separator = '=' if with_equals else ' '
        return f'--{self.argname}{separator}{value}'
        

if TYPE_CHECKING:
    def Argument[T](x: T, argname: str) -> T:
        return x
else:
    def Argument[T](x: T, argname: str) -> T:
        return CliArgument(x, argname)

def run(
    path: str | pathlib.Path,
    *,
    dependencies: bool                                     = Argument(False,   '--dependencies'),
    ignore_external: bool                                  = Argument(False,   '--ignoreexternal'),
    level: Literal['error', 'warning']                     = Argument('error', '--level'),
    output_json: bool                                      = Argument(False,   '--outputjson'),
    project: str | pathlib.Path                            = Argument(None,    '--project'),
    python_platform: Literal['Darwin', 'Linux', 'Windows'] = Argument(None,    '--pythonplatform'),
    python_version: str                                    = Argument(None,    '--pythonversion'),
    skip_unannotated: bool                                 = Argument(False,   '--skipunannotated'),
    stats: bool                                            = Argument(False,   '--stats'),
    typeshed_path: None | str | pathlib.Path               = Argument(None,    '--typeshedpath'),
    threads: int | None                                    = Argument(None,    '--threads'),
    venv_path: None | str | pathlib.Path                   = Argument(None,    '--venvpath'),
    verbose: bool                                          = Argument(False,   '--verbose'),
    verify_types: str | None                               = Argument(None,    '--verifytypes'),
    warnings: bool                                         = Argument(False,   '--warnings'),
):
    args = locals()
    path = args.pop('path')
    for k, v in args.items():
        print(k,v, type(v))

    # result = pyright.run(path, **args)
    # return result