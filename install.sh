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
# Preserve existing skill customizations and same-name agents on upgrade.
BACKUP=""
backup_existing() {
  local current="$1" relative="$2"
  [ -e "$current" ] || return 0
  if [ -z "$BACKUP" ]; then
    mkdir -p "$DEST/game-studio-backups"
    BACKUP=$(mktemp -d "$DEST/game-studio-backups/install.XXXXXX")
  fi
  mkdir -p "$(dirname "$BACKUP/$relative")"
  mv "$current" "$BACKUP/$relative"
}
backup_existing "$DEST/skills/game-studio" "skills/game-studio"
for agent_file in "$SRC/agents/"*.md; do
  backup_existing "$DEST/agents/$(basename "$agent_file")" "agents/$(basename "$agent_file")"
done
cp -R "$SRC/skills/game-studio" "$DEST/skills/game-studio"
cp "$SRC/agents/"*.md "$DEST/agents/"
echo "Installed skill:  $DEST/skills/game-studio"
echo "Installed agents: $(cd "$SRC/agents" && ls *.md | sed 's/\.md$//' | tr '\n' ' ')-> $DEST/agents"
echo "Start a new Claude Code session in the project and paste the prompt from PROMPT.md."
if [ -n "$BACKUP" ]; then echo "Previous installation preserved: $BACKUP"; fi
