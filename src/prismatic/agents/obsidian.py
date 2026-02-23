import asyncio
import json
from pathlib import Path

SYSTEM_PROMPT_TEMPLATE = """\
You are operating on an Obsidian vault folder.

## Folder Rules (_DIR.md)
{dir_rules}

## Context
The triggered file is at: {relative_path}
The working directory is: {working_dir}

Process the file content below according to the folder rules above.\
"""


async def run_obsidian_agent(
    soc_file: Path, dir_note: Path, vault_root: Path
) -> None:
    """Invoke the claude CLI to process a triggered SOC file using folder rules."""
    dir_rules = dir_note.read_text(encoding="utf-8")
    prompt_text = soc_file.read_text(encoding="utf-8")
    working_dir = dir_note.parent

    relative_path = soc_file.relative_to(working_dir)

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        dir_rules=dir_rules,
        relative_path=relative_path,
        working_dir=working_dir,
    )

    cmd = [
        "claude",
        "-p",
        "--system-prompt",
        system_prompt,
        "--allowedTools",
        "Read",
        "Write",
        "Edit",
        "Glob",
        "Grep",
        "--max-turns",
        "25",
        "--output-format",
        "json",
        prompt_text,
    ]

    print(f"[agent] Spawning claude agent for {soc_file.name}", flush=True)
    print(f"[agent] Working directory: {working_dir}", flush=True)

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(working_dir),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()

    if stderr:
        print(f"[agent] stderr: {stderr.decode()}", flush=True)

    if proc.returncode != 0:
        print(
            f"[agent] claude exited with code {proc.returncode}", flush=True
        )
        return

    try:
        result = json.loads(stdout.decode())
        output_text = result.get("result", stdout.decode())
    except json.JSONDecodeError:
        output_text = stdout.decode()

    print(f"[agent] Output:\n{output_text}", flush=True)
    print(f"[agent] Done processing {soc_file.name}", flush=True)
