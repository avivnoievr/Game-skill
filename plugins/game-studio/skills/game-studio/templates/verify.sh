#!/usr/bin/env bash
# qa/verify.sh: one entry point for the automated gates of a web (Vite + TypeScript) game.
#   bash qa/verify.sh --quick   G1 static + G2 logic (fast; suitable for a Stop hook)
#   bash qa/verify.sh           + G3 boot smoke, budgets, leak test and captures against a dev server
# Adapt the commands to the project; missing required checks are BLOCKED, never PASS. This template
# targets web/TypeScript projects. Native engines must replace these commands with their own gates.
# Skipping a non-applicable check requires a recorded reason in the project's gate definition;
# prototype rigor does not make required static, logic or boot checks optional.
#
# The game-studio scripts folder is found in this order:
#   $GAME_STUDIO_SCRIPTS · the path stored in qa/.game-studio-scripts (the director writes it at the start
#   of each session; gitignored) · .claude/skills/game-studio/scripts · ~/.claude/skills/game-studio/scripts
set -u
cd "$(dirname "$0")/.." || exit 2
MODE="${1:-full}"
case "$MODE" in full|--quick) ;; *) printf 'Usage: bash qa/verify.sh [--quick]\n' >&2; exit 2 ;; esac
PORT="${QA_PORT:-5199}"
OUT="qa/out/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"
fail=0
blocked() { printf '== %s\n   BLOCKED: %s\n' "$1" "$2"; fail=1; }

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
has_script() {
  node -e 'try { const p = JSON.parse(require("fs").readFileSync("package.json", "utf8"));
    process.exit(typeof p.scripts?.[process.argv[1]] === "string" && p.scripts[process.argv[1]].trim() ? 0 : 1);
    } catch { process.exit(1); }' "$1" 2>/dev/null
}
required_script() {
  if has_script "$2"; then step "$1" npm run -s "$2";
  else blocked "$1" "package.json must define a terminating '$2' check"; fi
}
find_scripts() {
  local c
  for c in "${GAME_STUDIO_SCRIPTS:-}" "$(cat qa/.game-studio-scripts 2>/dev/null)" \
           ".claude/skills/game-studio/scripts" "$HOME/.claude/skills/game-studio/scripts"; do
    [ -n "$c" ] && [ -f "$c/web/capture.mjs" ] && { echo "$c"; return 0; }
  done
  return 1
}

# G1 static
if has_script typecheck; then step "typecheck" npm run -s typecheck
elif [ -f tsconfig.json ] && [ -x node_modules/.bin/tsc ]; then step "typecheck" node_modules/.bin/tsc --noEmit
else blocked "typecheck" "define a typecheck script, or provide tsconfig.json and a local TypeScript installation"; fi
required_script "lint" lint
required_script "layer rules" depcheck
# G2 logic
required_script "unit tests" test

if [ "$MODE" != "--quick" ]; then
  # G3 boot smoke + budgets + leak test + captures (needs playwright in devDependencies)
  for f in design/brief.md design/research.md design/plan.md design/art-bible.md design/features.json design/budgets.json design/assets.json progress.md; do
    [ -f "$f" ] || blocked "scaffold" "missing required state file: $f"
  done
  if [ "$fail" -ne 0 ]; then
    blocked "boot smoke" "resolve the static/logic/scaffold failures before starting the server"
  elif ! SCRIPTS="$(find_scripts)"; then
    blocked "boot smoke" "game-studio scripts not found; write their absolute path to qa/.game-studio-scripts"
  elif [ ! -x node_modules/.bin/vite ]; then
    blocked "boot smoke" "install Vite in this project; verification never downloads tools implicitly"
  else
    node_modules/.bin/vite --port "$PORT" --strictPort > "$OUT/devserver.log" 2>&1 &
    SERVER=$!
    trap 'kill $SERVER 2>/dev/null' EXIT
    for _ in $(seq 1 60); do curl -sf "http://localhost:$PORT/" > /dev/null && break; sleep 0.5; done
    step "boot smoke" node "$SCRIPTS/web/capture.mjs" --url "http://localhost:$PORT/?qa=1&seed=1234" \
      --out "$OUT/captures" --require-qa --budgets design/budgets.json --sequence 8 --step-ms 125 --reloads 5
    kill $SERVER 2>/dev/null
  fi
fi

printf '\nVERIFY: %s  (logs and captures: %s)\n' "$([ $fail -eq 0 ] && echo PASS || echo FAIL)" "$OUT"
exit $fail
