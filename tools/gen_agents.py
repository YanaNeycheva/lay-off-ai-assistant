"""Generate other tools' agent trees from the .claude/ source of truth (stdlib only).

Decision (PORTING-PLAN.layoff.md §6.3): `.claude/` is the hand-authored source; every other
tool's tree is GENERATED from it. This is the Phase-3/4 generator. It currently emits the
**OpenCode** benefits-slice agents (`bg-navigator`, `freshness-checker`) from
`.claude/agents/*.md` + the OpenCode adapter below. The `comeback` primary/entry agent is a
separate entry recipe (from the skill + orchestrator) and stays hand-authored in `.opencode/`.

Extend by adding agents to SLICE and adapters to ADAPTERS (codex/copilot come later).

Usage:  python tools/gen_agents.py            # write generated files
        python tools/gen_agents.py --check    # exit 1 if any generated file is stale/missing

Run tools/lint_opencode_spike.py afterwards to validate the emitted tree.
"""

from __future__ import annotations

import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAUDE_AGENTS = ROOT / ".claude" / "agents"

# All subagents (.claude/agents/*.md). The `comeback` primary/entry is a per-tool recipe
# (Seam 4), hand-authored in .opencode/agents/comeback.md — not generated from a subagent body.
AGENTS = [
    "bg-navigator",
    "freshness-checker",
    "cv-builder",
    "interview-coach",
    "search-strategist",
    "company-intel",
]

# Per-agent model tier (Seam 5); model id is omitted -> inherits the tool default until §6.1 pins it.
TIERS = {"freshness-checker": "strong"}
DEFAULT_TIER = "mid"

# --- OpenCode adapter (the six seams, declaratively) -----------------------
OPENCODE = {
    "dir": ROOT / ".opencode" / "agents",
    # Seam 3: Claude tool name -> OpenCode permission key.
    "tool_to_perm": {
        "Read": "read",
        "Write": "edit",
        "Bash": "bash",
        "WebSearch": "websearch",
        "WebFetch": "webfetch",
    },
    "perm_order": ["read", "edit", "bash", "websearch", "webfetch"],
    # Seam 3: tool-name references in prose -> OpenCode-neutral wording.
    # (The Claude `Skill` tool has no OpenCode equivalent: /tailor-cv becomes a
    # read-and-follow of the skill file, which the agent already has `read` for.)
    "prose_subs": [
        (r"\bWebSearch\b", "web search"),
        (r"\bWebFetch\b", "web fetch"),
        (r"via Bash", "in a shell"),
        (r"`?/tailor-cv`? skill", "tailor-cv flow (read & follow `.claude/skills/tailor-cv/SKILL.md`)"),
    ],
}


def parse_claude_agent(md: str) -> tuple[dict, str]:
    """Split a .claude agent markdown into (frontmatter dict, body)."""
    lines = md.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("no frontmatter")
    i = 1
    fm: dict[str, str] = {}
    while i < len(lines) and lines[i].strip() != "---":
        if ":" in lines[i]:
            key, val = lines[i].split(":", 1)
            fm[key.strip()] = val.strip()
        i += 1
    body = "\n".join(lines[i + 1:]).lstrip("\n")
    return fm, body


def fold_description(desc: str) -> str:
    wrapped = textwrap.wrap(desc, width=94) or [desc]
    return "description: >-\n" + "\n".join("  " + line for line in wrapped)


def render_opencode(name: str, fm: dict, body: str) -> str:
    tools = [t.strip() for t in fm.get("tools", "").split(",") if t.strip()]
    allowed = {OPENCODE["tool_to_perm"][t] for t in tools if t in OPENCODE["tool_to_perm"]}

    perm_lines = [f"  {key}: allow" for key in OPENCODE["perm_order"] if key in allowed]
    perm_lines.append("  task: deny")  # slice subagents never spawn

    tier = TIERS.get(name, DEFAULT_TIER)

    desc = fm.get("description", name)
    for pattern, repl in OPENCODE["prose_subs"]:
        desc = re.sub(pattern, repl, desc)

    out = []
    out.append("---")
    out.append(fold_description(desc))
    out.append("mode: subagent")
    out.append(f"# tier: {tier}. model omitted -> inherits the tool default "
               "(Seam 5, PORTING-PLAN.layoff.md §6.1).")
    out.append("permission:")
    out.extend(perm_lines)
    out.append("---")
    out.append("")
    out.append(f"<!-- GENERATED from .claude/agents/{name}.md by tools/gen_agents.py "
               "(adapter: opencode).")
    out.append("     Do not edit here — edit the .claude source and regenerate. -->")
    out.append("")

    transformed = body
    for pattern, repl in OPENCODE["prose_subs"]:
        transformed = re.sub(pattern, repl, transformed)
    out.append(transformed.rstrip() + "\n")
    return "\n".join(out)


def generate() -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    for name in AGENTS:
        src = CLAUDE_AGENTS / f"{name}.md"
        fm, body = parse_claude_agent(src.read_text(encoding="utf-8"))
        outputs[OPENCODE["dir"] / f"{name}.md"] = render_opencode(name, fm, body)
    return outputs


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    argv = argv if argv is not None else sys.argv[1:]
    check = "--check" in argv
    outputs = generate()

    stale = []
    for path, content in outputs.items():
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current != content:
            stale.append(path)
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    rel = [str(p.relative_to(ROOT)) for p in outputs]
    if check:
        if stale:
            print("STALE (regenerate with `python tools/gen_agents.py`):")
            for p in stale:
                print(f"  {p.relative_to(ROOT)}")
            return 1
        print(f"up to date: {', '.join(rel)}")
        return 0
    print("generated:\n  " + "\n  ".join(rel))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
