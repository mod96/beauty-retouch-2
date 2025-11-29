#!/usr/bin/env bash
set -euo pipefail

DEST="${1:-./compare/women}"
INPUT_DIR="${2:-./inputs/original/women}"
mkdir -p "$DEST"
OUTPUT_DIR="$DEST"

if [[ ! -d "$INPUT_DIR" ]]; then
  echo "Input directory '$INPUT_DIR' does not exist." >&2
  exit 1
fi

extract_prefix() {
  local stem="$1"
  if [[ "$stem" == *_* ]]; then
    local IFS='_'
    local first second _
    read -r first second _ <<< "$stem"
    if [[ -n "$second" ]]; then
      printf '%s_%s\n' "$first" "$second"
      return
    fi
  fi
  printf '%s\n' "$stem"
}

# build a temp file with prefixes from destination (output) folder
PREFIX_FILE="$(mktemp)"
trap 'rm -f "$PREFIX_FILE"' EXIT

found_output=0
while IFS= read -r -d '' f; do
  found_output=1
  base="$(basename "$f")"
  name="${base%.*}"                                  # remove extension
  prefix="$(extract_prefix "$name")"                 # prefix up to second underscore
  printf '%s\n' "$prefix" >> "$PREFIX_FILE"
done < <(find "$OUTPUT_DIR" -maxdepth 1 -type f -print0)

if [[ "$found_output" -eq 0 ]]; then
  echo "No output files found in $OUTPUT_DIR; nothing to copy."
  exit 0
fi

# deduplicate
sort -u -o "$PREFIX_FILE" "$PREFIX_FILE"

# for each file in the input directory, check if its stem is in the prefix list
while IFS= read -r -d '' f; do
  base="$(basename "$f")"
  stem="${base%.*}"
  b_prefix="$(extract_prefix "$stem")"
  if grep -qxF "$b_prefix" "$PREFIX_FILE"; then
    echo "Copying $f -> $DEST/"
    cp -np "$f" "$DEST/"
  fi
done < <(find "$INPUT_DIR" -maxdepth 1 -type f -print0)
