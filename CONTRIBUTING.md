# Contributing

**Read [CLAUDE.md](CLAUDE.md) first.** It is the source of truth for architecture and conventions; this file only points at the essentials.

## Language

Bulgarian for user-facing content (the agent's replies, the guide, templates, mode playbooks). English for everything else — code, config, docs, and commit messages.

## Architecture

One **orchestrator** ([agent/orchestrator.md](agent/orchestrator.md)) holds the relationship and routes work to **subagents** ([.claude/agents/](.claude/agents/)), which are bounded tools it calls. The `freshness-checker` subagent independently verifies institutional facts (НАП / НОИ / Бюро по труда) in another subagent's output — producer ≠ checker.

## Versioning & workflow

This project follows [SemVer](https://semver.org/). Every change bumps the top-level `VERSION` file, gets an annotated tag (`git tag -a vX.Y.Z -m "…"`), and adds a [CHANGELOG.md](CHANGELOG.md) entry ([Keep a Changelog](https://keepachangelog.com/) format).

## Local test gate

The full test suite must pass before every push. This is enforced locally by a version-controlled `pre-push` hook (`.githooks/pre-push`) — there is no server-side CI. Enable it once per clone:

```bash
git config core.hooksPath .githooks
```

From then on, `git push` first runs `python -m unittest discover -s tests` and **aborts the push (non-zero exit) if any test fails**. To run the suite by hand at any time:

```bash
python -m unittest discover -s tests
```

The hook is stdlib-only and picks a working Python interpreter automatically. (The e2e smoke harness in `tests/e2e/` is deliberately *not* part of this suite — see its runbook.)

## Licensing

By contributing you agree that code contributions are licensed under [MIT](LICENSE), and contributions to `knowledge-base/` content under [CC BY-NC 4.0](knowledge-base/LICENSE).

## Optional tooling

**LibreOffice** (optional, but recommended) is the primary path for exporting tailored CVs to PDF. The `/tailor-cv` skill renders the `.docx` and then converts it to PDF with LibreOffice in headless mode:

```bash
soffice --headless --convert-to pdf --outdir <folder> <folder>/<file>.docx
```

We use LibreOffice because it renders **Cyrillic (Bulgarian) reliably** — verified end-to-end (docx → PDF → extracted text round-trips Cyrillic, en-dashes, and `€`).

- **Windows:** installed at `C:\Program Files\LibreOffice\program\soffice.exe`; it is **not on `PATH`**, so call it by full path (`"/c/Program Files/LibreOffice/program/soffice.exe"` from the Bash tool). It prints a harmless `Could not find platform independent libraries` warning and still exits 0 — verify the `.pdf` was written rather than trusting the log.
- **macOS/Linux:** install LibreOffice; `soffice` (or `libreoffice`) is on `PATH`.

If LibreOffice isn't installed, the flow degrades cleanly: the `.docx` is delivered as the primary artifact and the PDF is left for the person to export themselves (Word / Google Docs → Save as PDF also preserves Cyrillic). Never ship a PDF with broken Cyrillic instead.

**python-docx** (or the harness `docx` skill) is the CV pipeline's `.docx` writer — the `/tailor-cv` render step builds the `.docx` with it before the LibreOffice PDF step above. When the `docx` skill is in context the pipeline uses it; otherwise it falls back to the `python-docx` package. If neither is available, `.docx` rendering can't proceed, so install `python-docx` (`pip install python-docx`) when running the CV pipeline outside the harness.

## Never commit person data

All files generated for a person live under `Personal/` (git-ignored). Never commit them.
