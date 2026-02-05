from typing import Any, ParamSpec, Callable, TypeVar
import subprocess
from time import perf_counter_ns
from subprocess import * # pyright: ignore[reportWildcardImportFromLibrary]
from typing import cast

P = ParamSpec('P')
R = TypeVar('R')

def copy_signature(f: Callable[P, Any]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        return func
    return decorator

@copy_signature(subprocess.call)
def time_call(*args, **kwargs):
    start = perf_counter_ns()
    result = subprocess.call(*args, **kwargs)
    elapsed = perf_counter_ns() - start
    return result, elapsed

@copy_signature(subprocess.run)
def time_run(*args, **kwargs):
    start = perf_counter_ns()
    result = subprocess.run(*args, **kwargs) # pyright: ignore[reportUnknownVariableType]
    result = cast(
        'subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]', 
        result
    )
    elapsed = perf_counter_ns() - start
    return result, elapsed