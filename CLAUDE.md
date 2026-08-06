# CLAUDE.md — comeback (laid-off support agent)

Read this before any task in this project.

## What this is

An interactive Bulgarian-language assistant for laid-off professionals. It supports one person through the whole job-search arc: emotional footing, CV, search strategy, and interviews. See `README.md` for the full rationale.

Sibling project: the `uncoachable.work` blog (one directory up). The guide in `knowledge-base/guide.md` is the shared source of truth and is also published as a blog post. Keep the two copies in sync when the guide changes.

## Language rules

- **User-facing content** (the agent's replies, the guide, templates, mode playbooks' example wording) → **Bulgarian**.
- **Everything else** (code, config, README, this file, commit messages, structural docs) → **English**.

## Voice

Inherited from the blog: **professional, sharp, generous.** The person is often anxious or ashamed — never talk down, never spew motivational filler. Be concrete, warm, and honest. Steady the person; don't perform empathy.

Avoid: clichés, corporate jargon, the "не защото…, а защото" construction, the word "неудобен" and its derivatives.

## Architecture (orchestrator + subagents)

**Entry point:** the `/comeback` skill (`.claude/skills/comeback/`) is the front door. It fires on `/comeback` or natural phrases ("съкратиха ме", "laid off", …), makes the main assistant adopt the orchestrator persona, bootstraps a per-person `work/<date>-<slug>/dossier.md`, and opens with triage. The orchestrator must be the top-level assistant (not a subagent) because subagents can't spawn subagents.

One **orchestrator** (`agent/orchestrator.md`) holds the relationship — triage, the always-on support layer, routing, and the single consistent voice. It delegates bounded, produce-an-artifact work to **subagents** (`.claude/agents/*.md`). The person only ever talks to the orchestrator; subagents are tools it calls.

Load-bearing rule: **the orchestrator is the relationship; subagents are tools.** Subagents start cold, so triage + support are never delegated.

- Orchestrator-owned (never delegated): `agent/triage.md`, `agent/support.md`.
- Subagents (`.claude/agents/`): `cv-builder` (drives the `/tailor-cv` skill), `interview-coach`, `search-strategist`, `bg-navigator`, `company-intel` (optional).

**Shared state:** a per-person `dossier.md` (schema in `agent/dossier-template.md`). Orchestrator and every subagent read/write it — this is how cold subagents get the person's full context. It lives in the person's working directory, **not** in this repo.

**CV engine:** the `cv-builder` subagent runs the vendored `/tailor-cv` skill (`.claude/skills/tailor-cv/`), which owns the ATS audit, JD capture, one-question-at-a-time gap analysis, and `.docx`/`.pdf` output. Its rules are skill-local in `ats-rules.md`.

## Knowledge base

- `knowledge-base/guide.md` — the guide; the agent's primary grounding.
- `knowledge-base/bg-legal.md` — BG legal/benefits facts. **Time-sensitive.** Deadlines and percentages change; re-verify against НОИ / Агенция по заетостта before relying on them, and never give legal advice as certainty — point the person to the official source.
- `knowledge-base/sources.md` — where the guide's claims come from.

## Conventions

- This is a standalone git repo. Commit/push only when asked.
- Don't invent BG legal specifics — cite `bg-legal.md` and flag anything unverified.
- When the guide changes here, mirror it to the blog post (and vice versa).

## Next steps (living list)

- [x] Full Bulgarian guide (`knowledge-base/guide.md`).
- [x] Restructure into orchestrator + subagents; vendor the `/tailor-cv` skill as the CV engine.
- [x] Entry-point `/comeback` skill (front door + per-person dossier bootstrap).
- [ ] **Test the flow end-to-end** (a real/sample persona through triage → subagents).
- [ ] Confirm `.docx`/`.pdf` rendering works (docx + pdf skills available in the harness).
- [ ] Flesh out `company-intel` only if we keep it (overlaps most with existing tools).
- [ ] Publish the guide to the blog via the `uncoach-` pipeline.
