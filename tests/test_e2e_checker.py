#!/usr/bin/env python3
"""Regression tests for the e2e artifact checker's Cyrillic logic.

Locks the fix for the false-FAIL where an all-English tailored CV made the
Cyrillic check fail even though a Bulgarian base CV in the same run carried the
Cyrillic signal. The check must assert "at least one CV .docx in the run contains
Cyrillic", not "the tailored CV contains Cyrillic".

Stdlib only. Builds synthetic .docx files (a .docx is a ZIP with word/document.xml)
in a tempdir — no repo/Personal writes, no external dependencies. Named test*.py so
`python -m unittest discover -s tests` picks it up.
"""

import importlib.util
import os
import tempfile
import unittest
import zipfile

# Import check_artifacts.py by path (it lives under tests/e2e/, not on sys.path
# and intentionally not named test*.py so discover ignores it).
_CHECKER_PATH = os.path.join(
    os.path.dirname(__file__), "e2e", "check_artifacts.py"
)
_spec = importlib.util.spec_from_file_location("check_artifacts", _CHECKER_PATH)
check_artifacts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_artifacts)


def _write_docx(path, body_text):
    """Write a minimal, valid .docx (ZIP) whose word/document.xml holds body_text."""
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>'
        + body_text
        + "</w:t></w:r></w:p></w:body></w:document>"
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("word/document.xml", document_xml)


class CyrillicCheckTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.run_dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _run_cyrillic_check(self, docx_paths):
        rep = check_artifacts.Report()
        check_artifacts._check_docx_cyrillic(docx_paths, self.run_dir, rep)
        # Exactly one check is recorded by _check_docx_cyrillic.
        self.assertEqual(len(rep.checks), 1)
        name, ok, detail = rep.checks[0]
        self.assertIn("Cyrillic", name)
        return ok, detail

    def test_english_tailored_plus_bulgarian_base_passes(self):
        """English tailored CV + Bulgarian base CV → PASS (base carries Cyrillic)."""
        tailored = os.path.join(
            self.run_dir, "cv", "2026-09-06_role", "Martin Georgiev CV - Role.docx"
        )
        base = os.path.join(self.run_dir, "cv", "Мартин Георгиев CV_latest.docx")
        _write_docx(tailored, "Martin Georgiev - Senior Backend Engineer")
        _write_docx(base, "Мартин Георгиев — автобиография")

        # Order matters for the bug: tailored (no Cyrillic) is scanned first.
        ok, detail = self._run_cyrillic_check([tailored, base])
        self.assertTrue(ok, f"expected PASS, got FAIL: {detail}")

    def test_no_cyrillic_anywhere_fails(self):
        """No .docx contains Cyrillic → FAIL (real mojibake/garbled signal)."""
        d1 = os.path.join(self.run_dir, "cv", "a.docx")
        d2 = os.path.join(self.run_dir, "cv", "b.docx")
        _write_docx(d1, "All English content here")
        _write_docx(d2, "Also entirely Latin text")

        ok, detail = self._run_cyrillic_check([d1, d2])
        self.assertFalse(ok, f"expected FAIL, got PASS: {detail}")

    def test_single_bulgarian_docx_passes(self):
        """A single Cyrillic-bearing .docx passes (no >1 guard needed)."""
        only = os.path.join(self.run_dir, "cv", "Мартин CV.docx")
        _write_docx(only, "Мартин Георгиев")
        ok, detail = self._run_cyrillic_check([only])
        self.assertTrue(ok, f"expected PASS, got FAIL: {detail}")


if __name__ == "__main__":
    unittest.main()
