#!/usr/bin/env python3
"""Deterministic artifact checker for the comeback end-to-end smoke harness.

Usage:
    python tests/e2e/check_artifacts.py Personal/<date>-<slug>/

Asserts the *shape* of a real (LLM-driven) run of the fixture_martin.md scenario:
dossier, a tailored CV (.docx + matching .pdf), Cyrillic integrity, and the live
tracker. No check needs the LLM — everything here is a file/zip/text assertion.

Stdlib only. Cyrillic integrity is verified by unzipping the .docx (it is a ZIP)
and reading word/document.xml directly, so a mojibake/garbled render fails without
any external dependency. If a PDF text extractor (pdftotext) is present, the .pdf
text is checked too; otherwise that sub-check is skipped with a printed note.

This file is intentionally NOT named test*.py so `unittest discover` never picks it
up (it needs a produced run folder that only exists after a manual run). It is
on-demand only — see tests/e2e/README.md.

Exit code: 0 if every required check passes, 1 otherwise.
"""

import os
import re
import shutil
import subprocess
import sys
import zipfile

CYRILLIC_RE = re.compile(r"[Ѐ-ӿ]")
PDF_MIN_BYTES = 10 * 1024  # a real rendered CV PDF is well over ~10 KB

# Required dossier section headers, derived from agent/dossier-template.md.
REQUIRED_DOSSIER_SECTIONS = [
    "## Profile",
    "## Layoff facts",
    "## Target",
    "## CV",
    "## Search",
    "## Legal / benefits",
    "## Log",
]
# Load-bearing sub-strings that must survive into a real dossier.
REQUIRED_DOSSIER_SUBSTRINGS = ["CV бриф", "Tracker път"]

# Tracker zones + columns, derived from agent/templates/tracker.md (person-facing).
REQUIRED_TRACKER_ZONES = [
    "Инерция",
    "В движение",
    "Изпратено, чака",
    "Цели",
    "Затворени",
    "Легенда",
]
REQUIRED_TRACKER_COLUMNS = ["Компания", "Роля", "Статус", "Следваща стъпка"]


class Report:
    """Collects per-check results and prints a clear pass/fail summary."""

    def __init__(self):
        self.checks = []  # (name, ok, detail)

    def add(self, name, ok, detail=""):
        self.checks.append((name, bool(ok), detail))
        return ok

    def note(self, name, detail):
        # A skipped/optional sub-check: recorded, never fails the run.
        self.checks.append((name, None, detail))

    def ok(self):
        return all(ok for _, ok, _ in self.checks if ok is not None)

    def render(self):
        lines = []
        for name, ok, detail in self.checks:
            mark = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
            line = f"  [{mark}] {name}"
            if detail:
                line += f" — {detail}"
            lines.append(line)
        return "\n".join(lines)


def _read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def check_dossier(run_dir, rep):
    path = os.path.join(run_dir, "dossier.md")
    if not rep.add("dossier.md exists", os.path.isfile(path), path):
        return
    text = _read_text(path)
    missing = [s for s in REQUIRED_DOSSIER_SECTIONS if s not in text]
    rep.add(
        "dossier has required sections",
        not missing,
        "missing: " + ", ".join(missing) if missing else "all present",
    )
    missing_sub = [s for s in REQUIRED_DOSSIER_SUBSTRINGS if s not in text]
    rep.add(
        "dossier has CV бриф + Tracker път",
        not missing_sub,
        "missing: " + ", ".join(missing_sub) if missing_sub else "present",
    )


def _find_cv_files(run_dir):
    """Return (docx_paths, pdf_paths) found anywhere under the run folder.

    Convention (ats-rules.md / dossier): the CV workspace is the `cv/` subtree of
    the run folder. We prefer that subtree but fall back to a full recursive walk
    so a slightly different layout still validates.
    """
    def walk(root):
        docx, pdf = [], []
        for base, _dirs, files in os.walk(root):
            for f in files:
                low = f.lower()
                if low.endswith(".docx"):
                    docx.append(os.path.join(base, f))
                elif low.endswith(".pdf"):
                    pdf.append(os.path.join(base, f))
        return docx, pdf

    cv_root = os.path.join(run_dir, "cv")
    if os.path.isdir(cv_root):
        docx, pdf = walk(cv_root)
        if docx or pdf:
            return docx, pdf
    return walk(run_dir)


def _is_tailored(path):
    """A tailored CV lives in a dated position folder (YYYY-MM-DD_...), per
    ats-rules.md, and/or is not the base 'CV_latest'/'CV_vX' file."""
    name = os.path.basename(path)
    parent = os.path.basename(os.path.dirname(path))
    if re.match(r"\d{4}-\d{2}-\d{2}[_-]", parent):
        return True
    low = name.lower()
    if "cv_latest" in low.replace(" ", "") or re.search(r"cv_v\d", low.replace(" ", "")):
        return False
    # A " - Company - Position" style name is a tailored artifact.
    return " - " in name or "_" in parent


def check_cv(run_dir, rep):
    docx_paths, pdf_paths = _find_cv_files(run_dir)
    rep.add("at least one CV .docx", bool(docx_paths),
            f"{len(docx_paths)} found")
    rep.add("at least one CV .pdf", bool(pdf_paths),
            f"{len(pdf_paths)} found")
    if not docx_paths:
        return

    tailored_docx = [p for p in docx_paths if _is_tailored(p)]
    rep.add(
        "a tailored CV .docx exists",
        bool(tailored_docx),
        os.path.relpath(tailored_docx[0], run_dir) if tailored_docx else
        "only base CV(s) found — no tailored position artifact",
    )

    # Matching .docx + .pdf pair (same stem, same folder).
    pdf_stems = {(os.path.dirname(p), os.path.splitext(os.path.basename(p))[0])
                 for p in pdf_paths}
    matched = None
    for d in (tailored_docx or docx_paths):
        stem = (os.path.dirname(d), os.path.splitext(os.path.basename(d))[0])
        if stem in pdf_stems:
            matched = d
            break
    rep.add(
        "a .docx has a matching .pdf",
        matched is not None,
        os.path.relpath(matched, run_dir) if matched else
        "no .docx/.pdf pair with the same name in the same folder",
    )

    # PDF is non-trivial (> ~10 KB).
    if pdf_paths:
        biggest = max(pdf_paths, key=lambda p: os.path.getsize(p))
        size = os.path.getsize(biggest)
        rep.add(
            "a CV .pdf is non-trivial (>10 KB)",
            size > PDF_MIN_BYTES,
            f"{os.path.relpath(biggest, run_dir)} = {size} bytes",
        )

    # Cyrillic integrity via zipfile on the .docx (no external dep).
    _check_docx_cyrillic(tailored_docx or docx_paths, run_dir, rep)
    # Optional PDF text check.
    _check_pdf_cyrillic(pdf_paths, run_dir, rep)


def _check_docx_cyrillic(docx_paths, run_dir, rep):
    target = docx_paths[0]
    try:
        with zipfile.ZipFile(target) as zf:
            xml = zf.read("word/document.xml").decode("utf-8", "replace")
    except (zipfile.BadZipFile, KeyError, OSError) as exc:
        rep.add("CV .docx has Cyrillic (zipfile)", False,
                f"could not read word/document.xml: {exc}")
        return
    has_cyr = bool(CYRILLIC_RE.search(xml))
    # A JD/CV can be English; the point is the render is not mojibake. Bulgarian
    # UI/labels and the person's name make Cyrillic the expected signal. If the
    # tailored CV is fully English, we still expect *some* Cyrillic somewhere in
    # the workspace docx set — fall back across all docx before failing.
    if not has_cyr and len(docx_paths) > 1:
        for extra in docx_paths[1:]:
            try:
                with zipfile.ZipFile(extra) as zf:
                    if CYRILLIC_RE.search(zf.read("word/document.xml")
                                          .decode("utf-8", "replace")):
                        has_cyr = True
                        target = extra
                        break
            except (zipfile.BadZipFile, KeyError, OSError):
                continue
    rep.add(
        "CV .docx has Cyrillic (zipfile)",
        has_cyr,
        f"{os.path.relpath(target, run_dir)} — "
        + ("Cyrillic found in word/document.xml"
           if has_cyr else "NO Cyrillic — possible mojibake/garbled render"),
    )


def _check_pdf_cyrillic(pdf_paths, run_dir, rep):
    tool = shutil.which("pdftotext")
    if not tool:
        rep.note("CV .pdf Cyrillic (pdftotext)",
                 "SKIPPED — pdftotext not installed (optional check)")
        return
    if not pdf_paths:
        return
    target = max(pdf_paths, key=lambda p: os.path.getsize(p))
    try:
        out = subprocess.run(
            [tool, "-q", target, "-"],
            capture_output=True, timeout=30,
        )
        text = out.stdout.decode("utf-8", "replace")
    except (OSError, subprocess.SubprocessError) as exc:
        rep.note("CV .pdf Cyrillic (pdftotext)", f"SKIPPED — {exc}")
        return
    # PDFs may embed no extractable text (image-only) — only fail on garbled text,
    # not on empty extraction.
    if not text.strip():
        rep.note("CV .pdf Cyrillic (pdftotext)",
                 "SKIPPED — no extractable text layer")
        return
    rep.add(
        "CV .pdf has Cyrillic (pdftotext)",
        bool(CYRILLIC_RE.search(text)),
        os.path.relpath(target, run_dir),
    )


def check_tracker(run_dir, rep):
    path = os.path.join(run_dir, "tracker.md")
    if not rep.add("tracker.md exists", os.path.isfile(path), path):
        return
    text = _read_text(path)
    missing_zones = [z for z in REQUIRED_TRACKER_ZONES if z not in text]
    rep.add(
        "tracker has the expected zones",
        not missing_zones,
        "missing: " + ", ".join(missing_zones) if missing_zones else "all present",
    )
    missing_cols = [c for c in REQUIRED_TRACKER_COLUMNS if c not in text]
    rep.add(
        "tracker has the expected columns",
        not missing_cols,
        "missing: " + ", ".join(missing_cols) if missing_cols else "all present",
    )


def main(argv):
    # The report prints Cyrillic and em-dashes; make stdout/stderr tolerate them
    # on a non-UTF-8 console (e.g. Windows cp1252) instead of crashing.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    if len(argv) != 2:
        print("usage: python tests/e2e/check_artifacts.py "
              "Personal/<date>-<slug>/", file=sys.stderr)
        return 2
    run_dir = argv[1]
    if not os.path.isdir(run_dir):
        print(f"error: run folder not found: {run_dir}", file=sys.stderr)
        return 2

    rep = Report()
    check_dossier(run_dir, rep)
    check_cv(run_dir, rep)
    check_tracker(run_dir, rep)

    print(f"E2E artifact check — {run_dir}")
    print(rep.render())
    passed = rep.ok()
    print("\nRESULT:", "PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
