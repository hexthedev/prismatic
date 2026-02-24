from datetime import datetime, timezone
from pathlib import Path

from prismatic.agents.obsidian import CLARIFICATION_MARKER, run_obsidian_agent

TRIGGER_CLAUDE = "@claude"
TRIGGER_SAFE = "@safe.claude"
DIR_NOTE_NAME = "_dir.md"


def consume_trigger(file_path: Path) -> str | None:
    """Check if file contains a trigger keyword. If so, remove it and return the trigger type.

    Returns "safe" for @safe.claude, "claude" for @claude, or None if no trigger found.
    Checks @safe.claude first to avoid partial matching by @claude.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    # Check @safe.claude first (contains @claude as substring)
    if TRIGGER_SAFE in content:
        cleaned = content.replace(TRIGGER_SAFE, "")
        file_path.write_text(cleaned, encoding="utf-8")
        return "safe"

    if TRIGGER_CLAUDE in content:
        cleaned = content.replace(TRIGGER_CLAUDE, "")
        file_path.write_text(cleaned, encoding="utf-8")
        return "claude"

    return None


def find_dir_note(start_dir: Path, vault_root: Path) -> Path | None:
    """Walk up from start_dir looking for a _DIR.md file (case-insensitive), stopping at vault_root."""
    current = start_dir
    while True:
        for entry in current.iterdir():
            if entry.is_file() and entry.name.lower() == DIR_NOTE_NAME:
                return entry
        if current == vault_root:
            break
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


async def handle_trigger(file_path: Path, vault_root: Path) -> None:
    """Check a file for the trigger keyword and spawn a Claude agent if found."""
    path = Path(file_path)

    trigger_type = consume_trigger(path)
    if trigger_type is None:
        return

    trigger_label = TRIGGER_SAFE if trigger_type == "safe" else TRIGGER_CLAUDE
    print(f"\n{'='*60}", flush=True)
    print(f"[trigger] {trigger_label} detected in {path}", flush=True)

    dir_note = find_dir_note(path.parent, vault_root)

    if dir_note is None:
        print(
            f"[trigger] No {DIR_NOTE_NAME} found (case-insensitive) in any parent up to {vault_root}",
            flush=True,
        )
        print(f"{'='*60}\n", flush=True)
        return

    relative_file = path.relative_to(dir_note.parent)
    print(f"[trigger] Found dir note at: {dir_note}", flush=True)
    print(f"[trigger] Triggered file relative to _DIR: {relative_file}", flush=True)
    print(f"[trigger] Mode: {'safe (preserve file)' if trigger_type == 'safe' else 'standard (clear file after processing)'}", flush=True)
    print(f"{'='*60}\n", flush=True)

    await run_obsidian_agent(path, dir_note, vault_root)

    # Check if agent wrote clarifying questions back — if so, preserve the file
    try:
        post_run_content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        post_run_content = ""

    if CLARIFICATION_MARKER in post_run_content:
        print(
            f"[trigger] Agent needs clarification — file preserved, waiting for user response",
            flush=True,
        )
        return

    # For standard @claude trigger, archive then clear the SOC file
    if trigger_type == "claude":
        archive_soc(path, vault_root)
        path.write_text("", encoding="utf-8")
        print(f"[trigger] Cleared contents of {path} (standard trigger)", flush=True)


def archive_soc(file_path: Path, vault_root: Path) -> Path | None:
    """Save a copy of the SOC file to .prismatic/history/ before it gets cleared."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    if not content.strip():
        return None

    history_dir = vault_root / ".prismatic" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    stem = file_path.stem
    archive_name = f"{timestamp}_{stem}.md"
    archive_path = history_dir / archive_name

    archive_path.write_text(content, encoding="utf-8")
    print(f"[trigger] Archived SOC to {archive_path}", flush=True)
    return archive_path
