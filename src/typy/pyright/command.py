import pyright.cli as pyright
from .models import Analysis
from subprocess import PIPE
from typing import Literal
import pathlib
from dataclasses import dataclass

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