#!/usr/bin/env bash
# Integration test for prismatic file watcher + trigger detection + agent spawning.
# Starts prismatic watching a temp folder, simulates file events, then cleans up.

set -euo pipefail

TEST_DIR="/tmp/test-watch"

# Clean up from previous runs
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR/projects/game-ideas"

# Set up a _DIR.md with real instructions
cat > "$TEST_DIR/projects/_DIR.md" << 'EOF'
# Projects Folder

This folder contains project ideas and notes.

## Rules
- Summarize raw notes into a clean bullet-point list
- Create or update a file called `summary.md` in this folder with the organized content
- Group related ideas together under headings
- Preserve all information from the original note, just organize it
EOF

# Start prismatic in the background
uv run prismatic "$TEST_DIR" &
PID=$!
trap "kill $PID 2>/dev/null; wait $PID 2>/dev/null; rm -rf $TEST_DIR" EXIT
sleep 1

echo "=== Test 1: File without trigger ==="
echo "just a normal note" > "$TEST_DIR/projects/game-ideas/notes.md"
sleep 1

echo "=== Test 2: File with @claude trigger (should detect + spawn agent) ==="
cat > "$TEST_DIR/projects/dump.md" << 'EOF'
@claude

ok so I had a few ideas today. First, a card game where you build a dungeon
and other players have to navigate it. Second, maybe a flashcard app that
uses spaced repetition but with a twist - you can challenge friends.
Also need to remember to cancel that subscription and book dentist appointment.
EOF
sleep 15

echo "--- dump.md after consumption ---"
cat "$TEST_DIR/projects/dump.md"
echo "---"

echo "=== Test 3: File with @claude at vault root (no _DIR.md) ==="
echo "hey @claude do something" > "$TEST_DIR/rootfile.md"
sleep 2

echo "--- rootfile.md after consumption ---"
cat "$TEST_DIR/rootfile.md"
echo "---"

echo "=== All tests complete ==="
