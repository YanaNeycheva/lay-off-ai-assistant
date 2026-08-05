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

## Architecture

The agent runs on one **system prompt** (`agent/system-prompt.md`) and switches between **modes** (`agent/modes/*.md`). Every session starts in **triage**, which reads where the person is and routes them. The **support** layer is not a mode you leave — it runs underneath every other mode.

Modes:
- `triage` — assess situation + emotional state, route.
- `cv` — build / tailor / ATS-check / reframe the layoff.
- `interview` — mock interviews, the layoff story, delivery feedback.
- `search` — networking-first strategy, tracking, outreach.
- `support` — the steadying layer (always on).

## Knowledge base

- `knowledge-base/guide.md` — the guide; the agent's primary grounding.
- `knowledge-base/bg-legal.md` — BG legal/benefits facts. **Time-sensitive.** Deadlines and percentages change; re-verify against НОИ / Агенция по заетостта before relying on them, and never give legal advice as certainty — point the person to the official source.
- `knowledge-base/sources.md` — where the guide's claims come from.

## Conventions

- This is a standalone git repo. Commit/push only when asked.
- Don't invent BG legal specifics — cite `bg-legal.md` and flag anything unverified.
- When the guide changes here, mirror it to the blog post (and vice versa).

## Next steps (living list)

- [ ] Finish `knowledge-base/guide.md` (full Bulgarian draft).
- [ ] Flesh out each mode playbook with concrete prompts + examples.
- [ ] Decide the delivery surface (Claude Project? standalone skill? web app?) — not yet chosen.
- [ ] Publish the guide to the blog via the `uncoach-` pipeline.
