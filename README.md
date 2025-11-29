# Gemini Wedding Retoucher

A thin Python CLI that shells Google’s Nano-Banana / Gemini image-generation API to lightly retouch Korean-style wedding photos. It focuses on subtle, natural refinements (clean skin, tidy proportions, tasteful wardrobe polish) while preserving the scene, outfits, and expressions exactly as captured.

## Requirements
- Python 3.11+
- Access to Google’s Gemini ("Nano-Banana") image generation endpoint and API key
- `inputs/` directory for source photos (provided, stays git-ignored)
- `outputs/` directory for generated photos (provided, git-ignored)

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # set GOOGLE_API_KEY inside
```
The CLI will auto-load `.env` if `python-dotenv` is available (already part of `requirements.txt`). You can also export `GOOGLE_API_KEY` directly in your shell.

## Usage
All commands run from the project root after activating the virtual environment.

```bash
# List bundled prompt snippets
python -m gemini_pic --list-prompts

# Retouch a single photo with the default prompt
python -m gemini_pic --input inputs/bride.png --prompt-id korean_wedding_soft_refine

# Use a folder of photos (every supported file inside is processed)
python -m gemini_pic --input inputs/wedding_batch --prompt-id korean_wedding_soft_refine

# Override the prompt inline (helpful for quick experimentation)
python -m gemini_pic --input inputs/bride.png --prompt-text "Describe the desired look"

# Load a custom prompt from an external file
python -m gemini_pic --input inputs/bride.png --prompt-file prompts/my_alt.txt
```
Results land in `outputs/` (filename stem + timestamp). Use `--output-dir` to override.

### Helpful flags
- `--model`: defaults to `gemini-3-pro-image-preview`. Change if Google introduces a better Nano-Banana model.
- `--verbose`: surface debug logs (API payloads aren’t logged, just tracing info).
- `--sample-input` / `--sample-output`: supply a before/after reference pair. The CLI automatically switches to the matching `_with_sample` prompt and sends the sample images to Gemini (input first, sample input second, sample output third).
- `--top-level-only`: when the input path is a directory, only consider files directly inside it (no recursion).
- `--stride N`: when the input path is a directory, process every Nth image in sorted order (default 1). Combine with `--top-level-only` to handle “first, skip two” batching.
- `--max-retries` / `--max-sleep`: configure the retry budget (default 10 attempts, max 30 s sleep). Requests use exponential backoff and skip the image if all attempts fail.
- `--resume-from-killed`: skip any image whose output prefix already exists in the `--output-dir`, which lets you restart after an interrupted batch without reprocessing completed files.

## Sample-guided retouching
When you want Gemini to mimic the exact finish of an existing refinement, pass a sample pair:

```bash
python -m gemini_pic \
  --input inputs/original/jsw_0004.jpg \
  --sample-input inputs/pre-refined/jsw_0001.jpg \
  --sample-output inputs/pre-refined/jsw_0001_beauty_retouched.png \
  --prompt-id korean_wedding_original_duo
```

The CLI automatically loads `korean_wedding_original_duo_with_sample`, then calls the API with three images in order: target photo, sample input, and sample output. The bundled `_with_sample` prompts explicitly describe this order so Gemini understands which reference demonstrates the desired finish. Omit the sample flags to fall back to the base prompt.

**Important:** Gemini must only refine and return the first image. The sample pair is a style/completion reference—never blend their subjects, backgrounds, or outfits into the target scene.

## Retry and resume
- Every Gemini request now uses exponential backoff (starting at 1 s, capped at 30 s) for up to 10 attempts. If all retries fail, the CLI logs the error and moves on to the next file.
- Pass `--resume-from-killed` to look at the filenames already present in `outputs/` and skip any matching sources (based on the stem before `__`). This is handy if the process was killed mid-run—you can restart immediately without duplicating work.

### Process every third file example
```bash
python -m gemini_pic \
  --input inputs/original \
  --prompt-id korean_wedding_original_duo \
  --top-level-only \
  --stride 3
```
The command above sorts the files directly under `inputs/original`, runs the first file, skips the next two, and repeats (non-recursive).

## Prompts
Prompt snippets live in `prompts/*.txt`. Add your own files to extend the library—each file name (without `.txt`) becomes a `--prompt-id`. The included `korean_wedding_soft_refine` prompt encodes the natural-elegant retouching guidelines from the project definition.

### Included prompt IDs
- `korean_wedding_soft_refine`: general-purpose natural retouch pass that keeps the full scene intact.
- `korean_wedding_original_duo`: untouched bride + groom photos; balance both subjects equally.
- `korean_wedding_original_men`: untouched groom-only portraits; emphasizes structured suits.
- `korean_wedding_original_women`: untouched bride-only portraits; focuses on airy glow and graceful posture.
- `korean_wedding_prerefined_duo`: pre-edited couple shots; undo prior distortions before polishing.
- `korean_wedding_prerefined_men`: pre-edited groom portraits; restore realistic anatomy and fabric detail.
- `korean_wedding_prerefined_women`: pre-edited bride portraits; fix plastic skin or warped dresses while keeping elegance.

Every prompt also has a `_with_sample` companion that assumes you pass `--sample-input`/`--sample-output`. Each companion prompt spells out the image order (target → sample input → sample output) so Gemini can learn the reference transformation before applying it to the new photo.

## Failure handling
The CLI fails fast: missing inputs, absent prompt text, or API errors raise immediately and exit with code 1. Check the logs for actionable context. Once an image is submitted, every returned inline image part is saved; if the API returns no pixels, you’ll get a descriptive error.
