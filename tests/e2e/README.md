# End-to-end smoke harness (Layer B)

A **repeatable** end-to-end smoke test for the comeback flow: triage → subagents →
`freshness-checker` gate → artifacts. It has two halves:

- **The LLM run is manual / on-demand.** You drive the assistant through the
  canonical scenario yourself — there is no way to assert a language-model
  conversation deterministically in an automated suite.
- **The check is automated and deterministic.** [`check_artifacts.py`](check_artifacts.py)
  inspects the *run folder* the assistant produced and asserts its **shape** —
  files, structure, a matching `.docx`/`.pdf` pair, Cyrillic integrity, tracker
  zones. No LLM, no external dependencies (stdlib only).

> **This is not part of the automated suite.** The check needs a produced run
> folder, and every run folder lives under `Personal/` (git-ignored). So this
> harness is run **by hand, on demand** — it is deliberately kept out of
> `unittest discover` (the checker is not named `test*.py`, and its logic is
> guarded under `__main__`). The static invariant suite in `tests/test_*.py` —
> the one the pre-push gate runs — is untouched by it.

## Files

- [`fixture_martin.md`](fixture_martin.md) — the checked-in fixture: the canonical
  persona ("Мартин") and the six scripted persona turns. Fabricated, safe to commit.
- [`check_artifacts.py`](check_artifacts.py) — the deterministic artifact checker.
- `README.md` — this runbook.

## How to run

### 1. Drive the flow (manual)

Open this project in Claude Code and run the assistant against the fixture:

1. Invoke `/comeback` (or paste **Turn 1** from `fixture_martin.md` — it triggers
   the skill). The assistant becomes the orchestrator and bootstraps a run folder
   `Personal/<today>-martin[-suffix]/`.
2. Feed the six turns from `fixture_martin.md` **in order**, one at a time, letting
   the orchestrator respond and delegate (bg-navigator, search-strategist,
   cv-builder, interview-coach) and write files between turns. Use the target JD in
   the fixture verbatim for the CV-tailoring turn.
3. Note the run folder path it created.

### 2. Check the artifacts (deterministic)

```bash
python tests/e2e/check_artifacts.py Personal/<today>-martin/
```

Exit code `0` = every required check passed; `1` = at least one failed (with a
per-check report saying which). A missing optional tool (`pdftotext`) prints a
`SKIP` line and never fails the run.

## What PASS means

`check_artifacts.py` reports `RESULT: PASS` (exit 0) only when **all** of these hold
in the run folder:

- **`dossier.md`** exists and carries the required sections derived from
  `agent/dossier-template.md` — `## Profile`, `## Layoff facts`, `## Target`,
  `## CV`, `## Search`, `## Legal / benefits`, `## Log` — plus the `CV бриф` and
  `Tracker път` markers.
- **A tailored CV** `.docx` **and a matching** `.pdf` (same name, same folder) exist
  under the person's `cv/` subtree, and the `.pdf` is non-trivial (> ~10 KB) — i.e.
  the CV was actually rendered, not just stubbed.
- **Cyrillic integrity**: the `.docx` is opened with stdlib `zipfile`, and
  `word/document.xml` contains Cyrillic characters — so a mojibake / garbled render
  fails. If `pdftotext` is installed, the `.pdf` text is checked too; otherwise that
  sub-check is skipped with a printed note (no hard fail on the missing tool).
- **`tracker.md`** exists with the expected zones (Инерция, В движение, Изпратено
  чака, Цели, Затворени, Легенда) and columns (Компания, Роля, Статус, Следваща
  стъпка), derived from `agent/templates/tracker.md`.

A `FAIL` names the exact checks that did not hold, so you can see whether the gap is
a missing PDF render (LibreOffice not installed?), a garbled CV, or a step of the
flow that never ran.

## Notes

- **Nothing from a real run is committed.** The run folder is under `Personal/`,
  which `.gitignore` excludes. Only the fixture, checker, and this runbook are
  version-controlled.
- Stdlib only — runs on any Python 3.7+ with no `pip install`.
