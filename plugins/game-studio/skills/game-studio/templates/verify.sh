#!/usr/bin/env bash
# qa/verify.sh: one entry point for the automated gates of a web (Vite + TypeScript) game.
#   bash qa/verify.sh --quick   G1 static + G2 logic (fast; suitable for a Stop hook)
#   bash qa/verify.sh           + G3 boot smoke, budgets, leak test and captures against a dev server
# Adapt the commands to the project; keep the structure: every step prints its result and the script
# exits non-zero if any step failed.
#
# The game-studio scripts folder is found in this order:
#   $GAME_STUDIO_SCRIPTS · the path stored in qa/.game-studio-scripts (the director writes it at the start
#   of each session; gitignored) · .claude/skills/game-studio/scripts · ~/.claude/skills/game-studio/scripts
set -u
cd "$(dirname "$0")/.." || exit 2
MODE="${1:-full}"
PORT="${QA_PORT:-5199}"
OUT="qa/out/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"
fail=0

step() {  # step "<name>" cmd args...
  local name="$1"; shift
  printf '== %s\n' "$name"
  if "$@" > "$OUT/${name// /_}.log" 2>&1; then
    printf '   ok\n'
  else
    printf '   FAILED (log: %s)\n' "$OUT/${name// /_}.log"
    tail -20 "$OUT/${name// /_}.log" | sed 's/^/   | /'
    fail=1
  fi
}
has_script() { grep -q "\"$1\"[[:space:]]*:" package.json 2>/dev/null; }
find_scripts() {
  local c
  for c in "${GAME_STUDIO_SCRIPTS:-}" "$(cat qa/.game-studio-scripts 2>/dev/null)" \
           ".claude/skills/game-studio/scripts" "$HOME/.claude/skills/game-studio/scripts"; do
    [ -n "$c" ] && [ -f "$c/web/capture.mjs" ] && { echo "$c"; return 0; }
  done
  return 1
}

# G1 static
[ -f tsconfig.json ] && step "typecheck" npx tsc --noEmit
has_script lint && step "lint" npm run -s lint
has_script depcheck && step "layer rules" npm run -s depcheck
# G2 logic
has_script test && step "unit tests" npm test --silent

if [ "$MODE" != "--quick" ]; then
  # G3 boot smoke + budgets + leak test + captures (needs playwright in devDependencies)
  if ! SCRIPTS="$(find_scripts)"; then
    printf '== boot smoke\n   FAILED: game-studio scripts not found; write their absolute path to qa/.game-studio-scripts\n'; fail=1
  else
    npx vite --port "$PORT" --strictPort > "$OUT/devserver.log" 2>&1 &
    SERVER=$!
    trap 'kill $SERVER 2>/dev/null' EXIT
    for _ in $(seq 1 60); do curl -sf "http://localhost:$PORT/" > /dev/null && break; sleep 0.5; done
    BUDGETS=(); [ -f design/budgets.json ] && BUDGETS=(--budgets design/budgets.json)
    step "boot smoke" node "$SCRIPTS/web/capture.mjs" --url "http://localhost:$PORT/?qa=1&seed=1234" \
      --out "$OUT/captures" --sequence 8 --step-ms 125 --reloads 5 ${BUDGETS[@]+"${BUDGETS[@]}"}  # bash 3.2-safe
    kill $SERVER 2>/dev/null
  fi
fi

printf '\nVERIFY: %s  (logs and captures: %s)\n' "$([ $fail -eq 0 ] && echo PASS || echo FAIL)" "$OUT"
exit $fail
