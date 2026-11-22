#!/usr/bin/env python3
"""Deterministic checks on scholar.bib, grants.bib, supervision.bib, awards.bib, service.bib,
activities.bib, courses.bib, committees.bib and the category lists in main.tex.

Errors change what the PDF says (a paper silently dropped or printed twice)
and fail CI. Warnings are worth a look; the ones accepted so far are listed in
scripts/warnings-baseline.txt, and a warning not listed there also fails, as
does a listed one that no longer occurs (see scripts/warning_ratchet.py).

    python3 scripts/check_cv.py            # human-readable report
    python3 scripts/check_cv.py --json     # machine-readable, for Claude
    python3 scripts/check_cv.py --keys k1,k2   # only report on these entries
    python3 scripts/check_cv.py --prune-baseline   # drop baseline lines that no longer occur
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from cvlib import (APR_CATEGORIES, KNOWN_TYPES, PRINTED_CATEGORIES, ROOT, add_supervised,  # noqa: E402
                   clean_name, is_marked_trainee, load_roster, mark_in_given_name,
                   name_parts, norm, parse_bib, parse_categories, review_period,
                   roster_index)
from warning_ratchet import (BASELINE_REL, check_cv_line, compare, read_baseline,  # noqa: E402
                             write_baseline)

SELF = "wallace"  # family name of the CV owner, excluded from trainee checks
OWNER = "James R. Wallace"  # how the owner's name is written, always inside \textbf


def unbraced_capitalised_words(title: str) -> list[str]:
    """Words outside braces with a capital after their first letter (LLM, AttentionGo, 3D).

    Sentence casing lowers them when the title prints. LaTeX commands are skipped; hyphenated
    words are split, so Co-Located is fine but COVID-19 is caught.
    """
    words, word, depth, i = [], "", 0, 0
    while i < len(title):
        c = title[i]
        if c == "\\":
            m = re.match(r"\\[A-Za-z]+|\\.", title[i:])
            i += len(m.group(0)) if m else 1
            if word:
                words.append(word)
                word = ""
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if depth == 0 and c.isalnum():
            word += c
        else:
            if word:
                words.append(word)
            word = ""
        i += 1
    if word:
        words.append(word)
    return [w for w in words if any(ch.isupper() for ch in w[1:])]
UNPRINTED = "unprinted"  # main.tex category for entries kept in scholar.bib on purpose but not printed


def run(only: set[str] | None = None) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []

    def err(code, msg, key=None):
        if only is None or key is None or key in only:
            errors.append({"code": code, "key": key, "msg": msg})

    def warn(code, msg, key=None):
        if only is None or key is None or key in only:
            warnings.append({"code": code, "key": key, "msg": msg})

    bib = parse_bib(ROOT / "scholar.bib")
    for e in bib.errors:
        err("E-syntax", e)
    cats = parse_categories(ROOT / "main.tex")
    period = review_period(ROOT / "main.tex")
    # Trainees: data/trainees.yaml plus every student in supervision.bib.
    roster, drift = add_supervised(load_roster(ROOT / "data" / "trainees.yaml"),
                                   parse_bib(ROOT / "supervision.bib"))
    for key, student, near in drift:
        warn("W-trainee", f"supervision.bib: '{key}' is '{student}', but data/trainees.yaml has "
             f"'{near}': the same person? Add the spelling to that entry's variants, or tell the "
             "two apart", key)
    ridx = roster_index(roster)
    rparts = {}
    for t in roster:
        for v in [t["name"]] + list(t.get("variants", []) or []):
            f, g = name_parts(v)
            rparts[(norm(f), norm(g))] = t["name"]
    by_key = bib.by_key()

    # Grants and supervision records (grants.bib, supervision.bib)
    records = {}
    for name in RECORD_FILES:
        rb = parse_bib(ROOT / name)
        for e in rb.errors:
            err("E-syntax", e)
        records[name] = rb
    main_src = (ROOT / "main.tex").read_text(encoding="utf-8")
    check_records(records, main_src, err, warn)
    check_awards(records["awards.bib"], bib, err, main_src)
    check_software(cats, by_key, err, warn)
    check_impact(cats, by_key, err, warn)
    record_keys = {e.key for rb in records.values() for e in rb.entries}
    all_keys = Counter(e.key for e in bib.entries)
    for rb in records.values():
        all_keys.update(e.key for e in rb.entries)
    for key, n in all_keys.items():
        if n > 1 and len(by_key.get(key, [])) < 2:
            err("E-dupkey", f"key '{key}' is used in more than one .bib file; biber keeps only the first", key)

    # E1 entry types
    for e in bib.entries:
        if e.type not in KNOWN_TYPES:
            err("E-type", f"scholar.bib:{e.line}: @{e.type}{{{e.key}}} is not a biblatex entry type "
                "(typo?), so it will not print as intended", e.key)

    # E2 duplicate keys: biber keeps the first and silently drops the rest
    for key, es in by_key.items():
        if len(es) > 1:
            titles = "; ".join(f"line {x.line}: {x.fields.get('title', '?')[:70]}" for x in es)
            err("E-dupkey", f"key '{key}' is defined {len(es)} times; only the first prints ({titles})", key)

    # E3 entries printed under more than one heading
    printed_in: dict[str, list[str]] = {}
    for c in PRINTED_CATEGORIES:
        for k in dict.fromkeys(cats.get(c, [])):
            printed_in.setdefault(k, []).append(c)
    for k, cs in printed_in.items():
        if len(cs) > 1:
            err("E-multicat", f"'{k}' is in {', '.join(cs)}, so it prints {len(cs)} times", k)

    # W: category keys with no bib entry; repeats inside one list
    for c, ks in cats.items():
        for k in ks:
            if k not in by_key and k not in record_keys:
                warn("W-nokey", f"\\addtocategory{{{c}}} lists '{k}', which is not in scholar.bib "
                     "(stale key, or a missing entry)", k)
        for k, n in Counter(ks).items():
            if n > 1:
                warn("W-repeat", f"'{k}' is listed {n} times in \\addtocategory{{{c}}}", k)
    unknown = set(cats) - set(PRINTED_CATEGORIES) - set(APR_CATEGORIES) - {"workshops", "thesis", UNPRINTED, "aprnoteaching"}
    for c in sorted(unknown):
        warn("W-cat", f"category '{c}' is not printed or used for APR colours")

    # W: entries that never print. Jim records a deliberate "keep in the .bib,
    # don't print" decision by listing the key in \addtocategory{unprinted}.
    kept_unprinted = set(cats.get(UNPRINTED, []))
    for key in by_key:
        if key not in printed_in and key not in kept_unprinted:
            warn("W-unprinted", f"'{key}' is in scholar.bib but in no printed category, so it does not appear", key)
    for key in sorted(kept_unprinted & set(printed_in)):
        warn("W-unprinted", f"'{key}' is in \\addtocategory{{{UNPRINTED}}} but also in "
             f"{', '.join(printed_in[key])}, so it prints; take it out of one", key)

    # W: entry type vs heading
    for key, cs in printed_in.items():
        if key not in by_key:
            continue
        t = by_key[key][0].type
        if "journal" in cs and t in {"inproceedings", "conference"}:
            warn("W-typecat", f"'{key}' is @{t} but listed under Refereed Journals", key)
        if "conference" in cs and t == "article" and "journal" not in by_key[key][0].fields \
                and "journaltitle" not in by_key[key][0].fields:
            pass  # @article with a journal field under conference is how PACM papers are often typed

    # W: missing DOI on refereed work since 2010. `nodoi = {reason}` on an entry
    # records that the work has no DOI (e.g. a poster with no proceedings).
    for key, cs in printed_in.items():
        if key in by_key and set(cs) & {"journal", "conference", "abstracts"}:
            e = by_key[key][0]
            if (e.year or 0) >= 2010 and "doi" not in e.fields \
                    and "nodoi" not in e.fields \
                    and not any(s in e.fields.get("note", "").lower() for s in ("in press", "to appear")):  # no DOI yet, by convention
                warn("W-nodoi", f"'{key}' ({e.year}) has no DOI, so it cannot be checked automatically", key)
    for e in bib.entries:
        if "nodoi" in e.fields and not e.fields["nodoi"].strip():
            warn("W-nodoi", f"'{e.key}' has an empty nodoi field; give the reason it has no DOI", e.key)
        elif "nodoi" in e.fields and "doi" in e.fields:
            warn("W-nodoi", f"'{e.key}' has both doi and nodoi; remove nodoi", e.key)

    # Trainee marks
    for e in bib.entries:
        for a in e.authors:
            if not is_marked_trainee(a):
                continue
            if mark_in_given_name(a):
                warn("W-markpos", f"'{e.key}': trainee mark is on the given name in '{clean_name(a)}' "
                     f"(written '{a.strip()}'); with giveninits biber likely drops it. Put * after the family name.", e.key)
            if ridx:
                fam, giv = name_parts(a)
                if norm(fam + giv) not in ridx:
                    near = sorted({c for (f, g), c in rparts.items()
                                   if f == norm(fam) and g[:1] == norm(giv)[:1]})
                    hint = f" (close to roster name '{near[0]}': typo, or add it as a variant)" if near else \
                        " (not in data/trainees.yaml or supervision.bib: a new trainee, or not a trainee?)"
                    warn("W-roster", f"'{e.key}': trainee '{clean_name(a)}'{hint}", e.key)

    # My name: always \textbf{James R. Wallace}. Inside \textbf the whole name is one literal,
    # so a surname-first form ("Wallace, James R.") prints surname-first.
    for e in bib.entries:
        for m in re.finditer(r"\\textbf\{([^{}]*)\}", e.fields.get("author", "")):
            if SELF in m.group(1).lower() and m.group(1).strip() != OWNER:
                err("E-myname", f"'{e.key}': author written \\textbf{{{m.group(1)}}}; "
                    f"use \\textbf{{{OWNER}}}", e.key)

    # Titles are sentence-cased when printed, so a word with a capital after its first letter
    # (an acronym or a name like AttentionGo) prints in lower case unless it is braced.
    for key, cs in printed_in.items():
        if key not in by_key:
            continue
        words = unbraced_capitalised_words(by_key[key][0].fields.get("title", ""))
        if words:
            warn("W-titlecase", f"'{key}': title word(s) {', '.join(sorted(set(words)))} will print in "
                 "lower case; brace them, e.g. {LLM}. (Names with one capital, like Reddit, "
                 "need braces too but can't be detected.)", key)

    # APR: review-period entries with trainees should also be teaching (apralsoteaching)
    if period:
        lo, hi = period
        also = set(cats.get("apralsoteaching", [])) | set(cats.get("aprteaching", []))
        include = set(cats.get("aprinclude", []))  # treated as dated in the review period
        excluded = set(cats.get("aprnone", []))
        # aprnoteaching (main.tex): Jim's decision that a trainee's work is counted in the
        # period but not as teaching (e.g. trainee work from long before it).
        noteach = set(cats.get("aprnoteaching", []))
        for key, cs in printed_in.items():
            if key not in by_key or key in excluded:
                continue
            e = by_key[key][0]
            in_period = key in include or (e.year is not None and lo <= e.year <= hi)
            if not in_period:
                continue
            has_trainee = any(is_marked_trainee(a) for a in e.authors)
            if has_trainee and key not in also and key not in noteach:
                warn("W-aprteach", f"'{key}' ({e.year}) has a trainee author but is not in apralsoteaching", key)
        # An entry whose main colour is service or award (a meetup: service, with
        # mentorship as teaching) is teaching by Jim's decision, not by a trainee.
        chosen = set(cats.get("aprservice", [])) | set(cats.get("apraward", []))
        for key in cats.get("apralsoteaching", []):
            if key in by_key and key not in chosen and not any(is_marked_trainee(a) for a in by_key[key][0].authors):
                warn("W-aprteach", f"'{key}' is in apralsoteaching but no author is marked * "
                     "(fine for talks where a trainee presented; check)", key)

    # Workshops and meetups co-organized at a conference (CLAUDE.md): the note starts
    # "Workshop proposal." or "Meetup.", and that decides the APR colours.
    organized = {
        "Workshop proposal.": ["apralsoservice"],
        "Meetup.": ["aprservice", "apralsoteaching", "apralsoresearch"],
    }
    for e in bib.entries:
        note = (e.fields.get("note") or "").strip()
        for prefix, needed in organized.items():
            if note.startswith(prefix):
                missing = [c for c in needed if e.key not in cats.get(c, [])]
                if missing:
                    warn("W-organized", f"'{e.key}' is a {prefix[:-1].lower()} (note starts "
                         f"'{prefix}') but is not in {', '.join(missing)}", e.key)

    return {
        "entries": len(bib.entries),
        "review_period": period,
        "errors": errors,
        "warnings": warnings,
    }


RECORD_FILES = ["grants.bib", "supervision.bib", "awards.bib", "service.bib", "activities.bib", "courses.bib",
                "committees.bib"]
GRANT_ROLES = {"PI", "Co-PI", "Co-I", "Co-A"}
DATE_RE = re.compile(r"^\d{4}(-\d{2})?(/\d{4}(-\d{2})?)?$")
# Course evaluation scores: Item=score pairs, comma-separated, scores out of 5
SCORES_RE = re.compile(r"^[^=,]*[^=,\s]=[0-5](\.\d+)?(\s*,\s*[^=,]*[^=,\s]=[0-5](\.\d+)?)*$")


def check_records(records: dict, main_tex: str, err, warn) -> None:
    """Grants, supervision, service, courses and committees: fields the template needs, in the
    form it reads."""
    check_committees(records, main_tex, err)
    for e in records["grants.bib"].entries:
        f, where = e.fields, f"grants.bib:{e.line}"
        if e.type != "grant":
            err("E-record", f"{where}: '{e.key}' is @{e.type}; grants.bib holds @grant entries", e.key)
            continue
        for k in ("investigators", "agency", "amount", "date", "title"):
            if not f.get(k):
                err("E-record", f"{where}: grant '{e.key}' has no {k}", e.key)
        inv = [x.strip() for x in re.split(r"\s+and\s+", f.get("investigators", ""))]
        if inv.count("\\me") != 1:
            err("E-record", f"{where}: grant '{e.key}' must list \\me exactly once in investigators", e.key)
        if f.get("role") not in GRANT_ROLES:
            warn("W-record", f"{where}: grant '{e.key}' has role '{f.get('role')}', not one of "
                 f"{', '.join(sorted(GRANT_ROLES))}", e.key)
        if f.get("amount") and not f["amount"].isdigit():
            err("E-record", f"{where}: grant '{e.key}' amount '{f['amount']}' must be digits only "
                "(no $ or commas)", e.key)
        if f.get("date") and not DATE_RE.match(f["date"]):
            err("E-record", f"{where}: grant '{e.key}' date '{f['date']}' should be YYYY or YYYY/YYYY", e.key)
    printed = set(re.findall(r"^[^%\n]*\\printsupervision\{([^}]*)\}", main_tex, re.M))
    for e in records["supervision.bib"].entries:
        f, where = e.fields, f"supervision.bib:{e.line}"
        if e.type != "supervision":
            err("E-record", f"{where}: '{e.key}' is @{e.type}; supervision.bib holds @supervision entries", e.key)
            continue
        if not f.get("author"):
            err("E-record", f"{where}: '{e.key}' has no author (the student)", e.key)
        if f.get("degree") not in printed:
            err("E-record", f"{where}: '{e.key}' has degree '{f.get('degree')}', which no "
                "\\printsupervision in main.tex prints, so it does not appear", e.key)
        if bool(f.get("date")) == bool(f.get("status")):
            err("E-record", f"{where}: '{e.key}' needs exactly one of date (completed) or "
                "status (e.g. In progress)", e.key)
        if f.get("date") and not DATE_RE.match(f["date"]):
            err("E-record", f"{where}: '{e.key}' date '{f['date']}' should be YYYY or YYYY-MM", e.key)
    levels = set(re.findall(r"^[^%\n]*\\printservice\{([^}]*)\}", main_tex, re.M))
    for name in ("service.bib", "activities.bib"):
        for e in records[name].entries:
            f, where = e.fields, f"{name}:{e.line}"
            if e.type != "service":
                err("E-record", f"{where}: '{e.key}' is @{e.type}; {name} holds @service entries", e.key)
                continue
            if not f.get("title"):
                err("E-record", f"{where}: service '{e.key}' has no title", e.key)
            named = [x.strip() for x in f.get("level", "").split(",") if x.strip()]
            if not named:
                err("E-record", f"{where}: service '{e.key}' has no level", e.key)
            for lv in named:
                if lv not in levels:
                    err("E-record", f"{where}: service '{e.key}' has level '{lv}', which no "
                        "\\printservice in main.tex prints, so it does not appear there", e.key)
            if not re.fullmatch(r"\d{4}(/(\d{4})?)?", f.get("date", "")):
                err("E-record", f"{where}: service '{e.key}' date '{f.get('date', '')}' should be YYYY, "
                    "YYYY/YYYY, or YYYY/ for an ongoing role", e.key)

    for e in records["courses.bib"].entries:
        f, where = e.fields, f"courses.bib:{e.line}"
        if e.type != "course":
            err("E-record", f"{where}: '{e.key}' is @{e.type}; courses.bib holds @course entries", e.key)
            continue
        if not f.get("course"):
            err("E-record", f"{where}: course '{e.key}' has no course number", e.key)
        if not re.fullmatch(r"\d{4}-(01|05|09)", f.get("date", "")):
            err("E-record", f"{where}: course '{e.key}' date '{f.get('date', '')}' should be the month "
                "the term starts: YYYY-01 (Winter), YYYY-05 (Spring) or YYYY-09 (Fall)", e.key)
        for k in ("enrolment", "responses"):
            if f.get(k) and not f[k].isdigit():
                err("E-record", f"{where}: course '{e.key}' {k} '{f[k]}' must be digits only", e.key)
        for k in ("scp", "scpaverage"):
            if f.get(k) and not SCORES_RE.match(f[k]):
                err("E-record", f"{where}: course '{e.key}' {k} '{f[k]}' should be Item=score pairs "
                    "out of 5, comma-separated, no spaces around = (Implementation=4.5, Design=4.6)", e.key)

def check_committees(records: dict, main_tex: str, err) -> None:
    """committees.bib: a named committee (author) or a count-only record (count), a degree
    that a \\printcommitteecounts in main.tex counts, and a date the template reads."""
    groups = {}
    for g, degrees in re.findall(r"^[^%\n]*\\cvcommitteegroup\{([^}]*)\}\{([^}]*)\}", main_tex, re.M):
        for d in degrees.split(","):
            groups[d.strip()] = g.strip()
    counted = {g.strip() for call in re.findall(r"^[^%\n]*\\printcommitteecounts\{([^}]*)\}", main_tex, re.M)
               for g in call.split(",")}
    for e in records["committees.bib"].entries:
        f, where = e.fields, f"committees.bib:{e.line}"
        if e.type != "committee":
            err("E-record", f"{where}: '{e.key}' is @{e.type}; committees.bib holds @committee entries", e.key)
            continue
        degree = f.get("degree", "")
        if not degree:
            err("E-record", f"{where}: committee '{e.key}' has no degree", e.key)
        elif groups.get(degree, degree) not in counted:
            err("E-record", f"{where}: committee '{e.key}' has degree '{degree}', which no "
                "\\printcommitteecounts in main.tex counts (add it to a \\cvcommitteegroup?)", e.key)
        if bool(f.get("author")) == bool(f.get("count")):
            err("E-record", f"{where}: committee '{e.key}' needs exactly one of author (a named "
                "committee) or count (the number for a year with no names)", e.key)
        if f.get("count"):
            if not f["count"].isdigit():
                err("E-record", f"{where}: committee '{e.key}' count '{f['count']}' must be digits only", e.key)
            if not re.fullmatch(r"\d{4}", f.get("date", "")):
                err("E-record", f"{where}: count-only committee '{e.key}' date '{f.get('date', '')}' "
                    "should be the year, YYYY", e.key)
        elif not re.fullmatch(r"\d{4}(/(\d{4})?)?", f.get("date", "")):
            err("E-record", f"{where}: committee '{e.key}' date '{f.get('date', '')}' should be the years "
                "served: YYYY, YYYY/YYYY, or YYYY/ while ongoing", e.key)


AWARD_ICONS = {"award", "images/hm.png"}


def check_software(cats: dict, by_key: dict, err, warn) -> None:
    """data/software.yaml names scholar.bib software entries; data/software-stats.tex
    (generated by scripts/software_stats.py) must cover exactly those keys."""
    cfg = ROOT / "data" / "software.yaml"
    if not cfg.exists():
        return
    keys = re.findall(r"^([^\s#:][^:]*):\s*(?:#.*)?$", cfg.read_text(encoding="utf-8"), re.M)
    software = set(cats.get("software", []))
    for k in keys:
        if k not in by_key:
            err("E-software", f"data/software.yaml lists '{k}', which is not in scholar.bib", k)
        elif k not in software:
            warn("W-software", f"data/software.yaml lists '{k}', which is not in \\addtocategory{{software}}", k)
    stats = ROOT / "data" / "software-stats.tex"
    have = re.findall(r"^\\setentrydetail\{([^}]*)\}", stats.read_text(encoding="utf-8"), re.M) \
        if stats.exists() else []
    if set(have) != set(keys):
        warn("W-software", "data/software-stats.tex does not match data/software.yaml; "
             "run python3 scripts/software_stats.py")


def check_impact(cats: dict, by_key: dict, err, warn) -> None:
    """data/impact.tex (hand-maintained deployment lines) names printed scholar.bib
    entries, each once, with a source, and none that another detail file covers:
    \\setentrydetail keeps only the last line for a key."""
    path = ROOT / "data" / "impact.tex"
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    printed = {k for c, ks in cats.items() if c != UNPRINTED for k in ks}
    other = set()
    for name in ("software-stats.tex", "citation-impact.tex"):
        f = ROOT / "data" / name
        if f.exists():
            other |= set(re.findall(r"^\\setentrydetail\{([^}]*)\}", f.read_text(encoding="utf-8"), re.M))
    seen = set()
    for i, line in enumerate(lines):
        m = re.match(r"\\setentrydetail\{([^}]*)\}", line)
        if not m:
            continue
        k = m.group(1)
        if k not in by_key:
            err("E-impact", f"data/impact.tex has a line for '{k}', which is not in scholar.bib", k)
        elif k not in printed:
            warn("W-impact", f"data/impact.tex has a line for '{k}', which is in no printed category", k)
        if k in seen:
            err("E-impact", f"data/impact.tex has more than one line for '{k}'", k)
        if k in other:
            err("E-impact", f"'{k}' has a line in data/impact.tex and in a generated detail file; "
                "only one prints", k)
        seen.add(k)
        j = i - 1
        while j >= 0 and lines[j].startswith("%") and not lines[j].startswith("% Source:"):
            j -= 1
        if j < 0 or not lines[j].startswith("% Source:"):
            warn("W-impact", f"data/impact.tex: the line for '{k}' has no '% Source:' comment above it", k)


def check_awards(awards, bib, err, main_tex: str = "") -> None:
    """awards.bib: well-formed, and in step with the award badges on entries."""
    # \printawards[level] lists: when main.tex prints awards by level (and has no plain
    # \printawards), an award whose level no list names would silently not print.
    award_levels = set(re.findall(r"^[^%\n]*\\printawards\[([^\]]*)\]", main_tex, re.M))
    plain = re.search(r"^[^%\n]*\\printawards(?!\[)", main_tex, re.M)
    pubs = {e.key: e for e in bib.entries}
    badged = {k for k, e in pubs.items() if e.fields.get("icon") in AWARD_ICONS}
    named = {}
    for e in awards.entries:
        f, where = e.fields, f"awards.bib:{e.line}"
        if e.type != "award":
            err("E-record", f"{where}: '{e.key}' is @{e.type}; awards.bib holds @award entries", e.key)
            continue
        if not f.get("title"):
            err("E-record", f"{where}: award '{e.key}' has no title", e.key)
        if not re.fullmatch(r"\d{4}", f.get("date", "")):
            err("E-record", f"{where}: award '{e.key}' date '{f.get('date', '')}' should be a year (YYYY)", e.key)
        if f.get("count") and not f["count"].isdigit():
            err("E-record", f"{where}: award '{e.key}' count '{f['count']}' must be a whole number", e.key)
        if award_levels and not plain:
            named_levels = [x.strip() for x in f.get("level", "").split(",") if x.strip()]
            if not named_levels:
                err("E-record", f"{where}: award '{e.key}' has no level, so no \\printawards[level] "
                    f"list prints it (main.tex prints {', '.join(sorted(award_levels))})", e.key)
            for lv in named_levels:
                if lv not in award_levels:
                    err("E-record", f"{where}: award '{e.key}' has level '{lv}', which no "
                        "\\printawards[level] in main.tex prints", e.key)
        w = f.get("work")
        if w:
            named[w] = e.key
            if w not in pubs:
                err("E-award", f"{where}: award '{e.key}' is for work '{w}', which is not in scholar.bib", e.key)
            elif w not in badged:
                err("E-award", f"{where}: award '{e.key}' is for '{w}', which has no icon = {{award}}, "
                    "so the award badge is missing from that entry", e.key)
    for k in sorted(badged - set(named)):
        err("E-award", f"'{k}' carries the award badge but no @award in awards.bib names it "
            "(work = {" + k + "}), so it is missing from ACADEMIC AWARDS AND DISTINCTIONS", k)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--keys", help="comma-separated keys to report on")
    ap.add_argument("--prune-baseline", action="store_true",
                    help=f"remove check_cv lines from {BASELINE_REL} that no longer occur")
    args = ap.parse_args()
    only = {k.strip() for k in args.keys.split(",")} if args.keys else None
    res = run(only)
    current = Counter(check_cv_line(w) for w in res["warnings"])
    baseline = read_baseline()
    new, stale = compare(current, baseline, {"check_cv"})
    if only is not None:
        stale = []  # a partial run cannot tell which baseline lines are fixed
    if args.prune_baseline and only is None:
        write_baseline(baseline - Counter(stale))
        print(f"Removed {len(stale)} stale line(s) from {BASELINE_REL}.")
        stale = []
    res["new_warnings"], res["stale_baseline"] = new, stale
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        lines = [f"## CV check: {len(res['errors'])} error(s), {len(res['warnings'])} warning(s) "
                 f"across {res['entries']} bib entries", ""]
        for title, items in (("Errors (these change what the PDF says)", res["errors"]),
                             ("Warnings", res["warnings"])):
            if items:
                lines.append(f"### {title}")
                for codes, grp in _group(items):
                    lines.append(f"- **{codes}**")
                    lines += [f"  - {i['msg']}" for i in grp]
                lines.append("")
        if new:
            lines += [f"### New warnings: not in {BASELINE_REL}, so CI fails",
                      "Fix the cause. Adding a line to the baseline instead means Jim has to "
                      "merge the PR by hand.", *[f"- `{n}`" for n in new], ""]
        if stale:
            lines += [f"### Fixed warnings still in {BASELINE_REL}, so CI fails",
                      "Run `python3 scripts/check_cv.py --prune-baseline` to delete them.",
                      *[f"- `{n}`" for n in stale], ""]
        out = "\n".join(lines)
        print(out)
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(out + "\n")
    return 1 if res["errors"] or new or stale else 0


def _group(items):
    order: dict[str, list] = {}
    for i in items:
        order.setdefault(i["code"], []).append(i)
    return order.items()


if __name__ == "__main__":
    sys.exit(main())
