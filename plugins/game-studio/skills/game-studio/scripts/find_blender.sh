#!/usr/bin/env bash
# Print the first working Blender 4.2+ executable as: absolute-path<TAB>version.
# This probes a factory scene; it never opens or changes the developer's .blend.
set -euo pipefail
if [ "${1:-}" = "--help" ]; then
  echo 'usage: bash find_blender.sh   (optional BLENDER=/absolute/path/to/blender)'
  exit 0
fi
if [ "$#" -ne 0 ]; then echo 'find_blender.sh takes no arguments' >&2; exit 2; fi

probe() {
  local candidate="$1" output version major minor candidate_dir
  [ -f "$candidate" ] && [ -x "$candidate" ] || return 1
  if ! output=$("$candidate" -b --factory-startup --python-exit-code 1 --python-expr \
    "import bpy; print('GS_BLENDER_PROBE\\t' + bpy.app.version_string)" 2>&1); then
    return 1
  fi
  version=$(printf '%s\n' "$output" | sed -n 's/^GS_BLENDER_PROBE[[:space:]]//p' | tail -n 1)
  [ -n "$version" ] || return 1
  major=${version%%.*}; minor=${version#*.}; minor=${minor%%.*}
  case "$major:$minor" in *[!0-9:]*|'') return 1 ;; esac
  if [ "$major" -lt 4 ] || { [ "$major" -eq 4 ] && [ "$minor" -lt 2 ]; }; then return 1; fi
  candidate_dir=$(cd "$(dirname "$candidate")" && pwd)
  printf '%s/%s\t%s\n' "$candidate_dir" "$(basename "$candidate")" "$version"
}

if [ -n "${BLENDER:-}" ]; then
  if probe "$BLENDER"; then exit 0; fi
  echo 'BLENDER does not name a working Blender 4.2+ executable; fix the override.' >&2
  exit 2
fi
if command -v blender >/dev/null 2>&1; then
  if probe "$(command -v blender)"; then exit 0; fi
fi
# Unmatched globs are harmless: probe requires an executable regular file.
for candidate in \
  /Applications/Blender*.app/Contents/MacOS/Blender \
  /c/Program\ Files/Blender\ Foundation/Blender*/blender.exe \
  /c/Program\ Files/Steam/steamapps/common/Blender/blender.exe \
  /c/Program\ Files\ \(x86\)/Steam/steamapps/common/Blender/blender.exe \
  "$HOME"/Library/Application\ Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender \
  "$HOME"/.local/share/Steam/steamapps/common/Blender/blender \
  "$HOME"/.steam/steam/steamapps/common/Blender/blender \
  "$HOME"/blender-*/blender \
  /snap/bin/blender; do
  if probe "$candidate"; then exit 0; fi
done
echo 'No working Blender 4.2+ found. Set BLENDER to the installed executable; do not install another copy automatically.' >&2
exit 2
