# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.8] - 2026-09-01

### Added
- **LibreOffice as the primary CV → PDF path.** The `/tailor-cv` render step and `cv-builder`
  step 3 now convert the rendered `.docx` to PDF via `soffice --headless --convert-to pdf`,
  chosen because it renders **Cyrillic (Bulgarian) reliably** — verified end-to-end
  (docx → PDF → extracted text round-trips Cyrillic, en-dashes, and `€`).
  - `.claude/skills/tailor-cv/SKILL.md`: Step 5 now spells out the LibreOffice export command
    (full `soffice.exe` path on Windows, which is not on `PATH`) and a clean no-LibreOffice
    fallback — deliver the `.docx` and let the person export the PDF themselves rather than
    shipping mojibake.
  - `.claude/agents/cv-builder.md`: step 3 points at the same primary path + fallback.
  - `CONTRIBUTING.md`: new "Optional tooling" section documenting the LibreOffice dependency,
    the Windows full-path quirk, the harmless startup warning, and the graceful degradation.

## [0.1.7] - 2026-08-29

### Changed
- CV gap-gathering is now **front-loaded to the orchestrator**. `cv-builder` runs headless and
  only the orchestrator talks to the person, so `/tailor-cv`'s one-question-at-a-time gap analysis
  can't reach them through the subagent. The orchestrator now collects the CV inputs up front (one
  question at a time, in its own voice), records them in the dossier's CV section, and hands
  `cv-builder` a complete brief.
  - `agent/orchestrator.md`: added a "CV brief (front-load before delegating to cv-builder)" step
    with a checklist derived from the skill's real inputs.
  - `.claude/agents/cv-builder.md`: now expects a complete brief and **does not interview** the
    person; residual gaps are returned to the orchestrator to ask one-at-a-time. The batched
    `CV_info_needed.md` is demoted to a last-resort fallback.
  - `.claude/skills/tailor-cv/SKILL.md`: one-line note that headless runs draw gap inputs from the
    orchestrator brief and surface residual gaps back instead of prompting.
  - `agent/dossier-template.md`: added a "CV бриф (front-load)" block to the CV section.

## [0.1.6] - 2026-08-29

### Fixed
- `bg-navigator` can now write the dossier (added `Write` tool) — its spec directs it to
  write the personalized checklist to the dossier's legal/benefits section.
- `cv-builder` can now render `.docx`/`.pdf` (added `Bash` tool) — the `/tailor-cv` render
  skills it wraps need a shell.
- Aligned both subagents' declared tools with their own specs (no spec rewrites).

## [0.1.5] - 2026-08-29

### Changed
- `knowledge-base/bg-legal.md` independently verified against NSSI (НОИ) for 2026, now in euro.
  - ✅ Confirmed against official sources: eurozone entry + EUR amounts and the fixed rate
    1 EUR = 1.95583 BGN (noi.bg); maximum insurable income **2300 EUR** from 01.08.2026
    (nssi.bg/dohod01082026); minimum/maximum daily unemployment benefit **9.21 / 54.78 EUR**
    for 2026 (official NSSI bulletin `unempl_02_2026.pdf`).
  - Fixed the source URL on the daily-benefit row (the figures live in the NSSI bulletin, not
    the dohod page) and re-stamped the two euro-figure rows to 2026-08-29.
  - ⚠️ Still unverified (kept непроверено): transitional paper-record period (до 1 юни 2026 г.)
    and the Labour Code severance orientation.

## [0.1.4] - 2026-08-28

### Added
- `CONTRIBUTING.md` (concise; points to `CLAUDE.md` for the full conventions).
- A "Contributing" pointer in `README.md`.

## [0.1.3] - 2026-08-28

### Added
- Dual licensing: MIT for the code, CC BY-NC 4.0 for the `knowledge-base/` content.
- Top-level `LICENSE` (MIT, with a dual-split header) and `knowledge-base/LICENSE` (full CC BY-NC 4.0 legal code).
- A "License" section in `README.md` explaining the split.

## [0.1.2] - 2026-08-28

### Added
- `CHANGELOG.md` in Keep a Changelog format, covering the 0.1.x history.

### Changed
- Versioning policy in `CLAUDE.md` now requires a changelog entry per release.

## [0.1.1] - 2026-08-28

### Changed
- Moved all per-person files under a git-ignored `Personal/<date>-<slug>/` root.
- Corrected the `CLAUDE.md` dev-commit convention and the person-data rule.

## [0.1.0] - 2026-08-27

### Added
- Full Bulgarian guide (`knowledge-base/guide.md`).
- Orchestrator + subagents architecture.
- Vendored `/tailor-cv` skill as the CV engine.
- `/comeback` entry-point skill (front door + per-person dossier bootstrap).
- `freshness-checker` verification gate for institutional facts.
- SemVer adoption and top-level `VERSION` file.
