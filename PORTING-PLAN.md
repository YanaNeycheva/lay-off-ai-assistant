# Making a Claude Code project tool-independent — generic porting plan

**Reusable, project-agnostic.** This plan describes how to take a project whose agents and
skills were authored for **Claude Code** and make the same machinery run on other agentic
CLIs — **OpenCode**, **OpenAI Codex CLI**, **GitHub Copilot CLI** — without maintaining N
hand-forked copies.

It is deliberately **not** specific to any one repo. To apply it to a concrete project,
create a companion file next to this one (e.g. `PORTING-PLAN.<project>.md`) that fills in the
blanks the phases below call out. See the Translation Agency companion (`PORTING-PLAN.translation-agency.md`)
for a worked example.

> Status of the target tools (verified 2026‑09): OpenCode, Codex CLI, and Copilot CLI **all**
> now support custom agents/subagents **and** per-agent model selection natively. So this is a
> *format/wiring* port, not a capability gap to work around.

---

## 0. Principles

1. **Keep the working tool working at every step.** The Claude Code path must stay green from
   commit to commit. Never break the thing that already works to build the thing that doesn't.
2. **Separate content from wiring.** The *intelligence* (system prompts, checklists, domain
   rules, config schemas) is portable prose. Only the *wiring* (frontmatter format, how one
   agent spawns another, tool names, model IDs, entry points) differs per tool. Isolate the
   wiring; share the content.
3. **One source of truth.** Never let the same instruction exist in two editable places. The
   per-tool trees should be **generated**, not hand-maintained — or, until a generator exists,
   there must be exactly one authored copy and the others are known-derived.
4. **Spike before you generalize.** Port one vertical slice to one tool by hand and run it for
   real *before* building any generator. The friction you discover reshapes the abstraction.
5. **Prove no regression with tests, not vibes.** Every phase ends with a deterministic check
   that the original path is unchanged and the new path is structurally valid.

---

## 1. The abstraction model

Split every agent/skill file into two layers:

- **Body (shared, tool-agnostic):** the system prompt, role, checklist, domain logic, output
  contract. This is the bulk of the file and should be **identical** across every tool.
- **Seams (per-tool):** the small set of things that must change per tool. There are only a
  handful. Enumerate them once and treat them as the entire porting surface:

| # | Seam | What varies | Where it lives |
|---|------|-------------|----------------|
| 1 | **Frontmatter / manifest** | YAML vs TOML; field names; required keys | top of each agent/skill file |
| 2 | **Spawn / delegation** | how a parent agent invokes a child subagent | inside agent bodies |
| 3 | **Tool names** | `Read`/`Edit`/`Grep`/`Bash`/… vs each tool's equivalents | anywhere the body names a tool |
| 4 | **Entry point** | slash-command / skill vs command vs plain prompt | how a human starts a run |
| 5 | **Model tiers** | tier label (strong/mid/cheap) → concrete provider model ID | frontmatter + any in-body model refs |
| 6 | **Task/todo primitives** | tool-provided task tracking vs prose checklist fallback | agent bodies that track work |

> If, during the inventory (Phase 0), you find coupling that does **not** fit one of these six
> seams, that is a finding — add a seam row rather than smuggling tool-specifics into a shared
> body.

---

## 2. Target-tool capability matrix (2026‑09)

Fill in / re-verify per project — model IDs drift fastest.

| | **Claude Code** (source) | **OpenCode** | **Codex CLI** | **Copilot CLI** |
|---|---|---|---|---|
| Agent file | `.claude/agents/*.md` (YAML fm) | `.opencode/agents/*.md` or `~/.config/opencode/agents/` (YAML fm) | `.codex/agents/*.toml` or `~/.codex/agents/` (**TOML**) | `*.agent.md` (YAML-ish fm) |
| Skill / command | `.claude/skills/<n>/SKILL.md` (`/name`) | command / primary agent | command / prompt | command / prompt |
| Spawn child | `Agent` tool | `@agent-name` or auto by description | "spawn `<name>`" by name in prompt | subagent delegation / `/fleet` |
| Per-agent model | `model:` frontmatter | `model:` frontmatter | `model` field | `model` field |
| Tool restriction | `tools:` list | `permission:` map (allow/ask/deny) | `sandbox_mode` (read-only/workspace-write) | `tools` spec |
| Frontmatter fields of note | `name, description, model, tools` | `description, mode, model, temperature, permission` | `name, description, developer_instructions, model, sandbox_mode` | `name, description, model, tools` |

Closeness to the Claude Code source (easiest → hardest to port): **OpenCode → Copilot → Codex**
(Codex is the odd one out because of TOML + `developer_instructions`).

---

## 3. Phased plan

### Phase 0 — Inventory & coupling audit *(no changes yet)*
Goal: know exactly what must change.

- [ ] List every agent and skill file.
- [ ] For each file, grep for and tag each occurrence of the six seams (spawn calls, tool
      names, model refs, entry-point assumptions, task primitives, frontmatter).
- [ ] Confirm the **non-agent** assets (config schemas, JSON, domain reference files, test
      fixtures) are already tool-agnostic — they usually are; note any that aren't.
- [ ] Produce a **coupling inventory** table: `file → seam# → line/snippet`. This is the spec
      for everything after.

**Exit test:** the inventory accounts for 100% of tool-specific references (re-run the greps;
every hit is either tagged to a seam or fixed). Nothing else in the repo references the tool.

### Phase 1 — Establish the source of truth *(structure only, behavior identical)*
Goal: one authored copy, cleanly split into body + seams — **without changing Claude Code
behavior**.

- [ ] Decide the layout. Recommended: keep authored bodies in a neutral `src/agents/` and
      `src/skills/` (tool-agnostic), and treat `.claude/` as a **generated** target like every
      other tool. If that's too big a leap initially, keep `.claude/` as the authored source and
      generate the others from it.
- [ ] Factor each seam into a named, substitutable token or a small per-tool table (e.g. a
      `tiers.json` mapping `strong|mid|cheap` → model ID per provider; a spawn-phrasing snippet
      per tool; a tool-name map per tool).
- [ ] Do **not** yet emit other tools.

**Exit test (critical — the "did we break anything" gate):** the Claude Code tree after
refactor is **byte-identical** (or diff-reviewed and intentional) to before. Capture a golden
snapshot at the start of this phase and diff against it. See §4.

### Phase 2 — Pilot spike *(one tool, one slice, run it for real)*
Goal: prove the whole approach end-to-end before investing in a generator.

- [ ] Pick the **closest** target first (usually OpenCode).
- [ ] Hand-port the **smallest vertical slice** that exercises spawning (a primary/entry + one
      or two subagents), not the whole surface.
- [ ] Run it against a **known fixture** with a known-correct outcome and confirm it behaves.
- [ ] Write down every friction point — these become adapter requirements.

**Exit test:** the pilot slice produces the expected result on the fixture (§4, behavioral
eval), and the Claude Code slice still produces its expected result unchanged.

### Phase 3 — Extract the adapter layer
Goal: turn the hand-port's tool-specifics into a reusable, declarative adapter.

- [ ] Create one **adapter descriptor per tool** capturing only the six seams: frontmatter
      template, tier→model map, spawn phrasing, tool-name map, entry-point recipe, task-primitive
      fallback.
- [ ] Re-derive the pilot slice from `body + adapter` and confirm it matches the hand-port.

**Exit test:** generated pilot slice == hand-ported pilot slice (diff is empty).

### Phase 4 — Generator / build step
Goal: emit every tool tree from `bodies + adapters` with one command.

- [ ] Write a small, dependency-light generator: for each tool, for each body, apply the
      adapter and write to that tool's path (`.opencode/`, `.codex/`, `.github/…`).
- [ ] Wire it to a script (e.g. `npm run build:agents`) and make emitted trees git-tracked
      **or** git-ignored+generated-on-demand (pick one and document it).

**Exit test:** running the generator produces trees that pass the per-tool structural lints
(§4) and re-generating is idempotent (no diff on second run).

### Phase 5 — Port the remaining surface
- [ ] Port the rest of the skills/agents beyond the pilot slice.
- [ ] Handle entry points: for tools without "skills," provide a command or a documented
      "run this agent with this prompt" recipe.

**Exit test:** behavioral eval passes for the full surface on the pilot tool; structural lints
pass for all files.

### Phase 6 — Remaining tools
- [ ] Add the other tools' adapters (Copilot, then Codex/TOML last).
- [ ] Run the full test matrix per tool.

**Exit test:** matrix green for every tool.

### Phase 7 — Docs, packaging, release
- [ ] Document per-tool install/run in the README.
- [ ] If the tool ecosystems have package formats (e.g. Claude `.skill` bundles), build those
      from the generated trees.
- [ ] Version bump + changelog per the project's release convention.

---

## 4. Testing strategy — "prove we didn't break anything"

Five layers, cheapest first. Layers 1–3 are deterministic and belong in CI/`npm test`; layer 4
is deterministic-assertion-over-manual-run; layer 5 costs tokens and is a pre-release runbook.

### Layer 1 — Golden regression snapshot (guards the original tool)
The single most important check for "did we break anything."
- **Before touching anything** (start of Phase 1), snapshot the authored Claude Code tree:
  `git stash`-clean state, or copy `.claude/` to `baseline/.claude/`, or just rely on
  `git diff`.
- After each refactor phase, assert the **Claude Code output is unchanged**: `git diff --stat`
  on `.claude/` should be empty (Phase 1) or only intentional, reviewed lines.
- Automate: a `test:no-regression` script that diffs the emitted `.claude/` tree against the
  committed baseline and fails on any unexpected delta.

### Layer 2 — Structural / format lint per tool
For each emitted tool tree, assert it's well-formed **in that tool's schema**:
- Frontmatter parses (YAML for OpenCode/Copilot/Claude; **TOML** for Codex).
- All **required fields** present (`name`/`description`/`model`/etc. per that tool).
- Every **model ID resolves** to a real tier→model mapping (no `undefined`, no stale IDs).
- Every **tool name** used in a body maps to a name that tool actually provides.
- Every **spawn reference** names an agent that exists in that tree.
- Entry points exist (command/skill file present where the tool expects it).

Keep this pure and offline (no network, no tokens). This is the bulk of the automated safety.

### Layer 3 — Equivalence / drift test (guards "one source of truth")
- Assert the **shared body** is identical across all emitted trees (strip frontmatter + seam
  substitutions, then diff). If OpenCode's body and Codex's body diverge in anything but the
  seams, that's a bug — content drifted.
- Assert the generator is **idempotent**: run twice, second run yields no diff.

### Layer 4 — Behavioral eval with deterministic assertions
This is how you prove the *ported agents still do their job*, not just that files parse.
- Keep (or create) a **fixture with a known-correct outcome** and an **answer key** — e.g. an
  input with planted defects the agents must catch, plus a machine-checkable assertion script
  that encodes the pass/fail post-conditions.
- The **assertion script** is deterministic (no LLM) and runs in `npm test` against a
  known-good and known-bad output, proving the assertion itself bites — no tokens spent.
- The **actual agent run** through each tool is the token-costing part: run the ported panel
  on the fixture, then run the same assertion script on its output. Because the assertion is
  shared, "OpenCode passed" and "Claude passed" mean the *same* thing.

### Layer 5 — Cross-tool behavioral parity (pre-release, manual)
- Run the same fixture through **every** tool and confirm all pass the same assertions.
- Optionally diff the *content* of outputs across tools for gross divergence (they need not be
  identical, but shouldn't disagree on the answer key).

### CI matrix
```
for tool in claude opencode codex copilot:
    lint(tool)         # Layer 2
equivalence()          # Layer 3
no_regression(claude)  # Layer 1
eval_assert_selftest() # Layer 4 deterministic half (good+bad fixtures)
```
The token-costing agent runs (Layer 4 live, Layer 5) stay **out** of per-commit CI and live in
a documented pre-release runbook.

---

## 5. Rollback & incremental safety

- Work on a branch; each phase is its own commit with its exit-test green.
- The Claude Code tree is the safety net: if a phase goes wrong, the original path still runs.
- Never delete `.claude/` until the generator reproduces it and Layer 1 is green.
- Prefer generated-and-git-ignored per-tool trees once the generator is trusted, so there's
  only ever one authored copy to review.

## 6. Definition of done

- [ ] One authored source of truth; all tool trees generated from it.
- [ ] Layers 1–4 automated and green in CI; Layer 5 runbook documented.
- [ ] Each target tool has a documented install + run path.
- [ ] Original Claude Code behavior provably unchanged (Layer 1).
- [ ] README/docs updated; version bumped per project convention.

---

### Applying this to a specific project
Create `PORTING-PLAN.<project>.md` that extends this file with: the concrete file inventory,
the filled-in six-seam table, the tier→model map for that project's providers, the specific
fixture/assertion used for Layer 4, and any project-specific release/hygiene rules. This generic
plan stays untouched and reusable across projects (it is the copy used for the LayOff project).
