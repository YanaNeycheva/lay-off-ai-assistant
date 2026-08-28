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
├── .claude/
│   ├── agents/               ← the subagents the orchestrator calls
│   │   ├── cv-builder.md      ← drives the /tailor-cv skill
│   │   ├── interview-coach.md
│   │   ├── search-strategist.md
│   │   ├── bg-navigator.md    ← BG legal/benefits clock
│   │   └── company-intel.md   ← optional
│   └── skills/
│       ├── comeback/         ← ENTRY POINT: /comeback launches the orchestrator
│       │   └── SKILL.md
│       └── tailor-cv/        ← vendored CV skill (ATS audit → tailored .docx/.pdf)
│           ├── SKILL.md
│           └── ats-rules.md
├── agent/
│   ├── orchestrator.md       ← the single voice; holds the relationship + routing
│   ├── triage.md             ← orchestrator-owned (never delegated)
│   ├── support.md            ← orchestrator-owned, always-on layer
│   ├── dossier-template.md   ← shared case-file schema (state across subagents)
│   └── templates/            ← reusable CV / outreach templates
└── knowledge-base/
    ├── guide.md              ← the Bulgarian guide (shared with the blog)
    ├── bg-legal.md           ← BG-specific legal & benefits facts (НОИ, Бюро по труда)
    └── sources.md            ← research sources behind the guide
```

## How to launch

Open this folder in Claude Code and type **`/comeback`** (or just say "съкратиха ме" / "laid off"). The assistant becomes the orchestrator, creates a private case file under `Personal/` (git-ignored), and opens with triage. Run it from *this* directory so the subagents and the `/tailor-cv` skill are in scope.

## Status

Orchestrator + subagents + entry skill in place; knowledge base drafted. Next: end-to-end testing. See `CLAUDE.md` for conventions and next steps.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) (and [CLAUDE.md](CLAUDE.md) for the full conventions).

## License

This project is dual-licensed. The code and everything outside `knowledge-base/` is released under the [MIT License](LICENSE). The written content in `knowledge-base/` — the guide, `bg-legal`, and `sources` — is released under [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](knowledge-base/LICENSE): you are free to share and adapt it with attribution, for non-commercial purposes only.
