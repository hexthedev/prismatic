from pathlib import Path

import watchfiles


CHANGE_LABELS = {
    watchfiles.Change.added: "created",
    watchfiles.Change.modified: "modified",
    watchfiles.Change.deleted: "deleted",
}


def watch_folder(path: Path) -> None:
    if not path.is_dir():
        raise SystemExit(f"Error: {path} is not a directory")

    print(f"Watching {path} for changes...", flush=True)

    for changes in watchfiles.watch(path):
        for change_type, file_path in changes:
            label = CHANGE_LABELS.get(change_type, str(change_type))
            print(f"[{label}] {file_path}", flush=True)
