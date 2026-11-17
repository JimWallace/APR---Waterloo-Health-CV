"""Tests for check_cv.py's exemptions.   python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_cv  # noqa: E402
import cvlib  # noqa: E402

MAIN_TEX = r"""
\DeclareBibliographyCategory{conference}
\addtocategory{conference}{plain2020, exempt2020, emptyreason2020, both2020}
\DeclareBibliographyCategory{unprinted}
\addtocategory{unprinted}{kept2020, both2020}
"""

SCHOLAR_BIB = r"""
@inproceedings{plain2020, title = {A}, year = {2020}}
@inproceedings{exempt2020, title = {B}, year = {2020}, nodoi = {Poster; no proceedings}}
@inproceedings{emptyreason2020, title = {C}, year = {2020}, nodoi = {}}
@inproceedings{both2020, title = {D}, year = {2020}, doi = {10.1/x}}
@misc{kept2020, title = {E}, year = {2020}}
@misc{stray2020, title = {F}, year = {2020}}
"""


class FieldReader(unittest.TestCase):
    def test_fields_after_a_commented_line_are_read(self):
        d = Path(tempfile.mkdtemp())
        p = d / "x.bib"
        p.write_text("@inproceedings{k,\n  year = {2026},\n  % pages = {--},\n  doi = {10.1/y},\n}\n",
                     encoding="utf-8")
        self.assertEqual(cvlib.parse_bib(p).entries[0].fields.get("doi"), "10.1/y")


class Exemptions(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "data").mkdir()
        shutil.copy(cvlib.ROOT / "data" / "trainees.yaml", self.root / "data" / "trainees.yaml")
        for name in check_cv.RECORD_FILES:
            (self.root / name).write_text("", encoding="utf-8")
        (self.root / "main.tex").write_text(MAIN_TEX, encoding="utf-8")
        (self.root / "scholar.bib").write_text(SCHOLAR_BIB, encoding="utf-8")
        self.saved = check_cv.ROOT
        check_cv.ROOT = self.root

    def tearDown(self):
        check_cv.ROOT = self.saved
        shutil.rmtree(self.root)

    def warnings(self, code):
        return {(w["key"], w["msg"]) for w in check_cv.run()["warnings"] if w["code"] == code}

    def test_nodoi_with_a_reason_silences_the_missing_doi_warning(self):
        keys = {k for k, _ in self.warnings("W-nodoi")}
        self.assertIn("plain2020", keys)
        self.assertNotIn("exempt2020", keys)

    def test_empty_nodoi_still_warns(self):
        msgs = [m for k, m in self.warnings("W-nodoi") if k == "emptyreason2020"]
        self.assertEqual(len(msgs), 1)
        self.assertIn("empty nodoi", msgs[0])

    def test_unprinted_category_silences_the_unprinted_warning(self):
        keys = {k for k, _ in self.warnings("W-unprinted")}
        self.assertIn("stray2020", keys)
        self.assertNotIn("kept2020", keys)
        self.assertFalse(self.warnings("W-cat"))

    def test_a_key_both_printed_and_unprinted_warns(self):
        msgs = [m for k, m in self.warnings("W-unprinted") if k == "both2020"]
        self.assertEqual(len(msgs), 1)
        self.assertIn("also in conference", msgs[0])


if __name__ == "__main__":
    unittest.main()
