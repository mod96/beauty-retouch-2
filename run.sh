#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-women}"

case "$TARGET" in
  women)
    INPUT_PATH="inputs/original/women"
    PROMPT_ID="korean_wedding_original_women"
    STRIDE=5
    ;;
  men)
    INPUT_PATH="inputs/original/men"
    PROMPT_ID="korean_wedding_original_men"
    STRIDE=5
    ;;
  duo)
    INPUT_PATH="inputs/original"
    PROMPT_ID="korean_wedding_original_duo"
    STRIDE=1
    ;;
  *)
    echo "Usage: $0 {women|men|duo}" >&2
    exit 1
    ;;
esac

if [[ ! -d "$INPUT_PATH" ]]; then
  echo "Input path '$INPUT_PATH' not found." >&2
  exit 1
fi

source ./.venv/bin/activate

python -m gemini_pic \
  --input "$INPUT_PATH" \
  --prompt-id "$PROMPT_ID" \
  --top-level-only \
  --stride "$STRIDE" \
  --resume-from-killed

timestamp=$(date +%Y%m%d_%H%M%S)
compare_dir="./compare/${TARGET}_${timestamp}"
output_dir="./outputs"

mkdir -p "$compare_dir"

output_count=0
while IFS= read -r -d '' file; do
  mv "$file" "$compare_dir/"
  output_count=$((output_count + 1))
done < <(find "$output_dir" -maxdepth 1 -type f -print0)

if [[ "$output_count" -eq 0 ]]; then
  echo "No output files found in $output_dir; skipping compare sync."
  exit 0
fi

echo "Moved $output_count output(s) to $compare_dir"
./move_to_compare.sh "$compare_dir" "$INPUT_PATH"
