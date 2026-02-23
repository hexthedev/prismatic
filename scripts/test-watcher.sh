#!/usr/bin/env bash
# Integration test for prismatic file watcher + trigger detection + agent spawning.
# Starts prismatic watching a temp folder, simulates file events, then cleans up.

set -euo pipefail

TEST_DIR="/tmp/test-watch"
PASS=0
FAIL=0

pass() { echo "  ✓ $1"; PASS=$((PASS + 1)); }
fail() { echo "  ✗ $1"; FAIL=$((FAIL + 1)); }

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

echo "=== Test 2: @claude trigger (should detect + clear file after agent) ==="
cat > "$TEST_DIR/projects/dump.md" << 'EOF'
@claude

ok so I had a few ideas today. First, a card game where you build a dungeon
and other players have to navigate it. Second, maybe a flashcard app that
uses spaced repetition but with a twist - you can challenge friends.
Also need to remember to cancel that subscription and book dentist appointment.
EOF
sleep 15

echo "--- dump.md after processing ---"
DUMP_CONTENT=$(cat "$TEST_DIR/projects/dump.md")
echo "'$DUMP_CONTENT'"
if [ -z "$DUMP_CONTENT" ]; then
  pass "@claude trigger cleared file contents"
else
  fail "@claude trigger did NOT clear file contents: '$DUMP_CONTENT'"
fi
echo "---"

echo "=== Test 3: @safe.claude trigger (should preserve file minus tag) ==="
cat > "$TEST_DIR/projects/safe-dump.md" << 'EOF'
@safe.claude

Here are some ideas I want to keep around:
- Build a roguelike deck builder
- Try out that new pasta recipe
EOF
sleep 15

echo "--- safe-dump.md after processing ---"
SAFE_CONTENT=$(cat "$TEST_DIR/projects/safe-dump.md")
echo "'$SAFE_CONTENT'"
if [ -n "$SAFE_CONTENT" ]; then
  pass "@safe.claude preserved file contents"
else
  fail "@safe.claude did NOT preserve file contents"
fi
if echo "$SAFE_CONTENT" | grep -q "@safe.claude"; then
  fail "@safe.claude tag was NOT removed from file"
else
  pass "@safe.claude tag was removed from file"
fi
echo "---"

echo "=== Test 4: Case-insensitive _DIR.md lookup ==="
mkdir -p "$TEST_DIR/lowercase-dir"
cat > "$TEST_DIR/lowercase-dir/_dir.md" << 'EOF'
# Lowercase Dir Note
## Rules
- Just organize the content
EOF
cat > "$TEST_DIR/lowercase-dir/test-lower.md" << 'EOF'
@safe.claude

Testing lowercase _dir.md detection.
EOF
sleep 15

echo "--- test-lower.md after processing ---"
LOWER_CONTENT=$(cat "$TEST_DIR/lowercase-dir/test-lower.md")
echo "'$LOWER_CONTENT'"
if [ -n "$LOWER_CONTENT" ]; then
  pass "Lowercase _dir.md: file preserved with @safe.claude"
else
  fail "Lowercase _dir.md: file was unexpectedly cleared"
fi
echo "---"

echo "=== Test 5: @claude at vault root (no _DIR.md) ==="
echo "hey @claude do something" > "$TEST_DIR/rootfile.md"
sleep 2

echo "--- rootfile.md after consumption ---"
cat "$TEST_DIR/rootfile.md"
echo "---"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
echo "=== All tests complete ==="
