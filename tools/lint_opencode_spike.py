"""Minimal structural lint for the Phase-2 OpenCode spike (stdlib only).

Scoped deliberately to `.opencode/agents/` — this is the spike's Layer-2 check, not the
general multi-tool linter (that is a Phase-4 deliverable). It asserts the hand-ported
tree is structurally coherent without running OpenCode:

  * each agent file has a `---` frontmatter block
  * required frontmatter fields are present (`description`, `mode`)
  * a `permission:` block is present
  * `mode: primary` agents can spawn (`task: allow`)
  * every `@name` spawn reference resolves to an agent file that exists

Usage:  python tools/lint_opencode_spike.py
Exit 0 = all checks pass, 1 = at least one failed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[1] / ".opencode" / "agents"
SPAWN_RE = re.compile(r"@([a-z][a-z0-9-]+)")


def parse_frontmatter(text: str):
    """Return (frontmatter_lines, ok). Frontmatter is between the first two '---'."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], False
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], True
    return [], False


def top_level_keys(fm_lines: list[str]) -> set[str]:
    keys = set()
    for ln in fm_lines:
        if ln and not ln[0].isspace():
            m = re.match(r"([A-Za-z_][\w-]*)\s*:", ln)
            if m:
                keys.add(m.group(1))
    return keys


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if not AGENTS_DIR.is_dir():
        print(f"FAIL: no agents dir at {AGENTS_DIR}")
        return 1

    files = sorted(AGENTS_DIR.glob("*.md"))
    names = {f.stem for f in files}
    failures: list[str] = []

    if not files:
        print(f"FAIL: no agent files in {AGENTS_DIR}")
        return 1

    for f in files:
        text = f.read_text(encoding="utf-8")
        fm, ok = parse_frontmatter(text)
        if not ok:
            failures.append(f"{f.name}: missing/unclosed frontmatter block")
            continue
        keys = top_level_keys(fm)
        for req in ("description", "mode"):
            if req not in keys:
                failures.append(f"{f.name}: missing required field '{req}'")
        if "permission" not in keys:
            failures.append(f"{f.name}: missing 'permission' block")

        fm_text = "\n".join(fm)
        is_primary = re.search(r"^mode:\s*primary\b", fm_text, re.M) is not None
        if is_primary and not re.search(r"^\s*task:\s*allow\b", fm_text, re.M):
            failures.append(f"{f.name}: primary agent must have 'task: allow' to spawn subagents")

        # Spawn references live in the BODY, not the frontmatter description.
        body = text.split("---", 2)[-1]
        for ref in SPAWN_RE.findall(body):
            if ref not in names:
                failures.append(f"{f.name}: @{ref} references a missing agent")

    print(f"OpenCode spike lint — {AGENTS_DIR}")
    print(f"  agents: {', '.join(sorted(names))}")
    if failures:
        for msg in failures:
            print(f"  [FAIL] {msg}")
        print("\nRESULT: FAIL")
        return 1
    print(f"  {len(files)} files OK — frontmatter, permission, spawn refs all valid")
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
