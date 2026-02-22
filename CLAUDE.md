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

## Development Guidelines

- This is a greenfield project — the repo is starting from scratch
- Keep the core file-watching and trigger-detection loop simple and reliable since it runs as a long-lived background process
- Folder rules should be flexible and user-defined (stored as markdown files within the vault itself)
- Processing should be idempotent where possible — re-processing the same SOC file shouldn't create duplicates
- The system should handle Obsidian Sync gracefully (partial writes, sync conflicts, etc.)
