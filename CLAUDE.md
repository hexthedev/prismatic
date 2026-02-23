# Prismatic

## What This Project Is

Prismatic is a long-lived process that watches an Obsidian vault for file changes and automatically organizes stream-of-consciousness (SOC) notes into structured documentation using Claude agents.

### The Problem

Capturing ideas on-the-go (often via voice-to-text on a phone) is easy with Obsidian Sync. But raw stream-of-consciousness dumps are messy — ideas for games, flashcards, life admin, and more all land as unstructured text. Manually sorting that text into the right places in a well-organized vault is tedious and rarely gets done.

### The Solution

Prismatic runs on a home computer, watches the Obsidian vault via the filesystem, and reacts to trigger keywords in files. When triggered, it spins up a Claude agent that:

1. Reads the **folder-specific rules** (each folder can define how its content should be organized and structured)
2. Reads the **triggered file's raw text** (the SOC dump)
3. **Processes and distributes** the information into the correct places according to the folder's rules

## Architecture

### Core Loop

```
Obsidian Vault (synced via Obsidian Sync)
  └── File change detected (filesystem watcher)
        └── Trigger keyword found in file?
              └── Yes → Spawn Claude agent
                    ├── Read folder rules/instructions
                    ├── Parse SOC text
                    └── Organize content into proper locations
```

### Key Concepts

- **Trigger keyword**: A specific keyword present in a file that signals Prismatic to process it. This is how the user opts in to processing — not every file change should be acted on.
- **Folder rules**: Each folder in the vault can have instructions defining how content in that folder should be organized, what structure to follow, and where different types of information belong.
- **SOC files**: Stream-of-consciousness files — raw, unstructured text dumps typically created via voice-to-text on mobile. These are the primary input that Prismatic processes.

## Tech Decisions

- **Language**: Python
- **Package management**: [uv](https://docs.astral.sh/uv/) — all dependency management, virtual environments, and script running go through `uv`
- **Distribution**: The project must be invocable via `uvx prismatic` — package accordingly (proper `pyproject.toml` with `[project.scripts]` entry point)
- **File watching**: Filesystem-level watching of the Obsidian vault directory
- **Obsidian integration**: Prismatic reads/writes Obsidian markdown files directly on disk. It may also use the Obsidian Local REST API or MCP server for richer interaction.
- **Claude integration**: Uses the Anthropic API to spawn agents that process SOC content according to folder rules

## Project Structure

```
prismatic/
├── pyproject.toml          # Project config, dependencies, entry point
├── src/prismatic/          # Application source code
│   ├── __init__.py         # Entry point (main function)
│   ├── watcher.py          # Async file watcher (watchfiles.awatch)
│   ├── trigger.py          # Trigger detection, consumption, agent dispatch
│   └── agents/
│       ├── __init__.py
│       └── obsidian.py     # Claude CLI subprocess agent for vault processing
├── scripts/                # Reusable test/dev scripts
│   └── test-watcher.sh     # Integration test for file watcher + triggers
└── CLAUDE.md
```

- Entry point: `prismatic:main` (invoked via `uv run prismatic` or `uvx prismatic`)
- Source layout: uv default `src/` layout

## Git Workflow

- **Always work on a branch, never commit directly to `main`.**
- Every body of work must have an open PR. Before starting work, create a new branch and open a PR for it. If the current branch doesn't have an open PR, create one.
- Push commits to the branch as work progresses so the user can review via the PR interface.
- The `claude.yml` GitHub Action is kept active so the user can `@claude` in PR comments. The `claude-code-review.yml` auto-review is disabled since code is written by Claude Code locally.

## Testing

- For integration tests that involve running prismatic as a background process and simulating file events, **write reusable bash scripts in `scripts/`** rather than inline multi-line shell commands. This avoids repeated permission prompts and makes tests easy to re-run and modify.
- Run integration tests via `bash scripts/test-watcher.sh` (or similar).
- When planning work, if a feature will need repeated manual testing, include a test script as part of the deliverable.

## Development Guidelines

- This is a greenfield project — the repo is starting from scratch
- Keep the core file-watching and trigger-detection loop simple and reliable since it runs as a long-lived background process
- Folder rules should be flexible and user-defined (stored as markdown files within the vault itself)
- Processing should be idempotent where possible — re-processing the same SOC file shouldn't create duplicates
- The system should handle Obsidian Sync gracefully (partial writes, sync conflicts, etc.)
