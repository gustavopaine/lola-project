# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Lola: an AI-generated virtual influencer for the BIG GOOD food truck (Patagonia,
Argentina). The pipeline turns a Spanish script into a talking-head video of Lola:
text → face image (SDXL) → voiceover (gTTS/XTTS-v2) → lip-synced video (SadTalker).

## Hybrid execution model — read this before editing anything

Code is edited/versioned locally (VS Code, no GPU). All actual generation
(image/voice/video) runs on Google Colab (free GPU), via `colab_bootstrap.ipynb`.

- `src/identidad.py`, `src/animacion.py`, and `generate_voiceover_clonada` in
  `src/voz.py` do their heavy imports (`torch`, `diffusers`, `TTS`) **inside the
  function body**, not at module level. This is intentional: it lets the whole
  package be imported locally for linting/autocomplete without a GPU or these
  packages installed. Keep new GPU-dependent modules following this pattern.
- `src/animacion.py` (SadTalker) only works inside the Colab environment set up
  by the bootstrap notebook (needs the SadTalker repo cloned alongside, and
  `python3.8`). It cannot be run or tested locally.
- Workflow: edit in VS Code → `git push` → in Colab, open
  `colab_bootstrap.ipynb` and run all 15 cells in order → call `init_lola(...)`.

## Architecture

Four-stage pipeline, each stage a module in `src/`, chained by the orchestrator:

1. **`src/config.py`** — `LOLA_CHARACTERISTICS` (the SDXL prompt that keeps
   Lola's face consistent across generations — deliberately kept under CLIP's
   77-token limit; do not lengthen it without checking token count) and
   `GUIONES` (dict of content-plan scripts, e.g. `dia_1`, `dia_3`...). Add new
   scripts here as new `SCRIPT_DIA_N` constants + an entry in `GUIONES`.
2. **`src/identidad.py`** (Etapa 1) — generates Lola's face with SDXL
   (`stabilityai/stable-diffusion-xl-base-1.0`), then resizes 1024→512 for
   SadTalker. `generate_avatar_image` frees GPU memory (`torch.cuda.empty_cache()`)
   after running — SadTalker runs right after and will hit
   `CUDNN_STATUS_NOT_INITIALIZED` if the SDXL pipeline is still resident.
3. **`src/voz.py`** (Etapa 2) — `generate_voiceover` (gTTS, CPU-only, default)
   or `generate_voiceover_clonada` (XTTS-v2 voice cloning, GPU, model cached in
   a module-level global after first load).
4. **`src/animacion.py`** (Etapa 3) — calls SadTalker's `inference.py` as a
   subprocess (`subprocess.run(capture_output=True)`) to produce the
   lip-synced video. `create_ai_influencer` snapshots `result_dir` (files
   *and* dirs — `_snapshot_results_entries`) before each attempt, then uses
   `_find_output_video` to diff against the post-run listing and locate the
   new run's `.mp4`. This has to check both, because SadTalker's own
   `inference.py`, on success, moves the final video to a loose `.mp4`
   sibling file and `shutil.rmtree`s its temp working dir (unless
   `--verbose` is passed, which we don't) — a new *directory* only shows up
   when the run failed partway through (README: "video con 0 segundos /
   carpeta solo con `first_frame_dir`"). Retries up to `max_retries` times
   (default 1) before raising `SadTalkerGenerationError` with the captured
   stderr. `diagnosticar_error` still exists for manual ad-hoc debugging
   outside `init_lola`. `still=False` (default) allows natural
   head movement; `still=True` restricts motion to lip-sync only.
5. **`src/orquestador.py`** (Etapa 4) — `init_lola(script_text, characteristics,
   reusar_imagen, pose_style, guion_id, max_retries, result_dir)` chains the
   three stages and returns the path to the final video (a single `str`, not
   a directory listing). Always pass `reusar_imagen=<path to the anchor
   image>` in normal use — regenerating Lola's face is expensive and
   reintroduces face-consistency drift; the versioned anchor is
   `examples/source_image/lola_512.png`. Pass `guion_id` (e.g. `"dia_1"`,
   matching a key in `GUIONES`) to get idempotency: if
   `{result_dir}/{guion_id}.mp4` already exists, generation is skipped
   entirely and that path is returned — this is what makes it safe to
   re-run a Colab cell without wasting GPU time regenerating a video that's
   already done. Without `guion_id`, behavior is the old one-off path with
   no dedup.

## Known environment gotchas (already patched in colab_bootstrap.ipynb)

If SadTalker/Colab setup ever needs to be redone or re-debugged, check the
troubleshooting table in `README.md` first — it documents real errors already
solved there (python3.8 pip/venv/dev headers, a `basicsr`/torchvision
compatibility patch, the SD 2.1→SDXL model swap after Stability AI deprecated
the old repo, the CUDNN GPU-memory issue, a SadTalker checkpoint release-tag
mismatch, and why `inference.py` needs an absolute image path plus `os.chdir()`
into `SadTalker/`).

## Tests

`tests/test_animacion.py` and `tests/test_orquestador.py` cover the
GPU-free logic only (result-dir diffing, output verification, retry loop,
idempotency) with `subprocess.run`/`liberar_gpu`/pipeline stages mocked —
they run locally, no Colab/GPU needed: `pip install -r requirements-dev.txt
&& pytest`. The actual GPU stages (SDXL, XTTS, SadTalker) have no test
coverage and can't be exercised outside Colab.

## Assets and secrets

- `examples/source_image/lola_512.png` is the only generated-image file tracked
  in git (the official anchor image) — `.gitignore` excludes all other PNGs
  under `examples/source_image/` and all WAVs under `examples/driven_audio/`.
- Local `.env` (see `.env.example`) is for lint/autocomplete reference only. On
  Colab, secrets (`OPENAI_API_KEY`, `HF_TOKEN`) are read via `userdata.get(...)`,
  not `.env`.
