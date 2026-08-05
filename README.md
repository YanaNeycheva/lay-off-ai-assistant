# comeback

An interactive assistant that supports a laid-off professional through the whole arc of finding their next job — from the shock of the layoff to signing the next offer.

**Working name:** `comeback` (easy to rename).
**Language (user-facing):** Bulgarian.
**Audience:** any laid-off professional (junior to senior, any industry).
**Sibling project:** the [uncoachable.work](../uncoachable.work) blog. The guide that grounds this agent is also published there as a post.

## Why this exists

The market is full of single-purpose tools: CV builders, auto-appliers, interview drills. People end up stacking two or three of them because none covers the whole journey — and every one of them optimizes a *document* or a *performance* while ignoring the *person*. There is almost nothing good in Bulgarian, and nothing that holds the person steadily across the entire process.

`comeback` does the opposite: one conversation, in Bulgarian, that covers CV, job-search strategy, and interview practice — with a steadying, human layer running underneath all of it.

## Capabilities

1. **CV / resume building** — draft, tailor to a specific role, sanity-check for ATS, reframe the layoff.
2. **Interview practice** — mock interviews with feedback, the "why did you leave?" story, delivery.
3. **Job-search strategy** — networking-first plan, application tracking, outreach templates.
4. **Emotional support / mindset** — the layer competitors skip; steadies the person and keeps momentum.

## Structure

```
comeback/
├── README.md                 ← this file
├── CLAUDE.md                 ← instructions for agents working on this project
├── agent/
│   ├── system-prompt.md      ← the agent's core system prompt (Bulgarian-facing)
│   ├── modes/                ← per-capability playbooks the agent switches between
│   │   ├── triage.md
│   │   ├── cv.md
│   │   ├── interview.md
│   │   ├── search.md
│   │   └── support.md
│   └── templates/            ← reusable CV / outreach / tracking templates
└── knowledge-base/
    ├── guide.md              ← the Bulgarian guide (shared with the blog)
    ├── bg-legal.md           ← BG-specific legal & benefits facts (НОИ, Бюро по труда)
    └── sources.md            ← research sources behind the guide
```

## Status

Scaffolding + knowledge base in progress. See `CLAUDE.md` for conventions and next steps.
