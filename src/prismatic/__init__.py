import sys
from pathlib import Path

from prismatic.watcher import watch_folder


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: prismatic <folder-path>")

    watch_folder(Path(sys.argv[1]))
