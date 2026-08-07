---
name: tailor-cv
description: Tailor the base CV for a specific job position. Audits the base CV for ATS-cleanliness, captures the JD, asks one-question-at-a-time to fill gaps, and produces a position-specific .docx + .pdf inside a dated position folder. Trigger when the user (or the cv-builder subagent) wants to tailor the CV for a role. Works in Bulgarian or English — CV language follows the target job.
---

# /tailor-cv — Tailor CV for a Specific Position

> Rules live in [ats-rules.md](ats-rules.md) (skill-local — no repo-root dependency). All file paths are relative to the **person's CV workspace**, given by the caller. Never write CV files into the project repo root. `{UserNames}` = the person's full name (ask if unknown). CV language = the target job's language (BG or EN).

## Prerequisite check (do this FIRST)

The base CV in the workspace must be **ATS-clean** before tailoring.

1. Read [ats-rules.md](ats-rules.md) and the workspace `CHANGELOG.md`.
2. Read the latest base CV (`{UserNames} CV_latest.docx`, or the latest versioned file per CHANGELOG).
3. Audit it against the **ATS Optimization Rules**.
4. If anything is off (non-standard headings, tables, images, missing contact info, inconsistent dates, missing quantified achievements, etc.), **STOP** and say:
   > "The base CV has ATS issues I need to fix first before tailoring for this position. Want me to fix the base CV first?"
   Continue only once the base is clean (or the person explicitly overrides).

## Step 1 — Capture the position

Ask for it if not already given: **Job URL**, **Company name**, **Position title**. If a URL is given, fetch it (WebFetch) to extract the JD. If gated (LinkedIn often is), ask the person to paste the JD text.

## Step 2 — Create the position folder

`YYYY-MM-DD_Company_Position-Title/` in the workspace (today's date; underscores between fields, hyphens within multi-word fields). Inside, create `position.md`:

```markdown
# {Company} — {Position Title}

- **URL:** {job URL}
- **Captured:** {YYYY-MM-DD}
- **Source CV version:** {e.g. v1.1 from CHANGELOG.md}

## Job Description
{full JD text}

## Key requirements extracted
- {must-haves the JD calls out}

## Nice-to-haves
- {nice-to-haves}

## Keywords for ATS
{comma-separated exact keywords from the JD}
```

## Step 3 — Gap analysis (ONE question at a time)

Compare the JD against the base CV. For each gap or ambiguity:
1. Ask **ONE** question. Wait for the answer. Then the next.
2. Never batch questions — one at a time, on purpose.
3. Log answers in `CV_info_needed.md` inside the position folder.

If the person says "skip" / "no more", stop asking and proceed with what you have.

## Step 4 — Compose the tailored CV

Compose the tailored CV **content** (rendering happens in Step 5, after proofing). Starting from the base CV:
- Reposition title/summary to match the JD's title and language.
- Promote bullets matching JD requirements; demote/cut those that don't.
- Inject exact JD keywords **only where truthful — never fabricate experience**.
- Reorder skills to lead with JD-relevant ones.
- Keep every ATS rule from `ats-rules.md`.

## Step 5 — Proofread, then render

1. **Run the proofing pass** ([proofing.md](proofing.md)) on the composed text: dashes → en-dashes (without breaking legitimate hyphens), and a grammar/spelling check in the CV's language (BG or EN). Apply confident fixes; note anything ambiguous you left.
2. **Render** with the docx skill, then export PDF, inside the position folder:
   ```
   {UserNames} CV - {Company} - {Position Title}.docx
   {UserNames} CV - {Company} - {Position Title}.pdf
   ```
   Both live **inside the position folder**, never in the workspace root (root holds only the canonical base CV).

## Step 6 — Log it

Add to the workspace `CHANGELOG.md`:
```
## tailored — YYYY-MM-DD — {Company} {Position}
Tailored CV for {Company} {Position} ({JD URL}). Source: {base version}. Output: `{folder}/`.
```

## Step 7 — Summarize

Report: folder path · what changed vs. the base (3–5 bullets) · the proofing changes made (typography + grammar) · any open gaps to fill before submitting.
