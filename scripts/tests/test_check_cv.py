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
\setreviewperiod{2020}{2021}
\addtocategory{conference}{meetup2020, also2020}
\addtocategory{aprservice}{meetup2020}
\addtocategory{apralsoteaching}{meetup2020, also2020}
\addtocategory{apralsoresearch}{meetup2020}
\addtocategory{conference}{ws2020, ws2021, mu2021}
\addtocategory{apralsoservice}{ws2020}
"""

SCHOLAR_BIB = r"""
@inproceedings{plain2020, title = {A}, year = {2020}}
@inproceedings{exempt2020, title = {B}, year = {2020}, nodoi = {Poster; no proceedings}}
@inproceedings{emptyreason2020, title = {C}, year = {2020}, nodoi = {}}
@inproceedings{both2020, title = {D}, year = {2020}, doi = {10.1/x}}
@misc{kept2020, title = {E}, year = {2020}}
@misc{stray2020, title = {F}, year = {2020}}
@inproceedings{meetup2020, title = {G}, year = {2020}, doi = {10.1/g}, note = {Meetup. Acceptance rate: 50\%}}
@inproceedings{ws2020, title = {I}, year = {2020}, doi = {10.1/i}, note = {Workshop proposal}}
@inproceedings{ws2021, title = {J}, year = {2021}, doi = {10.1/j}, note = {Workshop proposal. Acceptance rate: 20\%}}
@inproceedings{mu2021, title = {K}, year = {2021}, doi = {10.1/k}, note = {Meetup.}}
@inproceedings{also2020, title = {H}, year = {2020}, doi = {10.1/h}}
"""



class Software(unittest.TestCase):
    """data/software.yaml and the generated data/software-stats.tex (check_software)."""
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "data").mkdir()
        shutil.copy(cvlib.ROOT / "data" / "trainees.yaml", self.root / "data" / "trainees.yaml")
        for name in check_cv.RECORD_FILES:
            (self.root / name).write_text("", encoding="utf-8")
        (self.root / "main.tex").write_text(
            "\\DeclareBibliographyCategory{software}\n\\addtocategory{software}{tool2020}\n",
            encoding="utf-8")
        (self.root / "scholar.bib").write_text("@misc{tool2020, title = {T}, year = {2020}}\n",
                                               encoding="utf-8")
        self.saved = check_cv.ROOT
        check_cv.ROOT = self.root

    def tearDown(self):
        check_cv.ROOT = self.saved
        shutil.rmtree(self.root)

    def write(self, yaml_text, stats_keys):
        (self.root / "data" / "software.yaml").write_text(yaml_text, encoding="utf-8")
        (self.root / "data" / "software-stats.tex").write_text(
            "".join(f"\\setentrydetail{{{k}}}{{x}}\n" for k in stats_keys), encoding="utf-8")
        r = check_cv.run()
        return ({e["code"] for e in r["errors"]}, {w["code"] for w in r["warnings"]})

    def test_matching_files_pass(self):
        errors, warnings = self.write("# c\ntool2020:\n  repo: https://example.org/x  # c\n", ["tool2020"])
        self.assertNotIn("E-software", errors)
        self.assertNotIn("W-software", warnings)

    def test_unknown_key_is_an_error(self):
        errors, _ = self.write("nosuch2020:\n  repo: x\n", ["nosuch2020"])
        self.assertIn("E-software", errors)

    def test_stale_stats_warn(self):
        _, warnings = self.write("tool2020:\n  repo: x\n", [])
        self.assertIn("W-software", warnings)


VENUES_YAML = """journals:
  - name: Health Journal & Review
    field: health
    aka: ["Health J. Rev."]
  - name: Another Health Journal
    field: health
  - name: Proceedings of HCI
    field: hci
  - name: PLOS ONE
    field: multidisciplinary
"""


class Venues(unittest.TestCase):
    """data/venues.yaml and the generated data/venue-profile.tex (check_venues)."""
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "data").mkdir()
        shutil.copy(cvlib.ROOT / "data" / "trainees.yaml", self.root / "data" / "trainees.yaml")
        for name in check_cv.RECORD_FILES:
            (self.root / name).write_text("", encoding="utf-8")
        (self.root / "main.tex").write_text(
            "\\setreviewperiod{2025}{2026}\n\\DeclareBibliographyCategory{journal}\n"
            "\\addtocategory{journal}{a2020, b2025, c2026, d2027, e2026}\n"
            "\\addtocategory{aprinclude}{d2027}\n\\addtocategory{aprnone}{e2026}\n",
            encoding="utf-8")
        (self.root / "scholar.bib").write_text(
            "@article{a2020, title = {A}, year = {2020}, journal = {Health J. Rev.}}\n"
            "@article{b2025, title = {B}, year = {2025}, journal = {Another Health Journal}}\n"
            "@article{c2026, title = {C}, year = {2026}, journal = {Proceedings of {HCI}}}\n"
            "@article{d2027, title = {D}, year = {2027}, journal = {Plos one}}\n"
            "@article{e2026, title = {E}, year = {2026}, journal = {Proceedings of HCI}}\n",
            encoding="utf-8")
        (self.root / "data" / "venues.yaml").write_text(VENUES_YAML, encoding="utf-8")
        self.saved = check_cv.ROOT
        check_cv.ROOT = self.root

    def tearDown(self):
        check_cv.ROOT = self.saved
        shutil.rmtree(self.root)

    def venue_warnings(self):
        return [w for w in check_cv.run()["warnings"] if w["code"] == "W-venues"
                or w["code"] == "W-generated" and "venue-profile" in w["msg"]]

    def test_the_profile_counts_fields_and_the_review_period(self):
        import venue_profile
        text, problems = venue_profile.build(self.root)
        self.assertEqual(problems, [])
        self.assertIn("Of the 5 refereed journal articles below, 2 are in health journals "
                      r"(\emph{Another Health Journal} and \emph{Health Journal \& Review}), "
                      r"2 in an HCI journal and 1 in a multidisciplinary journal (\emph{PLOS ONE}).",
                      text)
        # b2025 and c2026 by year, d2027 by aprinclude; e2026 is in aprnone
        self.assertIn(r"\ifAPR Of the 3 in the review period (2025--2026), 1 is in a health journal.\fi",
                      text)

    def test_the_plain_reader_matches_pyyaml(self):
        import venue_profile
        got = venue_profile.load_venues(self.root / "data" / "venues.yaml")
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.assertEqual(got[0], {"name": "Health Journal & Review", "field": "health",
                                      "aka": ["Health J. Rev."]})
        self.assertEqual([v["field"] for v in got], ["health", "health", "hci", "multidisciplinary"])

    def test_a_stale_profile_warns_and_a_fresh_one_does_not(self):
        self.assertEqual(len(self.venue_warnings()), 1)
        import venue_profile
        (self.root / "data" / "venue-profile.tex").write_text(venue_profile.build(self.root)[0],
                                                              encoding="utf-8")
        self.assertEqual(self.venue_warnings(), [])

    def test_a_journal_with_no_field_warns(self):
        with (self.root / "scholar.bib").open("a", encoding="utf-8") as f:
            f.write("@article{f2026, title = {F}, year = {2026}, journal = {Unknown Journal}}\n")
        main = (self.root / "main.tex").read_text(encoding="utf-8")
        (self.root / "main.tex").write_text(main + "\\addtocategory{journal}{f2026}\n",
                                            encoding="utf-8")
        keys = {w["key"] for w in self.venue_warnings()}
        self.assertEqual(keys, {"f2026"})


class SoftwareSentence(unittest.TestCase):
    def test_sentence(self):
        import software_stats
        s = {"releases": 1, "commits": 1234, "code": 238456, "tests": 0,
             "first": "2025-11", "last": "2026-02"}
        self.assertEqual(software_stats.sentence(s),
                         "Developed November 2025 -- February 2026: 1 release, 1,234 commits "
                         "and 238,000 lines of code.")

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

    def test_apralsoteaching_without_a_trainee_warns_unless_service_first(self):
        keys = {k for k, _ in self.warnings("W-aprteach")}
        self.assertIn("also2020", keys)
        self.assertNotIn("meetup2020", keys)

    def test_workshops_and_meetups_need_their_colours(self):
        found = {k: m for k, m in self.warnings("W-organized")}
        self.assertEqual(set(found), {"ws2021", "mu2021"})
        self.assertIn("apralsoservice", found["ws2021"])
        self.assertIn("aprservice, apralsoteaching, apralsoresearch", found["mu2021"])

    def test_a_key_both_printed_and_unprinted_warns(self):
        msgs = [m for k, m in self.warnings("W-unprinted") if k == "both2020"]
        self.assertEqual(len(msgs), 1)
        self.assertIn("also in conference", msgs[0])



class ServiceRecords(unittest.TestCase):
    """service.bib: each role needs a title, a level some \\printservice prints, and YYYY[/YYYY]."""

    def errors(self, service_bib):
        records = {name: cvlib.parse_bib(self.write(name, "")) for name in check_cv.RECORD_FILES}
        records["service.bib"] = cvlib.parse_bib(self.write("service.bib", service_bib))
        found = []
        check_cv.check_records(records, "\\printservice{school}\n% \\printservice{faculty}\n",
                               lambda code, msg, key=None: found.append((key, msg)),
                               lambda *a, **k: None)
        return found

    def write(self, name, text):
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return p

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_a_well_formed_role_passes(self):
        self.assertEqual(self.errors("@service{ok, title = {A Committee}, level = {school}, "
                                     "date = {2023/2025}, years = {2023, 2025}}\n"), [])

    def test_an_unprinted_level_is_an_error(self):
        # faculty is only in a comment, so nothing prints it
        errs = self.errors("@service{lost, title = {A Committee}, level = {faculty}, date = {2023}}\n")
        self.assertEqual([k for k, _ in errs], ["lost"])
        self.assertIn("no \\printservice", errs[0][1])

    def test_an_ongoing_role_and_several_levels_pass(self):
        self.assertEqual(self.errors("@service{ongoing, title = {A Committee}, level = {school}, date = {2021/}}\n"
                                     "@service{both, title = {A Chair}, level = {school, school}, date = {2024}}\n"), [])

    def test_each_named_level_must_be_printed(self):
        # school is printed, faculty is only in a comment
        errs = self.errors("@service{half, title = {A Chair}, level = {school, faculty}, date = {2024}}\n")
        self.assertEqual([k for k, _ in errs], ["half"])
        self.assertIn("'faculty'", errs[0][1])

    def test_a_bad_date_is_an_error(self):
        errs = self.errors("@service{when, title = {A Committee}, level = {school}, date = {2023 -- 2025}}\n")
        self.assertEqual([k for k, _ in errs], ["when"])
        self.assertIn("YYYY/YYYY", errs[0][1])


class GrantRecords(unittest.TestCase):
    """grants.bib records every application: funded grants are complete, applications have a
    status and the date they went in, and declines a decision date."""

    FUNDED = ("@grant{funded, investigators = {\\me}, role = {PI}, agency = {NSERC}, "
              "amount = {1000}, date = {2024/2026}, title = {A Grant}}\n")

    def errors(self, grants_bib, main_tex=""):
        records = {name: cvlib.parse_bib(self.write(name, "")) for name in check_cv.RECORD_FILES}
        records["grants.bib"] = cvlib.parse_bib(self.write("grants.bib", grants_bib))
        found = []
        check_cv.check_records(records, main_tex, lambda code, msg, key=None: found.append((key, msg)),
                               lambda *a, **k: None)
        return found

    def write(self, name, text):
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return p

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_a_funded_grant_passes(self):
        self.assertEqual(self.errors(self.FUNDED), [])

    def test_a_funded_grant_needs_its_amount(self):
        errs = self.errors(self.FUNDED.replace("amount = {1000}, ", ""))
        self.assertEqual([k for k, _ in errs], ["funded"])

    def test_a_pending_application_needs_only_when_it_went_in(self):
        self.assertEqual(self.errors("@grant{pending, investigators = {\\me}, agency = {CIHR}, "
                                     "status = {Submitted}, submitted = {2026-09-09}}\n"), [])

    def test_an_application_without_a_submission_date_is_an_error(self):
        errs = self.errors("@grant{when, investigators = {\\me}, agency = {CIHR}, status = {Submitted}}\n")
        self.assertEqual([k for k, _ in errs], ["when"])
        self.assertIn("submitted", errs[0][1])

    def test_a_printed_submitted_application_may_have_gaps(self):
        # missing details print as blank cells (template v0.9.1)
        self.assertEqual(self.errors("@grant{thin, investigators = {\\me}, agency = {CIHR}, "
                                     "status = {Submitted}, submitted = {2026-09}}\n",
                                     "\\printgrants[Submitted]\n"), [])

    def test_a_decline_needs_its_decision_date(self):
        errs = self.errors("@grant{no, investigators = {\\me}, agency = {NFRF}, "
                           "status = {Rejected}, submitted = {2025}}\n")
        self.assertEqual([k for k, _ in errs], ["no"])
        self.assertIn("decided", errs[0][1])
        self.assertEqual(self.errors("@grant{no, investigators = {\\me}, agency = {NFRF}, "
                                     "status = {Rejected}, submitted = {2025}, decided = {2026-03}}\n"), [])

    def test_an_unknown_status_or_bad_date_is_an_error(self):
        errs = self.errors("@grant{odd, investigators = {\\me}, agency = {NFRF}, "
                           "status = {Declined}, submitted = {Sept 2025}, decided = {2026}}\n")
        self.assertEqual(len(errs), 2)
        self.assertTrue(any("status 'Declined'" in m for _, m in errs))
        self.assertTrue(any("submitted 'Sept 2025'" in m for _, m in errs))


class CourseRecords(unittest.TestCase):
    """courses.bib: course, title, a term-start date, digits for enrolment, Item=score pairs."""

    def errors(self, courses_bib):
        records = {name: cvlib.parse_bib(self.write(name, "")) for name in check_cv.RECORD_FILES}
        records["courses.bib"] = cvlib.parse_bib(self.write("courses.bib", courses_bib))
        found = []
        check_cv.check_records(records, "", lambda code, msg, key=None: found.append((key, msg)),
                               lambda *a, **k: None)
        return found

    def write(self, name, text):
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return p

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_a_well_formed_course_passes(self):
        self.assertEqual(self.errors("@course{ok, course = {HLTH 101}, title = {A Course}, date = {2024-09}, "
                                     "enrolment = {40}, scp = {Implementation=4.5, Design=4.0}, "
                                     "scpaverage = {Course Overall=4.1}}\n"), [])

    def test_a_date_that_is_not_a_term_start_is_an_error(self):
        errs = self.errors("@course{when, course = {HLTH 101}, title = {A Course}, date = {2024-10}}\n")
        self.assertEqual([k for k, _ in errs], ["when"])
        self.assertIn("Fall", errs[0][1])

    def test_malformed_scores_are_an_error(self):
        errs = self.errors("@course{bad, course = {HLTH 101}, title = {A Course}, date = {2024-01}, "
                           "scp = {Implementation = 4.5/5}, enrolment = {~40}}\n")
        self.assertEqual(len(errs), 2)
        self.assertTrue(any("enrolment" in m for _, m in errs))
        self.assertTrue(any("scp 'Implementation = 4.5/5'" in m for _, m in errs))


if __name__ == "__main__":
    unittest.main()


class SupervisedTrainees(unittest.TestCase):
    """supervision.bib students count as trainees; a respelled one is flagged."""

    ROSTER = [
        {"name": "Liudmila Tahai", "variants": ["Tahai, Liudmila"]},
        {"name": "Robert P. Gauthier", "variants": ["Robert Gauthier"]},
    ]

    def supervision(self, *authors):
        d = Path(tempfile.mkdtemp())
        p = d / "supervision.bib"
        p.write_text("".join(f"@supervision{{s{i}, author = {{{a}}}, degree = {{PhD}}, status = {{In progress}}}}\n"
                             for i, a in enumerate(authors)), encoding="utf-8")
        return cvlib.parse_bib(p)

    def test_a_new_student_joins_the_roster(self):
        roster, drift = cvlib.add_supervised(self.ROSTER, self.supervision("Liaqat, Taha"))
        self.assertEqual(drift, [])
        self.assertIn("taha", {cvlib.norm(n) for n in [cvlib.name_parts(t["name"])[1] for t in roster]})
        self.assertIn(cvlib.norm("liaqattaha"), cvlib.roster_index(roster))

    def test_a_student_already_named_is_not_added_twice(self):
        roster, drift = cvlib.add_supervised(self.ROSTER, self.supervision("Gauthier, Robert"))
        self.assertEqual((len(roster), drift), (2, []))

    def test_a_respelled_student_is_flagged(self):
        _, drift = cvlib.add_supervised(self.ROSTER, self.supervision("Tahai, Mila"))
        self.assertEqual(drift, [("s0", "Mila Tahai", "Liudmila Tahai")])

    def test_the_real_files_are_consistent(self):
        roster = cvlib.load_roster(cvlib.ROOT / "data" / "trainees.yaml")
        _, drift = cvlib.add_supervised(roster, cvlib.parse_bib(cvlib.ROOT / "supervision.bib"))
        self.assertEqual(drift, [])


class TitlesAndNames(unittest.TestCase):
    """E-myname (one written form of my name) and W-titlecase (unbraced capitalised title words)."""
    BIB = r"""
@inproceedings{surname2020, title = {A}, year = {2020}, doi = {10.1/a},
  author = {Smith, Ann and \textbf{Wallace, James R.}}}
@inproceedings{good2020, title = {{LLM} Support for Co-Located {AttentionGo} and Edit{B}lind}, year = {2020},
  doi = {10.1/b}, author = {Wallace Jarvis*, Laura and \textbf{James R. Wallace}{\dag}}}
@inproceedings{caps2020, title = {Using LLMs for COVID-19 in {HCI} {\texttimes} Health}, year = {2020},
  doi = {10.1/c}, author = {\textbf{James R. Wallace}}}
"""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "data").mkdir()
        shutil.copy(cvlib.ROOT / "data" / "trainees.yaml", self.root / "data" / "trainees.yaml")
        for name in check_cv.RECORD_FILES:
            (self.root / name).write_text("", encoding="utf-8")
        (self.root / "main.tex").write_text(
            "\\DeclareBibliographyCategory{conference}\n"
            "\\addtocategory{conference}{surname2020, good2020, caps2020}\n", encoding="utf-8")
        (self.root / "scholar.bib").write_text(self.BIB, encoding="utf-8")
        self.saved = check_cv.ROOT
        check_cv.ROOT = self.root

    def tearDown(self):
        check_cv.ROOT = self.saved
        shutil.rmtree(self.root)

    def keys(self, code):
        r = check_cv.run()
        return {x["key"] for x in r["errors"] + r["warnings"] if x["code"] == code}

    def test_surname_first_name_is_an_error(self):
        self.assertEqual(self.keys("E-myname"), {"surname2020"})

    def test_unbraced_acronyms_warn_and_braced_ones_do_not(self):
        self.assertEqual(self.keys("W-titlecase"), {"caps2020"})

    def test_word_finder(self):
        self.assertEqual(check_cv.unbraced_capitalised_words(r"Using LLMs for COVID-19 in {HCI} {\texttimes} Health"),
                         ["LLMs", "COVID"])
        self.assertEqual(check_cv.unbraced_capitalised_words(r"{LLM} Co-Located Edit{B}lind 3d"), [])
        self.assertEqual(check_cv.unbraced_capitalised_words("Freehand 3D Interaction"), ["3D"])


class CanadianSpellingTest(unittest.TestCase):
    """W-spelling: Canadian and only Canadian English in Jim's prose (Jim, 2026-11-25)."""

    def words(self, text):
        return [(w, fix) for _, w, fix in check_cv.american_spellings(check_cv.tex_prose(text))]

    def test_american_spellings_are_found_with_the_canadian_form(self):
        self.assertEqual(self.words("Best Paper Honorable Mention; the Games Center; PhD Defense Chair"),
                         [("Honorable", "Honourable"), ("Center", "Centre"), ("Defense", "Defence")])
        self.assertEqual(self.words("we analysed and recognised behavior"),
                         [("analysed", "analyzed"), ("recognised", "recognized"), ("behavior", "behaviour")])
        self.assertEqual(self.words("modeling, labeled, enrollment, gray, catalog, programme"),
                         [("modeling", "modelling"), ("labeled", "labelled"), ("enrollment", "enrolment"),
                          ("gray", "grey"), ("catalog", "catalogue"), ("programme", "program")])

    def test_canadian_spellings_pass(self):
        self.assertEqual(self.words("Honourable Mention, behaviour, centre, defence, modelling, labelled, "
                                    "enrolment, grey, catalogue, program, recognized, analyzed, practise, "
                                    "honorary, rigorous, humorous, analyses, analysis"), [])

    def test_what_is_not_prose_is_skipped(self):
        tex = (r"\begin{center}\centering %  honor in a comment" "\n"
               r"\emph{Computers in Human Behavior} and \emph{Behavior Research Methods}" "\n"
               r"``a color quoted from the Addendum'' \url{https://x.org/honorable-mention}" "\n"
               r"\extlink{https://chi.acm.org/best-paper-and-honorable-mention}{(CHI Awards)}")
        self.assertEqual(self.words(tex), [])

    def test_offsets_keep_their_line(self):
        prose = check_cv.tex_prose("line one\n% favor\nline three has a color\n")
        (off, word, _), = check_cv.american_spellings(prose)
        self.assertEqual((word, prose.count("\n", 0, off) + 1), ("color", 3))

    def test_check_reads_the_prose_files_and_jims_fields(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        (root / "letters").mkdir()
        (root / "data").mkdir()
        (root / "main.tex").write_text("Fine text.\nThe Note on Service: a labor of love.\n", encoding="utf-8")
        (root / "letters" / "cover.tex").write_text(r"\emph{Behavior}. Organised well." "\n", encoding="utf-8")
        (root / "awards.bib").write_text(
            "@award{a2020, title = {Best Paper Honorable Mention}, date = {2020}}\n", encoding="utf-8")
        awards = cvlib.parse_bib(root / "awards.bib")
        (root / "supervision.bib").write_text(
            "@supervision{s2020, author = {Doe, Jo}, title = {Modeling Arm Fatigue}, position = {Labor analyst}}\n",
            encoding="utf-8")
        supervision = cvlib.parse_bib(root / "supervision.bib")
        out = []
        check_cv.check_spelling({"awards.bib": awards.entries, "supervision.bib": supervision.entries},
                                lambda code, msg, key=None: out.append(msg), root)
        joined = "\n".join(out)
        self.assertIn("main.tex:2: 'labor'", joined)
        self.assertIn("cover.tex:1: 'Organised'", joined)
        self.assertIn("'a2020' title: 'Honorable'", joined)
        self.assertIn("'s2020' position: 'Labor'", joined)
        self.assertNotIn("Modeling", joined)  # thesis titles keep their own spelling
        self.assertNotIn("'Behavior'", joined)  # \emph{} titles of works are skipped
        self.assertEqual(len(out), 4)
