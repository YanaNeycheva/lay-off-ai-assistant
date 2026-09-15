# Porting plan — LayOff / `comeback` (companion to `PORTING-PLAN.md`)

**This file extends the generic [`PORTING-PLAN.md`](PORTING-PLAN.md).** The generic plan owns the
method — the six-seam abstraction, the phased approach, and the five-layer testing strategy. This
companion fills in the blanks for **this** repo: the concrete inventory, the filled-in seam tables
(with line references), the tier→model map, the Layer-4 fixture, and LayOff-specific invariants that
the port must not break. Read the generic plan first; this only records what is specific here.

**Targets (from the generic plan):** OpenCode, OpenAI Codex CLI, GitHub Copilot CLI. All three
support custom subagents and per-agent models natively — so for this project too it is a
**format/wiring port, not a capability gap** (one real exception: live web search — see Seam 3).

> **Correction to an earlier draft of this file:** a first pass proposed collapsing the subagents
> into inline single-agent "roles." That is **wrong for this project** and is rejected here: the
> targets all support real subagents, and the `freshness-checker` gate is only sound when it runs
> as a *separate* agent from its producer (see Invariant 2). Keep true subagents.

> **▶ Current milestone.** Phases 2, 3 and 5 **COMPLETE for OpenCode.** Phase 2: the benefits slice
> ran end-to-end in OpenCode Desktop (live). Phase 3: `tools/gen_agents.py` derives the OpenCode
> agents from `.claude/` + adapter (the resolved §6.3 model). Phase 5: the **full** OpenCode surface
> — all 6 subagents generated + the hand-authored `comeback` entry — passes `lint_opencode_spike.py`,
> is idempotent (`--check`), tests stay 50/50, and `.claude/` is byte-identical to v1.4.0.
> **Next milestone: Phase 6** — add the Codex (TOML) and Copilot adapters to `gen_agents.py`; and
> **§6.1** — pin the tier→`provider/model-id` map. Point `/goal` there, not at §7's full DoD.

---

## 0. Inventory & coupling audit (generic Phase 0)

### File inventory

**Subagent bodies** — `.claude/agents/*.md` (6): `cv-builder`, `interview-coach`,
`search-strategist`, `bg-navigator`, `company-intel`, `freshness-checker`.

**Skills** — `.claude/skills/`: `comeback/SKILL.md` (entry point + orchestrator bootstrap),
`tailor-cv/SKILL.md` (+ skill-local `ats-rules.md`, `proofing.md`).

**Orchestrator + shared prose** (loaded by the entry skill, *not* Claude-specific mechanism) —
`agent/orchestrator.md`, `agent/triage.md`, `agent/support.md`, `agent/dossier-template.md`,
`agent/templates/{cv-structure,outreach,tracker}.md`. These are the top-level persona and its
shared state schema; they carry seam references (spawn phrasing, tool names) but no frontmatter.

**Already tool-agnostic (no port work):** `knowledge-base/*`, `lib/benefits.py` (stdlib-only
calculator), `tests/*`, `scripts/*` (see Seam 7), `VERSION`, `CHANGELOG.md`, `CONTRIBUTING.md`,
`.githooks/pre-push`.

### Coupling inventory (file → seam# → snippet)

| File | Seam | Evidence |
|---|---|---|
| `.claude/agents/*.md` (all 6) | 1, 3, 5 | YAML frontmatter `name`/`description`/`tools:`; **no `model:`** set (all inherit the session model) |
| `.claude/agents/cv-builder.md:4` | 3 | `tools: Read, Write, WebFetch, Skill, Bash` |
| `.claude/agents/bg-navigator.md:4` | 3 | `tools: Read, WebSearch, Write, Bash` |
| `.claude/agents/company-intel.md:4` | 3 | `tools: Read, WebSearch, WebFetch, Write` |
| `.claude/agents/freshness-checker.md:4` | 3 | `tools: Read, WebSearch, Write` |
| `.claude/agents/{search-strategist,interview-coach}.md:4` | 3 | `tools: Read, Write` |
| `bg-navigator.md` body | 2, 3 | "verify with **WebSearch**", "call the helper **via Bash**" (`python -m lib.benefits`) |
| `tailor-cv/SKILL.md:23` | 3 | "fetch it (**WebFetch**)" |
| `cv-builder.md` | 2, 3 | wraps the `/tailor-cv` skill via the **Skill** tool |
| `comeback/SKILL.md` | 2, 4 | `/comeback` slash + auto-trigger; bootstraps orchestrator + dossier; delegates to subagents |
| `orchestrator.md` (Delegation protocol, Subagents table, Freshness gate) | 2 | "spawn the subagent", "spawn **`freshness-checker`**" |
| `tailor-cv/SKILL.md`, `comeback/SKILL.md` | 4 | skill entry points (`/tailor-cv`, `/comeback`) |
| all subagents + orchestrator | 6 | task tracking is the **dossier.md** + prose checklists — **no harness TODO primitive** (low-risk seam here) |
| `cv-builder.md`, `tailor-cv/SKILL.md`, `orchestrator.md`, `templates/tracker.md` | **7 (new)** | harness `docx`/`pdf`/`xlsx` skills — see Seam 7 |

**Phase 0 exit test:** the greps behind this table (`\b(Read|Write|WebSearch|WebFetch|Bash|Skill|Agent)\b`
over `.claude/`, plus `^tools:`/`^model:` over `.claude/agents/`) account for every tool-specific
reference. Re-run them after any body edit; each hit must map to a seam row above.

---

## 1. The six seams, filled in for LayOff

**Seam 1 — Frontmatter.** 6 subagents + 2 skills. Fields in use: `name`, `description`, `tools`
(no `model`, no `temperature`). Port = re-emit as each target's manifest (YAML for OpenCode/Copilot,
**TOML** for Codex).

**Seam 2 — Spawn/delegation.** The orchestrator (top-level, from `agent/orchestrator.md`) spawns
bounded subagents and, critically, spawns `freshness-checker` **on** `bg-navigator`'s output.
Per-tool phrasing: OpenCode `@agent-name`; Codex "spawn `<name>`" by name; Copilot subagent
delegation. **Invariant 2 constrains this seam** — the freshness check must be a distinct agent.

**Seam 3 — Tool names + a real capability risk.** Map per target at build time (names drift):

| Logical need | Claude Code | Used by | Port note |
|---|---|---|---|
| read/write files | `Read`, `Write` | all 6 | 1:1 on every target |
| run Python | `Bash` (`python -m lib.benefits`) | bg-navigator, cv-builder | needs shell/exec; all 3 CLIs have it |
| fetch a URL | `WebFetch` | cv-builder, company-intel, tailor-cv | maps to each tool's fetch |
| **live web search** | `WebSearch` | **bg-navigator, company-intel, freshness-checker** | ⚠️ **not built into every target CLI** — may need an MCP/plug-in per tool. This is the one seam-3 item that is a genuine capability check, not a rename. |
| invoke CV engine | `Skill` (`/tailor-cv`) | cv-builder | becomes a spawn/command per Seam 4 |

⚠️ **Finding:** three subagents depend on `WebSearch`. `freshness-checker`'s whole job is live
verification against nssi.bg / az.government.bg / nap.bg, so a target without web search **cannot
run the safety gate**. Confirm web-search availability per tool in the Phase 2 spike before
committing to that tool.

**Seam 4 — Entry point.** `/comeback` (slash + natural-phrase auto-trigger) bootstraps the
orchestrator persona + a per-person `Personal/<date>-<slug>/dossier.md`, then opens with triage.
`/tailor-cv` is a secondary entry. On tools without skills: provide a command or a documented
"load `agent/orchestrator.md` + `agent/triage.md` + `agent/support.md` as the system prompt, then
bootstrap the dossier" recipe. Auto-trigger on Bulgarian phrases likely won't port — an explicit
start command is the fallback.

**Seam 5 — Model tiers.** The repo currently sets **no** models (everything inherits the session
model), so this is net-new and needs a decision. Proposed `tiers.json` for this project:

| Tier | Agents | Why |
|---|---|---|
| `strong` | orchestrator, `freshness-checker` | holds the relationship + judgement; correctness-critical verification |
| `mid` | `bg-navigator`, `cv-builder`, `interview-coach`, `search-strategist`, `company-intel` | bounded produce-an-artifact work |
| `cheap` | — | none; nothing here is pure boilerplate |

Map `strong|mid|cheap` → concrete provider model IDs per tool at build time (IDs drift fastest —
re-verify each build).

**Seam 6 — Task primitives.** Low-risk here: work is tracked in `dossier.md` (schema in
`agent/dossier-template.md`) and prose checklists (the tracker статус конвейер, the CV brief
checklist). No harness TODO tool is assumed, so nothing to substitute — the dossier is already the
tool-agnostic task substrate. Keep it.

**Seam 7 (new) — Harness-provided output skills.** *Not one of the generic six; added per the
generic plan's instruction to record coupling that doesn't fit.* The CV/tracker pipeline used the
Claude-bundled `docx` / `pdf` / `xlsx` skills. **Resolved (see §2 — already implemented):** shipped
`scripts/render_cv_docx.py`, `scripts/docx_to_pdf.py`, `scripts/tracker_to_xlsx.py`. Bodies now call
the scripts as the portable primary path and note the bundled skill as the in-Claude equivalent, so
this seam is uniform across every tool and needs no per-adapter work.

---

## 2. Status — what is already done

**Seam 7 is resolved (this branch, `tool-agnostic`).** Before the wiring port, the hardest
harness-content dependency was removed:

- `scripts/render_cv_docx.py` — CV JSON → ATS-clean `.docx` (`python-docx`); enforces the ATS
  structure from `.claude/skills/tailor-cv/ats-rules.md` deterministically. JSON contract in
  `scripts/README.md`.
- `scripts/docx_to_pdf.py` — `.docx` → `.pdf` via LibreOffice headless (auto-locates `soffice`,
  Windows full path included; verifies the PDF was written). Clean degradation when LibreOffice is
  absent.
- `scripts/tracker_to_xlsx.py` — `tracker.md` → `.xlsx` snapshot (`openpyxl`).
- `requirements.txt` (python-docx, openpyxl); `tests/test_scripts.py` (guarded with `skipUnless`
  so the stdlib-only pre-push gate stays green when deps are absent).
- Bodies rewired: `cv-builder.md`, `tailor-cv/SKILL.md`, `orchestrator.md`, `templates/tracker.md`,
  `CONTRIBUTING.md`.
- Verified: full suite 50/50 green; a real Cyrillic CV renders (0 tables → ATS-clean, en-dashes,
  Cyrillic intact); tracker exports 5 sheets.

> These edits **touch `.claude/` bodies**, so the Layer-1 golden baseline is captured **as of the
> `v1.4.0` commit**, treating these as the intentional, reviewed Phase-1 changes the generic plan
> allows — not as a regression to diff away.

**Phase 1 is committed** on branch `tool-agnostic` as `v1.4.0` (VERSION + CHANGELOG bumped, annotated
tag). `git diff --stat v1.4.0 -- .claude/` is the Layer-1 no-regression check; it is currently empty.

**Phase 2 pilot spike (OpenCode) — COMPLETE, behaviorally validated.** Hand-ported the benefits
safety slice under `.opencode/agents/`: `comeback` (primary/entry, spawns the slice), `bg-navigator`,
`freshness-checker` — bodies neutralized, frontmatter in OpenCode's verified format
(`.opencode/agents/`, `permission` map, `provider/model-id`, spawn via Task tool / `@mention`).
`tools/lint_opencode_spike.py` (stdlib) validates them offline → `RESULT: PASS`.

**Live run (2026-09-15, OpenCode Desktop v1.18.31, model "Big Pickle" / OpenCode Zen).** Opened the
LayOff project, selected the `Comeback` agent (OpenCode discovered it), and fed the Martin persona's
Turn-1+2 (layoff + benefits question). Observed, in order: orchestrator read its 4 instruction files
→ `mkdir Personal/2026-09-15-anon/` → wrote `dossier.md` → **spawned `Bg-Navigator`** (which ran
`python -m lib.benefits` several times — 3200 BGN→1636 EUR conversion, `bureau-deadline`,
`noi-deadline`, `estimate` — then edited the dossier) → **spawned `Freshness-Checker`** (verified
against nssi.bg/nra.bg/lex.bg and stamped `bg-legal.md`'s Дневник table). The dossier's
`## Legal / benefits` came out fully populated with deterministic values (Bureau 25.08.2026, НОИ
14.11.2026, ~981.60 EUR/mo, 8 months) + a "За потвърждаване" freshness handoff.
`tools/check_benefits_slice.py Personal/2026-09-15-anon/` → **RESULT: PASS**.

**What the live run proves (all four seams + the invariants, on a real tool):**
- **Seam 2 (spawn) works** — `comeback` spawned two real subagents in the right order.
- **Seam 3 (tools) works** — `bash`/`python` ran the calculator; `websearch`/`webfetch` ran the
  verification. **OpenCode HAS native web search** (`websearch`, Exa/Parallel) — the Seam-3
  WebSearch risk is **resolved for OpenCode**; the freshness gate runs there.
- **Invariant 2 (producer ≠ checker) holds** — `freshness-checker` ran as a separate agent on
  `bg-navigator`'s output.
- **Invariant 3 (deterministic boundary) holds** — every date/amount traced to `lib.benefits`, not
  prose.
- **Model/auth:** no CLI auth needed — the Desktop app's OpenCode Zen model ("Big Pickle") ran the
  agents; `model:` omitted → inherited it. (Seam 5 tier→`provider/model-id` still to pin per §6.1.)
- **Entry (Seam 4):** the `/comeback` skill became a `mode: primary` agent selected in the UI;
  natural-phrase auto-trigger did not port (expected).

**Housekeeping from the run:** the freshness-checker's stamp of `bg-legal.md` (dates → 2026-09-15,
no value changes) was **reverted** — an automated test run must not leave an unverified
"last-checked today" claim on the source of truth. The `Personal/2026-09-15-anon/` run folder is
git-ignored (never committed). The remaining hand-neutralization duplication (`.claude` says
"WebSearch"/"via Bash"; the `.opencode` copies say "web search"/"`python -m lib.benefits`") is
expected for a spike — the Phase-4 generator emits both from one neutral body + per-tool seams.

**Everything else below is not yet started.**

---

## 3. Phased plan (this project's instance of the generic phases)

- **Phase 0 — Inventory.** ✅ done — §0/§1 above.
- **Phase 1 — Source of truth.** Capture the Layer-1 golden snapshot of `.claude/` **now**. Decide
  layout: keep `.claude/` as the authored source initially (subagents already live there); factor
  the seams into a per-tool adapter + `tiers.json` + a spawn-phrasing snippet + a tool-name map.
  Note the wrinkle that the orchestrator/triage/support are in `agent/` while subagents are in
  `.claude/agents/` — the "shared body" set spans both. No other tools emitted yet.
- **Phase 2 — Pilot spike (OpenCode, smallest slice).** Port the **benefits safety slice**:
  entry → `bg-navigator` → `freshness-checker`. Chosen deliberately — it is the smallest slice that
  exercises spawning **and** the project's load-bearing constraints (producer≠checker, the
  deterministic `lib/benefits.py` boundary, and the `WebSearch` dependency). Run it against the
  Martin fixture's benefits turn; confirm the gate actually fires and web search works on OpenCode.
- **Phase 3 — Adapter layer.** One descriptor per tool: frontmatter template, `tiers.json`,
  spawn phrasing, tool-name map, entry-point recipe. (Seam 7 already uniform.) Re-derive the pilot
  slice from `body + adapter`; diff against the hand-port.
- **Phase 4 — Generator.** Emit `.opencode/`, `.codex/` (TOML), Copilot trees from bodies+adapters.
- **Phase 5 — Full surface on OpenCode.** Remaining 5 subagents + `tailor-cv`; entry-point recipes.
- **Phase 6 — Copilot, then Codex (TOML/`developer_instructions`) last.**
- **Phase 7 — Docs + release** per §5 conventions.

---

## 4. Testing — this project's mapping to the five layers

- **Layer 1 (golden regression):** diff emitted `.claude/` against a baseline captured at the start
  of Phase 1 (i.e. this commit). Must be empty or intentional.
- **Layer 2 (structural lint):** per-tool frontmatter parses (YAML / TOML for Codex); required
  fields present; every tier→model ID resolves; every tool name maps to one that tool provides —
  **including a check that `WebSearch`-dependent agents have a web-search capability on that tool**;
  every spawn reference names an agent that exists. Runs offline. The existing stdlib suite
  (`tests/test_*.py`) and the **drift test** (`tests/test_benefits.py`, guarding
  `bg-legal.md` ↔ `lib/benefits.py`) are this project's ready-made Layer-2/3 half and stay green.
- **Layer 3 (equivalence/drift):** shared bodies identical across emitted trees (strip
  frontmatter + seam substitutions, then diff); generator idempotent.
- **Layer 4 (behavioral eval):** **already built** — `tests/e2e/fixture_martin.md` (canonical
  persona, 6 scripted turns) + `tests/e2e/check_artifacts.py` (deterministic: dossier sections, a
  tailored `.docx`+`.pdf` pair, Cyrillic integrity via `zipfile`, tracker zones/columns). This is
  the answer key. The deterministic half runs with no tokens; the live agent run per tool is the
  token-costing half.
- **Layer 5 (cross-tool parity):** drive `fixture_martin.md` through each tool, run
  `check_artifacts.py` on each produced `Personal/<date>-martin/` folder. Because the assertion is
  shared, "OpenCode passed" and "Claude passed" mean the same thing.
- **CI reality:** there is **no server CI** — the local `.githooks/pre-push` gate runs the
  deterministic suite (Layer 2/3 half) before every push. Layer 4/5 live runs stay in the on-demand
  e2e runbook (`tests/e2e/README.md`), exactly as today.

---

## 5. LayOff-specific invariants the port must not break

1. **`Personal/` is never committed.** Every tool's run folder + dossier + CV/tracker output stays
   git-ignored and local.
2. **Producer ≠ checker (the freshness gate).** `freshness-checker` must run as a **separate agent**
   from `bg-navigator`, on its output, before anything reaches the person. No single-agent collapse.
   A target without live web search cannot host this gate (Seam 3).
3. **Deterministic calculator boundary.** All date/duration/money values come only from
   `lib/benefits.py`, never LLM prose, on every tool. The drift test keeps
   `lib/benefits.py` ↔ `knowledge-base/bg-legal.md` in sync.
4. **Language rule.** Bulgarian for everything the person sees; English for code/config/docs. The
   port is wiring only — it must not touch user-facing Bulgarian wording.
5. **The relationship model.** The orchestrator holds the human thread (triage + support, never
   delegated); subagents are bounded tools. True on every tool.
6. **Release hygiene.** `VERSION` bump + annotated `vX.Y.Z` tag + `CHANGELOG.md` entry per change;
   the stdlib-only pre-push gate must stay green.

---

## 6. Open decisions for the user

1. **Tier→model map (Seam 5) — RESOLVED (2026-09-15):** models live in `tiers.json` (single source;
   the generator emits each agent's `model:` from it). OpenCode is assigned its **free** OpenCode Zen
   models, read live from the app's model selector: `strong` → `opencode/nemotron-3-ultra-free`
   (orchestrator + freshness-checker), `mid` → `opencode/big-pickle` (proven end-to-end in the live
   run), `cheap` → `opencode/nemotron-3.5-lightning-free`. When a real provider is authed in OpenCode,
   swap the IDs in `tiers.json` and regenerate — no agent files touched. **On "make it dynamic":** the
   assignment IS driven by the user's available models (read from the tool), and `tiers.json` +
   regenerate is the refresh path; a fully-automatic query isn't practical for the GUI-only Desktop
   app (no headless model-list API), so the config-file-of-record is the pragmatic equivalent.
2. **First target confirmation:** generic plan orders OpenCode → Copilot → Codex. Proceed OpenCode-
   first for the Phase 2 spike?
3. **Authored-source layout (Phase 1) — RESOLVED (2026-09-15): keep `.claude/` as the hand-authored
   source of truth; generate every other tool's tree from it** (no neutral `src/`, and Claude is
   never generated). Rationale: the primary contributor develops this project in Claude Code, so the
   `.claude/` tree must stay the directly-edited, first-class artifact. The generator
   (`tools/gen_agents.py`) reads `.claude/agents/*.md` + body and applies a per-tool adapter
   (frontmatter transform + tool-name prose substitutions + spawn phrasing) to emit `.opencode/`
   etc. Generated files carry a "do not edit — regenerate" header.
4. **`WebSearch` gap:** if a chosen target lacks native web search, are we willing to wire an MCP/
   plug-in for it, or does that drop the target for the benefits/freshness slice?

None of these block the Phase 1 golden-snapshot step, which is pure setup.

---

## 7. Definition of done — how to verify the final result

The port is **done** when every box below is checked. Each maps to a runnable command, so this
section doubles as the finish line for a `/goal` condition (point it at "the Definition of Done in
`PORTING-PLAN.layoff.md` §7 passes"). Commands run from the repo root.

### Runnable today (deterministic, no tokens)

```bash
# Layer 2/3 — static invariants + the bg-legal.md <-> lib/benefits.py drift test
python -m unittest discover -s tests            # expect: OK (all green)

# Seam 7 — the harness-independent output scripts actually produce artifacts
python scripts/render_cv_docx.py <cv.json> --out out.docx   # expect: "Wrote out.docx", 0 tables, Cyrillic intact
python scripts/tracker_to_xlsx.py agent/templates/tracker.md --out out.xlsx  # expect: sheets written
```

### Lights up as phases land

```bash
# Layer 1 (golden regression) — .claude/ unchanged vs the Phase-1 baseline
git diff --stat <phase1-baseline> -- .claude/    # expect: empty, or only reviewed/intentional lines

# Layer 2 (structural lint, Phase 4 deliverable) — per emitted tool tree
python tools/lint_agents.py claude opencode copilot codex
#   asserts: frontmatter parses (YAML / TOML for codex); required fields present;
#   every tier->model ID resolves; every tool name maps to one that tool provides
#   (incl. a web-search capability for WebSearch-dependent agents); every spawn
#   reference names an agent that exists; entry point present.

# Layer 3 (equivalence + idempotence)
python tools/check_equivalence.py               # shared bodies identical across trees (seams stripped)
python tools/build_agents.py && git diff --exit-code   # generator is idempotent (no diff on re-run)

# Layer 4 / 5 (behavioral parity) — drive fixture_martin.md through EACH tool, then:
python tests/e2e/check_artifacts.py Personal/<date>-martin/   # expect: RESULT: PASS
#   (run once per target: claude, opencode, copilot, codex — same assertion, same meaning)
```

### Acceptance checklist (definition of done)

- [ ] `python -m unittest discover -s tests` → OK (Layer 2/3 half incl. the drift test).
- [ ] One authored source of truth; every tool tree (`.claude/`, `.opencode/`, `.codex/`, Copilot)
      is **generated** from `bodies + adapters`, and the generator is idempotent.
- [ ] Structural lint (Layer 2) green for **all four** tools — including the WebSearch-capability
      check for `bg-navigator` / `company-intel` / `freshness-checker`.
- [ ] Shared bodies identical across trees (Layer 3 equivalence).
- [ ] `check_artifacts.py` → `RESULT: PASS` for a `fixture_martin.md` run on **every** target tool
      (Layer 5 parity).
- [ ] Layer 1 golden: `.claude/` unchanged vs the Phase-1 baseline (or diff reviewed + intentional).
- [ ] The five invariants in §5 hold on every tool — spot-check the freshness gate fires
      (producer ≠ checker) and no benefit figure appears that didn't come from `lib/benefits.py`.
- [ ] Each target has a documented install + run recipe in the README.
- [ ] `VERSION` bumped, `CHANGELOG.md` entry added, annotated `vX.Y.Z` tag created.

> `tools/lint_agents.py`, `tools/check_equivalence.py`, `tools/build_agents.py` above are **named
> here as the contract**, not yet written — they are the Phase 3–4 deliverables. Until they exist,
> the checkable finish line is the "Runnable today" block plus a hand-run `check_artifacts.py`.
