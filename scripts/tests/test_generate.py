"""Tests for the generators (scripts/generate.py) and the checks on them in check_cv.py.
    python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_cv  # noqa: E402
import cv_numbers  # noqa: E402
import cvlib  # noqa: E402
import funder_profile  # noqa: E402
import generate  # noqa: E402
import venue_profile  # noqa: E402

MAIN_TEX = r"""
\setreviewperiod{2025}{2026}
\addtocategory{journal}{j2020, j2025}
\addtocategory{conference}{c2025, c2026}
\addtocategory{abstracts}{a2026}
\addtocategory{presentations}{p2025, p2027}
\addtocategory{aprinclude}{p2027}
\addtocategory{aprnone}{c2026}
"""

SCHOLAR_BIB = r"""
@article{j2020, author = {Lee*, Ann and \textbf{James R. Wallace}}, title = {A}, year = {2020}, journal = {Health Journal}}
@article{j2025, author = {\textbf{James R. Wallace} and Lee*, Ann}, title = {B}, year = {2025}, journal = {HCI Journal}}
@inproceedings{c2025, author = {Kim*, Bo}, title = {C}, year = {2025}, booktitle = {Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems}}
@inproceedings{c2026, author = {Kim*, Bo}, title = {D}, year = {2026}, booktitle = {Proceedings of ICHEC 2026}}
@inproceedings{a2026, author = {Roe, Cy}, title = {E}, year = {2026}, booktitle = {Extended Abstracts of the CHI Conference on Human Factors in Computing Systems}}
@misc{p2025, author = {Kim*{\dag}, Bo}, title = {F}, year = {2025}}
@misc{p2027, author = {Roe, Cy}, title = {G}, year = {2027}}
"""

VENUES_YAML = """journals:
  - name: Health Journal
    field: health
  - name: HCI Journal
    field: hci
proceedings:
  - name: ICHEC
    field: health
    match: ["ICHEC"]
  - name: CHI
    field: hci
    match: ["Human Factors in Computing Systems"]
"""

GRANTS_BIB = r"""
@grant{phac2017, investigators = {\me}, role = {PI}, agency = {PHAC}, amount = {1}, date = {2017}, title = {T}}
@grant{cihr2020, investigators = {X and \me}, role = {Co-I}, agency = {CIHR}, amount = {1}, date = {2020/2021}, title = {T}}
@grant{cihr2022, investigators = {X and \me}, role = {Co-A}, agency = {CIHR Project Grant}, amount = {1}, date = {2022/2024}, title = {T}}
@grant{nserc2015, investigators = {\me}, role = {PI}, agency = {NSERC}, amount = {1}, date = {2015/2022}, title = {T}}
@grant{cihr2026, investigators = {\me}, agency = {CIHR Project Grant}, submitted = {2026}, status = {Submitted}}
"""

FUNDERS_YAML = """funders:
  - name: Public Health Agency of Canada
    sector: health
    agency: ["PHAC"]
  - name: CIHR
    sector: health
    agency: ["CIHR", "CIHR Project Grant"]
  - name: NSERC
    sector: nse
    agency: ["NSERC"]
"""

CITATION_YAML = """exported: 2026-11-20
threshold: 10
j2020: 3 | 5.0 | 50 | 2020
c2025: 20 | 1.0 | 5 | 2025
j2025: 8 | 2.0 | 9 | 2025
c2026: 1 | 9.0 | 2 | 2026
"""


class Generators(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "data").mkdir()
        shutil.copy(cvlib.ROOT / "data" / "trainees.yaml", self.root / "data" / "trainees.yaml")
        for name in check_cv.RECORD_FILES:
            (self.root / name).write_text("", encoding="utf-8")
        files = {"main.tex": MAIN_TEX, "scholar.bib": SCHOLAR_BIB, "grants.bib": GRANTS_BIB,
                 "data/venues.yaml": VENUES_YAML, "data/funders.yaml": FUNDERS_YAML,
                 "data/citation-impact.yaml": CITATION_YAML}
        for name, text in files.items():
            (self.root / name).write_text(text, encoding="utf-8")
        self.saved = check_cv.ROOT
        check_cv.ROOT = self.root

    def tearDown(self):
        check_cv.ROOT = self.saved
        shutil.rmtree(self.root)

    def write(self, name, text):
        (self.root / name).write_text(text, encoding="utf-8")

    def append(self, name, text):
        with (self.root / name).open("a", encoding="utf-8") as f:
            f.write(text)

    def regenerate(self):
        for path, text, problems in generate.results(self.root):
            self.assertEqual(problems, [])
            (self.root / path).write_text(text, encoding="utf-8")

    def codes(self, code):
        report = check_cv.run()
        return [x for x in report["errors"] + report["warnings"] if x["code"] == code]

    # ---------------------------------------------------------------- funders
    def test_the_funder_sentence_groups_by_role_and_funder(self):
        text, problems = funder_profile.build(self.root)
        self.assertEqual(problems, [])
        self.assertIn("I was PI of a Public Health Agency of Canada project (2017) and a "
                      "co-investigator or co-applicant on two CIHR grants (2020--21 and 2022--24).",
                      text)
        self.assertNotIn("NSERC", text)  # not a health funder
        self.assertNotIn("2026", text)  # an application, not a funded grant

    def test_years(self):
        self.assertEqual(funder_profile.years("2017"), "2017")
        self.assertEqual(funder_profile.years("2017/2018"), "2017--18")
        self.assertEqual(funder_profile.years("1999/2001"), "1999--2001")

    def test_an_unknown_agency_warns(self):
        self.append("grants.bib", "@grant{x2024, investigators = {\\me}, role = {PI}, agency = "
                    "{New Agency}, amount = {1}, date = {2024}, title = {T}}\n")
        self.regenerate_where_possible()
        found = self.codes("W-funders")
        self.assertEqual([w["key"] for w in found], ["x2024"])

    def regenerate_where_possible(self):
        for path, text, problems in generate.results(self.root):
            if text is not None:
                (self.root / path).write_text(text, encoding="utf-8")

    # ---------------------------------------------------------------- venues
    def test_proceedings_are_classified(self):
        classified, problems = venue_profile.classify(self.root)
        self.assertEqual(problems, [])
        fields = {k: v["field"] for k, v, _ in classified["proceedings"]}
        self.assertEqual(fields, {"c2025": "hci", "c2026": "health", "a2026": "hci"})

    def test_an_unmatched_proceedings_entry_warns(self):
        self.append("scholar.bib", "@inproceedings{c2024, title = {H}, year = {2024}, "
                    "booktitle = {Proceedings of Somewhere New}}\n")
        self.append("main.tex", "\\addtocategory{conference}{c2024}\n")
        self.assertEqual([w["key"] for w in self.codes("W-venues")], ["c2024"])

    def test_the_plain_reader_matches_pyyaml(self):
        saved = sys.modules.get("yaml")
        sys.modules["yaml"] = None  # import yaml now raises ImportError
        try:
            plain = cvlib.load_tagged(self.root / "data" / "venues.yaml")
            funders = cvlib.load_tagged(self.root / "data" / "funders.yaml")
        finally:
            if saved is None:
                del sys.modules["yaml"]
            else:
                sys.modules["yaml"] = saved
        self.assertEqual(plain["proceedings"][1], {"name": "CHI", "field": "hci",
                                                   "match": ["Human Factors in Computing Systems"]})
        self.assertEqual(funders["funders"][1]["agency"], ["CIHR", "CIHR Project Grant"])
        self.assertEqual([len(v) for v in plain.values()], [2, 2])

    def test_the_real_files_read_the_same_without_pyyaml(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML not installed")
        for name in ("venues.yaml", "funders.yaml"):
            path = cvlib.ROOT / "data" / name
            with_yaml = cvlib.load_tagged(path)
            saved = sys.modules["yaml"]
            sys.modules["yaml"] = None
            try:
                self.assertEqual(cvlib.load_tagged(path), with_yaml, name)
            finally:
                sys.modules["yaml"] = saved

    # ---------------------------------------------------------------- numbers
    def numbers(self):
        nums, problems = cv_numbers.numbers(self.root)
        self.assertEqual(problems, [])
        return {name: value for name, value, _ in nums}

    def test_review_period_counts_and_trainee_first_authors(self):
        n = self.numbers()
        # j2025 (trainee second), c2025 (trainee first); c2026 is in aprnone; a2026 by Roe;
        # p2025 (trainee first); p2027 by aprinclude
        self.assertEqual((n["review-journal"], n["review-journal-trainee-first"]), (1, 0))
        self.assertEqual((n["review-conference"], n["review-conference-trainee-first"]), (2, 1))
        self.assertEqual((n["review-presentations"], n["review-presentations-trainee-first"]), (2, 1))
        self.assertEqual((n["review-works"], n["review-works-trainee-first"]), (5, 2))

    def test_scival_counts_leave_out_the_export_year(self):
        n = self.numbers()
        self.assertEqual(n["scival-last-year"], 2025)
        self.assertEqual(n["scival-papers"], 3)  # c2026 is too new
        self.assertEqual(n["scival-top"], 2)  # j2020 and j2025
        self.assertEqual(n["scival-top-share"], 67)
        self.assertEqual(n["scival-top-trainee-first"], 1)  # j2020

    def test_venue_and_funder_counts(self):
        n = self.numbers()
        self.assertEqual((n["journals"], n["journals-health"]), (2, 1))
        self.assertEqual((n["proceedings"], n["proceedings-health"]), (3, 1))
        self.assertEqual((n["grants-funded"], n["grants-funded-health"]), (4, 3))

    def test_an_undefined_number_is_an_error(self):
        self.regenerate()
        self.append("main.tex", "Of \\cvnumber{review-works} and \\cvnumber{no-such-count}.\n")
        self.assertEqual(len(self.codes("E-numbers")), 1)

    def test_a_hard_coded_number_warns(self):
        self.regenerate()
        self.append("main.tex", "Trainees are first authors on 2 of the 5 papers.\n")
        self.assertEqual(len(self.codes("W-numbers")), 1)
        self.write("main.tex", MAIN_TEX + "Trainees are first authors on \\cvnumber{review-works-"
                   "trainee-first} of the \\cvnumber{review-works} papers.\n")
        self.assertEqual(self.codes("W-numbers"), [])

    # ---------------------------------------------------------------- staleness
    def test_stale_files_warn_until_regenerated(self):
        stale = {w["msg"].split(" ", 1)[0] for w in self.codes("W-generated")}
        self.assertEqual(stale, {"data/venue-profile.tex", "data/funders.tex",
                                 "data/cv-numbers.tex", "data/citation-impact.tex",
                                 "data/gaps.tex"})
        self.regenerate()
        self.assertEqual(self.codes("W-generated"), [])
        # a new trainee-led paper changes the counts, so cv-numbers goes stale
        self.append("scholar.bib", "@misc{p2026, author = {Kim*, Bo}, title = {I}, year = {2026}}\n")
        self.append("main.tex", "\\addtocategory{presentations}{p2026}\n")
        stale = {w["msg"].split(" ", 1)[0] for w in self.codes("W-generated")}
        self.assertEqual(stale, {"data/cv-numbers.tex"})  # a misc entry has no gaps to list

    # ---------------------------------------------------------------- gaps
    def test_paper_gaps(self):
        import gaps
        found = dict(gaps.gaps(self.root))
        # none of the test papers has a DOI, pages or a rate
        self.assertEqual(found["j2025"], ["DOI", "pages", "acceptance rate or impact factor"])
        self.append("scholar.bib", "@article{j2026, title = {J}, year = {2026}, doi = {10.1/j}, "
                    "articleno = {3}, note = {In press. Journal Impact Factor (2025): 4.0}}\n")
        self.append("main.tex", "\\addtocategory{journal}{j2026}\n")
        self.assertEqual(dict(gaps.gaps(self.root))["j2026"],
                         ["final publication details (in press)"])
        self.assertNotIn("p2025", found)  # presentations are not checked

    def test_detail_gaps(self):
        # the "so what?" facts (CLAUDE.md -> Entry detail)
        import gaps
        self.append("scholar.bib",
                    "@inproceedings{aw2025, title = {A}, year = {2025}, doi = {10.1/a}, pages = {1--2}, "
                    "icon = {award}, note = {\\textbf{Best Paper Award}. Acceptance rate: 20\\%}}\n"
                    "@inproceedings{at2025, title = {B}, year = {2025}, doi = {10.1/b}, pages = {1--2}, "
                    "icon = {award}, note = {\\textbf{Best Paper Award} (top 1\\% of submissions). "
                    "Acceptance rate: 20\\%}}\n"
                    "@inproceedings{mu2025, title = {C}, year = {2025}, doi = {10.1/c}, pages = {1--2}, "
                    "note = {Meetup. Acceptance rate: 50\\%}}\n"
                    "@inproceedings{ws2025, title = {D}, year = {2025}, doi = {10.1/d}, pages = {1--2}, "
                    "note = {Workshop proposal. Acceptance rate: 23\\%. 111 participants in person}}\n")
        self.append("main.tex", "\\addtocategory{conference}{aw2025, at2025, mu2025, ws2025}\n")
        self.write("service.bib",
                   "@service{gc2025, title = {T}, level = {discipline, organizing}, date = {2025}, "
                   "role = {General Chair}}\n"
                   "@service{gc2026, title = {T}, level = {organizing}, date = {2026}, role = {General Chair}, "
                   "note = {About 130 attendees. Almost 300 submissions.}}\n"
                   "@service{ecw2026, title = {T}, level = {organizing, mentorship}, date = {2026}, "
                   "role = {Early Career Workshop Chair}, note = {For 15 early-career researchers.}}\n"
                   "@service{tpc2027, title = {T}, level = {organizing}, date = {2026/2027}, years = {2027}, "
                   "role = {Technical Program Chair}}\n"
                   "@service{gc2023, title = {T}, level = {organizing}, date = {2023}, role = {General Chair}}\n"
                   "@service{pc2025, title = {T}, level = {programcommittee}, date = {2025}}\n")
        self.write("activities.bib",
                   "@service{ae2024, title = {J}, level = {editorial}, date = {2024/}, role = {Associate Editor}}\n"
                   "@service{ae2025, title = {J}, level = {editorial}, date = {2025}, note = {12 submissions}}\n"
                   "@service{ae2020, title = {J}, level = {editorial}, date = {2019/2020}}\n")
        found = dict(gaps.gaps(self.root))
        self.assertIn("award tier", found["aw2025"])
        self.assertNotIn("award tier", found.get("at2025", []))
        self.assertIn("attendance", found["mu2025"])
        self.assertNotIn("attendance", found.get("ws2025", []))
        self.assertEqual(found["gc2025"], ["attendance", "submissions"])
        for key in ("gc2026", "ecw2026", "tpc2027", "gc2023", "pc2025", "ae2025", "ae2020"):
            self.assertNotIn(key, found)  # complete, still to come, before the period, or not a chair
        self.assertEqual(found["ae2024"], ["load"])  # ongoing through the period
        self.write("data/gaps.yaml", "gc2025: submissions | not published | 2026-11-22\n")
        self.assertEqual(dict(gaps.gaps(self.root))["gc2025"], ["attendance"])

    def test_metrics_yaml_none_and_unresolved(self):
        import gaps
        self.write("data/metrics.yaml", "c2025: none | Extended abstract | 2026-01-01\n"
                   "c2026: unresolved | not found | 2026-02-02\n")
        found = dict(gaps.gaps(self.root))
        self.assertNotIn("acceptance rate or impact factor", found["c2025"])
        self.assertIn("acceptance rate or impact factor (unresolved, last looked for 2026-02-02)",
                      found["c2026"])

    def test_record_gaps_and_accepted_gaps(self):
        import gaps
        self.write("supervision.bib",
                   "@supervision{s1, author = {Kim, Bo}, degree = {PhD}, status = {In progress}}\n"
                   "@supervision{s2, author = {Lee, Ann}, degree = {MSc}, program = {CS}, "
                   "started = {2019}, date = {2021}, title = {T}}\n"
                   "@supervision{s3, author = {Roe, Cy}, degree = {PDF}, started = {2020}, "
                   "date = {2022}, title = {T}, position = {P}}\n")
        self.write("committees.bib", "@committee{c1, author = {X, Y}, degree = {PhD}, date = {2024}, "
                   "note = {defended 2025}}\n@committee{c2, degree = {PhD}, date = {2019}, count = {3}}\n")
        self.write("courses.bib", "@course{k1, course = {HLTH 1}, date = {2026-01}, enrolment = {40}}\n")
        found = dict(gaps.gaps(self.root))
        self.assertEqual(found["s1"], ["program", "start year"])
        self.assertEqual(found["s2"], ["position"])
        self.assertNotIn("s3", found)  # a postdoc has no program
        self.assertEqual(found["c1"], ["thesis title"])
        self.assertNotIn("c2", found)
        self.assertEqual(found["k1"], ["SCP responses", "SCP scores"])
        self.write("data/gaps.yaml", "k1: responses, scp | no survey that term | 2026-11-22\n"
                   "s1: started | not known\n")
        found = dict(gaps.gaps(self.root))
        self.assertNotIn("k1", found)
        self.assertEqual(found["s1"], ["program"])

    def test_the_gap_file_escapes_tex(self):
        import gaps
        self.write("courses.bib", "@course{k1, course = {HLTH 1}, date = {2026-01}}\n")
        text, _ = gaps.build(self.root)
        self.assertIn(r"\setentrygap{k1}{enrolment, SCP responses, SCP scores}", text)
        self.assertIn(r"\providecommand\setentrygap[2]{}", text)

    def test_the_real_files_are_in_step(self):
        problems, stale = generate.check(cvlib.ROOT)
        self.assertEqual((problems, stale), ([], []))


if __name__ == "__main__":
    unittest.main()
