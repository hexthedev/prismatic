#!/usr/bin/env bash
# Integration test for prismatic file watcher + trigger detection.
# Starts prismatic watching a temp folder, simulates file events, then cleans up.

set -euo pipefail

TEST_DIR="/tmp/test-watch"

# Clean up from previous runs
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR/projects/game-ideas"

# Set up a _DIR.md
cat > "$TEST_DIR/projects/_DIR.md" << 'EOF'
# Projects Folder
Organize content into subfolders.
EOF

# Start prismatic in the background
uv run prismatic "$TEST_DIR" &
PID=$!
trap "kill $PID 2>/dev/null; wait $PID 2>/dev/null; rm -rf $TEST_DIR" EXIT
sleep 1

echo "=== Test 1: File without trigger ==="
echo "just a normal note" > "$TEST_DIR/projects/game-ideas/notes.md"
sleep 1

echo "=== Test 2: File with @claude trigger (should detect + consume) ==="
echo "brain dump @claude organize this" > "$TEST_DIR/projects/dump.md"
sleep 2

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
