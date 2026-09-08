# comeback

An interactive assistant that supports a laid-off professional through the **whole** arc of finding their next job — from the shock of the layoff to signing the next offer. One conversation, in **Bulgarian**, that covers benefits, CV, job-search strategy, and interviews — with a steadying, human layer running underneath all of it.

- **Language (what you see):** Bulgarian
- **Who it's for:** any laid-off professional — junior to senior, any industry
- **Where it runs:** [Claude Code](https://claude.com/claude-code) (desktop app, CLI, or IDE) — it's an agent you talk to, not a website
- **Sibling project:** the [uncoachable.work](https://uncoachable.work) blog; the guide that grounds this agent is also published there

## Why this exists

The market is full of single-purpose tools: CV builders, auto-appliers, interview drills. People stack two or three of them because none covers the whole journey — and every one optimizes a *document* or a *performance* while ignoring the *person*. There is almost nothing good in Bulgarian, and nothing that holds someone steadily across the entire process.

`comeback` does the opposite: **one assistant for the entire comeback**, in your language, that also handles the thing Bulgarian tools ignore — the money-and-deadlines side of losing a job — and never loses sight of the human going through it.

## What it does

It's not a CV tool with extras. It covers six things, and it decides which one you need by talking to you:

- **📋 Benefits & the legal clock** *(Bulgaria-specific)* — Are you owed unemployment benefit, how much, and by when must you act? It works out your **actual** Бюро по труда deadline (7 working days) and НОИ deadline (3 months) from your termination date, estimates your benefit, and orients you on severance and the electronic trudova kniga at НАП. The dates and amounts are computed deterministically and **verified against official НОИ/НАП sources** — never guessed.
- **📄 CV / resume** — Build one from scratch or clean up what you have, tailor it to a specific posting, sanity-check it for ATS, and reframe the layoff honestly. You get a finished `.docx` **and** a `.pdf`.
- **🎯 Job-search strategy** — A networking-first plan, a living application **tracker** the assistant maintains for you, and outreach drafts — so you're not just firing CVs into the void.
- **🗣️ Interview practice** — Mock interviews with real feedback, the "why did you leave?" story worked out until it lands, and delivery.
- **🔎 Company research** *(optional)* — For a specific posting: an honest fit read, concrete "why here" angles, and sharp questions to ask.
- **🫂 Emotional footing** — An always-on steadying layer underneath everything. You never have to ask for it; it's the part competitors skip.

> **A note on trust:** anything the assistant tells you about benefits, deadlines, or documents is checked by a **separate verifier** against the official source before you see it. If something can't be confirmed, it says so and points you to НОИ/Бюро по труда rather than handing you a confident wrong number.

## How to use it

### Before you start
1. Open this project in **Claude Code** and make **this folder** the working directory — that's what puts the subagents and the CV skill in scope. (On a plain Claude.ai project without them, only the conversation works — no file output.)
2. *Optional:* install **LibreOffice** if you want CV **PDFs** rendered locally with correct Cyrillic. Without it you still get the `.docx`.

### Start a session
Type **`/comeback`** — or just say what happened, in Bulgarian or English:

> „Съкратиха ме." · „Останах без работа." · „laid off"

It opens with a short, human check-in — what happened and where you are — and then routes to whatever you need. **You don't pick a mode or memorize commands; you just talk to it.**

### What you can ask for
You steer it in plain language. A few examples of what to say and what happens:

| Say something like… | …and it |
|---|---|
| „Съкратиха ме вчера, откъде да започна?" | Steadies you, then lays out the first days — with your benefit deadlines if the clock is ticking |
| „Полагат ли ми се пари и до кога да се регистрирам?" | Works out eligibility, your **exact** Бюро/НОИ deadlines and a benefit estimate — verified against official sources |
| „Помогни ми да стегна CV-то за тази обява" *(paste the job ad)* | Produces a tailored, ATS-clean CV as `.docx` + `.pdf` |
| „Имам интервю в петък, дай да порепетираме" | Runs a mock interview with feedback and helps you tell the layoff story |
| „Не знам как да си търся работа" | Builds a networking-first plan, a tracker, and outreach drafts |
| „Разкажи ми за тази компания преди интервюто" *(paste the posting)* | Fit read, „защо точно тук" angles, and questions to ask |
| *(feeling low / overwhelmed)* | The steadying layer is always on — you don't have to ask |

**CV only?** If all you want is a tailored CV, you can invoke **`/tailor-cv`** directly.

### What you get, and where
Everything produced **for you** lives in a private, **git-ignored** `Personal/<date>-you/` folder — so nothing about your situation is ever committed to the repo:
- a **dossier** — the assistant's running memory of your situation (so it never re-asks)
- your tailored **CV** (`.docx` + `.pdf`)
- a job-search **tracker**
- **interview** notes

## How it works

One **orchestrator** is the single voice you talk to. It holds the relationship — the check-in, the steadying layer, and one consistent tone — and never hands that off. For concrete work it quietly delegates to specialized **subagents** (CV, interview, search, benefits, company research), each of which reads and writes your shared **dossier**. A separate **freshness-checker** independently verifies every benefits/legal claim before it reaches you. You never see the machinery — just one assistant.

```
agent/            orchestrator (the voice), triage, always-on support, dossier schema
.claude/agents/   the subagents: cv-builder, interview-coach, search-strategist,
                  bg-navigator, company-intel, and the freshness-checker verifier
.claude/skills/   /comeback (the front door) and /tailor-cv (the CV engine)
knowledge-base/   the Bulgarian guide + BG legal/benefits facts + sources
```

Full architecture and conventions are in [CLAUDE.md](CLAUDE.md).

## Status

Shipped and stable (see `VERSION`). The full orchestrator → subagent → verification flow works end-to-end and is backed by an automated test suite (`tests/`), enforced before every push by a local test gate (see [CONTRIBUTING.md](CONTRIBUTING.md)). History is in [CHANGELOG.md](CHANGELOG.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), and [CLAUDE.md](CLAUDE.md) for the full conventions.

## License

Dual-licensed. The code and everything outside `knowledge-base/` is under the [MIT License](LICENSE). The written content in `knowledge-base/` — the guide, `bg-legal`, and `sources` — is under [Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0)](knowledge-base/LICENSE): share and adapt with attribution, non-commercial only.
