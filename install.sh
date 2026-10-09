#!/usr/bin/env bash
# Install the game-studio skill and its agents without the plugin system.
#   bash install.sh /path/to/your-game   -> <game>/.claude/skills + .claude/agents (commit them; works in cloud sessions)
#   bash install.sh --user               -> ~/.claude/skills + ~/.claude/agents (this machine only)
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)/plugins/game-studio"
case "${1:-}" in
  --user) DEST="$HOME/.claude" ;;
  "") echo "usage: bash install.sh /path/to/your-game   |   bash install.sh --user" >&2; exit 2 ;;
  *) [ -d "$1" ] || { echo "error: $1 is not a directory" >&2; exit 2; }; DEST="$(cd "$1" && pwd)/.claude" ;;
esac
mkdir -p "$DEST/skills" "$DEST/agents"
rm -rf "$DEST/skills/game-studio"
cp -R "$SRC/skills/game-studio" "$DEST/skills/game-studio"
cp "$SRC/agents/"*.md "$DEST/agents/"
echo "Installed skill:  $DEST/skills/game-studio"
echo "Installed agents: $(cd "$SRC/agents" && ls *.md | sed 's/\.md$//' | tr '\n' ' ')-> $DEST/agents"
echo "Start a new Claude Code session in the project and paste the prompt from PROMPT.md."
