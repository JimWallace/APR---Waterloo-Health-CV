#!/usr/bin/env python3
"""Deterministic checks on scholar.bib and the category lists in main.tex.

Errors change what the PDF says (a paper silently dropped or printed twice)
and fail CI. Warnings are worth a look but do not block a merge.

    python3 scripts/check_cv.py            # human-readable report
    python3 scripts/check_cv.py --json     # machine-readable, for Claude
    python3 scripts/check_cv.py --keys k1,k2   # only report on these entries
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from cvlib import (APR_CATEGORIES, KNOWN_TYPES, PRINTED_CATEGORIES, ROOT,  # noqa: E402
                   clean_name, is_marked_trainee, load_roster, mark_in_given_name,
                   name_parts, norm, parse_bib, parse_categories, review_period,
                   roster_index)

SELF = "wallace"  # family name of the CV owner, excluded from trainee checks


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
    roster = load_roster(ROOT / "data" / "trainees.yaml")
    ridx = roster_index(roster)
    rparts = {}
    for t in roster:
        for v in [t["name"]] + list(t.get("variants", []) or []):
            f, g = name_parts(v)
            rparts[(norm(f), norm(g))] = t["name"]
    by_key = bib.by_key()

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
            if k not in by_key:
                warn("W-nokey", f"\\addtocategory{{{c}}} lists '{k}', which is not in scholar.bib "
                     "(stale key, or a missing entry)", k)
        for k, n in Counter(ks).items():
            if n > 1:
                warn("W-repeat", f"'{k}' is listed {n} times in \\addtocategory{{{c}}}", k)
    unknown = set(cats) - set(PRINTED_CATEGORIES) - set(APR_CATEGORIES) - {"workshops", "thesis"}
    for c in sorted(unknown):
        warn("W-cat", f"category '{c}' is not printed or used for APR colours")

    # W: entries that never print
    for key in by_key:
        if key not in printed_in:
            warn("W-unprinted", f"'{key}' is in scholar.bib but in no printed category, so it does not appear", key)

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

    # W: missing DOI on refereed work since 2010
    for key, cs in printed_in.items():
        if key in by_key and set(cs) & {"journal", "conference"}:
            e = by_key[key][0]
            if (e.year or 0) >= 2010 and "doi" not in e.fields:
                warn("W-nodoi", f"'{key}' ({e.year}) has no DOI, so it cannot be checked automatically", key)

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
                        " (not in data/trainees.yaml: a new trainee, or not a trainee?)"
                    warn("W-roster", f"'{e.key}': trainee '{clean_name(a)}'{hint}", e.key)

    # APR: review-period entries with trainees should also be teaching (apralsoteaching)
    if period:
        lo, hi = period
        also = set(cats.get("apralsoteaching", [])) | set(cats.get("aprteaching", []))
        include = set(cats.get("aprinclude", []))  # treated as dated in the review period
        excluded = set(cats.get("aprnone", []))
        for key, cs in printed_in.items():
            if key not in by_key or key in excluded:
                continue
            e = by_key[key][0]
            in_period = key in include or (e.year is not None and lo <= e.year <= hi)
            if not in_period:
                continue
            has_trainee = any(is_marked_trainee(a) for a in e.authors)
            if has_trainee and key not in also:
                warn("W-aprteach", f"'{key}' ({e.year}) has a trainee author but is not in apralsoteaching", key)
        for key in cats.get("apralsoteaching", []):
            if key in by_key and not any(is_marked_trainee(a) for a in by_key[key][0].authors):
                warn("W-aprteach", f"'{key}' is in apralsoteaching but no author is marked * "
                     "(fine for talks where a trainee presented; check)", key)

    return {
        "entries": len(bib.entries),
        "review_period": period,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--keys", help="comma-separated keys to report on")
    args = ap.parse_args()
    only = {k.strip() for k in args.keys.split(",")} if args.keys else None
    res = run(only)
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
        out = "\n".join(lines)
        print(out)
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(out + "\n")
    return 1 if res["errors"] else 0


def _group(items):
    order: dict[str, list] = {}
    for i in items:
        order.setdefault(i["code"], []).append(i)
    return order.items()


if __name__ == "__main__":
    sys.exit(main())
