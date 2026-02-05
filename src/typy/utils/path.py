from pathlib import Path

def resolve_path(x: str|Path) -> str:
    return str(Path(x).resolve())

def resolve_paths(xs: list[Path]) -> str:
    return ' '.join(map(resolve_path, xs))
