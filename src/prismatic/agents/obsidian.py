import asyncio
import json
from pathlib import Path

CLARIFICATION_MARKER = "<!-- prismatic:needs-clarification -->"

SYSTEM_PROMPT_TEMPLATE = """\
You are operating on an Obsidian vault folder.

## Folder Rules (_DIR.md)
{dir_rules}

## Context
The triggered file is at: {relative_path}
The working directory is: {working_dir}

Process the file content below according to the folder rules above.

## Asking Clarifying Questions

If you encounter genuine ambiguity that prevents you from confidently processing the file,
you may ask the user for clarification instead of guessing. Use this sparingly — only when
the ambiguity is significant enough that proceeding would likely produce the wrong result.

To ask clarifying questions, overwrite the SOC file ({relative_path}) with this exact format:

```
{clarification_marker}

## I need a few clarifications before proceeding

[1-2 sentences summarising what you understood from the content]

**Questions:**
1. [Question 1]
2. [Question 2]

---

*Original content:*

[paste the original file content here verbatim]
```

After writing that file, stop — do not do any other processing. Prismatic will detect the
marker, preserve the file, and wait for the user to answer. The user will edit the file
inline, then re-trigger with @claude when ready.\
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
        clarification_marker=CLARIFICATION_MARKER,
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
        "100",
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
