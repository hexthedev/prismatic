import asyncio
import os
import subprocess
import sys
from pathlib import Path

from prismatic.watcher import watch_folder


def main() -> None:
    args = sys.argv[1:]
    long_lived = "--long-lived" in args
    if long_lived:
        args.remove("--long-lived")

    if len(args) < 1:
        raise SystemExit("Usage: prismatic [--long-lived] <folder-path>")

    folder = Path(args[0])

    if long_lived:
        # Re-exec under caffeinate -i (prevent idle sleep, allow display sleep).
        # Only do this if we're not already running under caffeinate.
        if not os.environ.get("PRISMATIC_CAFFEINATED"):
            env = {**os.environ, "PRISMATIC_CAFFEINATED": "1"}
            cmd = ["caffeinate", "-i", sys.argv[0], str(folder), "--long-lived"]
            try:
                proc = subprocess.run(cmd, env=env)
                raise SystemExit(proc.returncode)
            except KeyboardInterrupt:
                raise SystemExit(0)

        print("[prismatic] Running in long-lived mode (caffeinate -i)", flush=True)

    asyncio.run(watch_folder(folder))
