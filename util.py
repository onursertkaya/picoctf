import subprocess
import shlex
from typing import Optional


def bash(cmd: str, get_stdout: bool = False) -> Optional[str]:
    kwargs = {}
    if get_stdout:
        kwargs = {"encoding": "utf-8", "capture_output": True}
    result = subprocess.run(shlex.split(cmd), **kwargs)
    return result.stdout if get_stdout else None


def cat(filepath: str):
    with open(filepath, encoding="utf-8") as f:
        print(f.read())
