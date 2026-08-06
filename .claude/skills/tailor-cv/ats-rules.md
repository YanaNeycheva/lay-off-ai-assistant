# ATS rules & versioning (skill-local)

Self-contained ruleset for the `tailor-cv` skill. Adapted from the original CV project's AGENTS.md so the skill does not depend on any repo-root file. Applies to CVs in **any language** (Bulgarian or English) — the target job's language decides the CV language; the ATS rules are the same either way.

## ATS Optimization Rules

1. **Keyword matching** — include exact keywords from the target job description; use the posting's own terminology (if it says "project management", don't only say "led projects").
2. **Standard section headings** — `Summary`, `Work Experience`, `Education`, `Skills`, `Certifications` (BG: `Резюме`, `Опит`, `Образование`, `Умения`, `Сертификати`). No creative headings.
3. **Clean formatting** — single column; no tables, text boxes, headers/footers, or columns. Scanners read top-to-bottom, left-to-right.
4. **No images or graphics** — plain text only.
5. **Dates** — consistent `Month YYYY – Month YYYY` or `YYYY – YYYY`, always with start and end.
6. **Contact info** — name, email, phone, LinkedIn, location at the very top.
7. **Skills section** — comma-separated keywords or a simple bulleted list, grouped by category.
8. **Bullet points for experience** — each bullet starts with a strong action verb.
9. **Quantify achievements** — numbers where possible ("reduced processing time by 30%", "managed a team of 8").
10. **File format** — deliver both `.docx` (ATS-primary) and `.pdf` (human-readable).

## Versioning convention

Never overwrite a previous version. Every change creates a new versioned file.

- Base filename: `{UserNames} CV`.
- `{UserNames} CV_v1.0.docx` → minor tweaks bump the decimal (`v1.1`, `v1.2`); major changes (new role, big restructure, new target category) bump the whole number (`v2.0`).
- Maintain `{UserNames} CV_latest.docx` (copy of the newest version) and a `CHANGELOG.md` (one line per version) **inside the person's CV workspace**.

## Base-CV workflow (workspace root)

1. Read the current `{UserNames} CV_latest.docx`.
2. Make changes.
3. Save as the next version number (check `CHANGELOG.md` for the last one).
4. Update `{UserNames} CV_latest.docx`.
5. Add a one-line `CHANGELOG.md` entry.

If you need more input from the person, create `CV_info_needed.md` in the workspace for them to fill; use their answers to fill the gaps.

## Workspace layout

The person's CV workspace (path is given by the caller — the `cv-builder` subagent / orchestrator, per the dossier; **never** the project repo root):

```
<cv-workspace>/
  {UserNames} CV_latest.docx        ← canonical base CV
  {UserNames} CV_v1.x.docx          ← versioned base CVs
  CHANGELOG.md
  CV_info_needed.md                 ← gap Q&A (base level)
  YYYY-MM-DD_Company_Position/      ← one folder per tailored position
    position.md
    CV_info_needed.md
    {UserNames} CV - Company - Position.docx
    {UserNames} CV - Company - Position.pdf
```
