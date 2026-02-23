from pathlib import Path

TRIGGER_KEYWORD = "@claude"
DIR_NOTE_NAME = "_DIR.md"


def consume_trigger(file_path: Path) -> bool:
    """Check if file contains the trigger keyword. If so, remove it and return True."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False

    if TRIGGER_KEYWORD not in content:
        return False

    cleaned = content.replace(TRIGGER_KEYWORD, "")
    file_path.write_text(cleaned, encoding="utf-8")
    return True


def find_dir_note(start_dir: Path, vault_root: Path) -> Path | None:
    """Walk up from start_dir looking for a _DIR.md file, stopping at vault_root."""
    current = start_dir
    while True:
        candidate = current / DIR_NOTE_NAME
        if candidate.is_file():
            return candidate
        if current == vault_root:
            break
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def handle_trigger(file_path: Path, vault_root: Path) -> None:
    """Check a file for the trigger keyword and log the event with DIR context."""
    path = Path(file_path)

    if not consume_trigger(path):
        return

    print(f"\n{'='*60}", flush=True)
    print(f"[trigger] @claude detected in {path}", flush=True)

    dir_note = find_dir_note(path.parent, vault_root)

    if dir_note is None:
        print(f"[trigger] No {DIR_NOTE_NAME} found in any parent up to {vault_root}", flush=True)
    else:
        relative_file = path.relative_to(dir_note.parent)
        print(f"[trigger] Found {DIR_NOTE_NAME} at: {dir_note}", flush=True)
        print(f"[trigger] Triggered file relative to _DIR: {relative_file}", flush=True)
        print(f"[trigger] _DIR.md contents:", flush=True)
        print(f"---", flush=True)
        print(dir_note.read_text(encoding="utf-8"), flush=True)
        print(f"---", flush=True)

    print(f"{'='*60}\n", flush=True)
