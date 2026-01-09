from typing import Callable

def convert(
    value: object,
    argname: str,
    with_value: bool = True, 
    with_equals: bool = True, 
    mapper: Callable[[object], str] = (lambda x: str(x)),
    is_truth: Callable[[object], bool] = (lambda x: (x is None) or bool(x))
) -> None|str:
    _value = mapper(value)
    
    if not is_truth(_value):
        return None

    if not with_value:
        return argname
    
    separator = '=' if with_equals else ' '
    return f'{argname}{separator}{_value}'        
