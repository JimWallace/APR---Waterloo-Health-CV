#!/usr/bin/env python3
"""Report on Jim's grant applications from grants.bib, the record of every application
(funded, pending, declined or withdrawn) since November 2026.

  python3 scripts/grant_report.py                    every application with a submission date
  python3 scripts/grant_report.py --period 2025 2026 applications that went in during 2025-26
  python3 scripts/grant_report.py --all              also funded grants with no submission date
  python3 scripts/grant_report.py --missing          applications still missing details

A funded grant has no status; an application awaiting a decision has status = {Submitted};
one that was not funded has {Declined}; {Withdrawn} if it was pulled. `submitted` is when it
went in and `decided` when the decision came (YYYY, YYYY-MM or YYYY-MM-DD). `amount` is the
amount awarded for a funded grant and the amount requested otherwise. Prints Markdown.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cvlib  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUTCOME = {None: "Funded", "Submitted": "Pending", "Declined": "Declined", "Withdrawn": "Withdrawn"}
DETAILS = ("title", "amount", "date", "role")


def applications(bib_path: Path, include_all: bool) -> list[dict]:
    rows = []
    for e in cvlib.parse_bib(bib_path).entries:
        if e.type != "grant":
            continue
        f = e.fields
        status = f.get("status")
        if not f.get("submitted") and not (include_all and status is None):
            continue
        year = (f.get("submitted") or f.get("date") or "")[:4]
        rows.append({
            "key": e.key, "year": year, "submitted": f.get("submitted", ""),
            "decided": f.get("decided", ""), "outcome": OUTCOME.get(status, status),
            "agency": f.get("agency", ""), "title": f.get("title", ""), "role": f.get("role", ""),
            "amount": int(f["amount"]) if f.get("amount", "").isdigit() else None,
            "tenure": f.get("date", ""), "status": status,
            "missing": [k for k in DETAILS if not f.get(k)]
                       + (["decided"] if status in ("Declined", "Withdrawn") and not f.get("decided") else []),
        })
    return sorted(rows, key=lambda r: (r["submitted"] or r["year"], r["key"]), reverse=True)


def money(n: int | None) -> str:
    return f"${n:,}" if n is not None else ""


def cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\\me", "").replace("{", "").replace("}", "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--period", nargs=2, type=int, metavar=("FROM", "TO"),
                    help="only applications that went in during these years (inclusive)")
    ap.add_argument("--all", action="store_true",
                    help="also list funded grants that have no submission date")
    ap.add_argument("--missing", action="store_true",
                    help="list applications still missing details, for Jim")
    ap.add_argument("--bib", type=Path, default=ROOT / "grants.bib")
    args = ap.parse_args()

    rows = applications(args.bib, args.all)
    if args.period:
        lo, hi = args.period
        rows = [r for r in rows if r["year"].isdigit() and lo <= int(r["year"]) <= hi]

    if args.missing:
        todo = [r for r in rows if r["status"] is not None and r["missing"]]
        print(f"## Applications missing details ({len(todo)})\n")
        for r in todo:
            print(f"- `{r['key']}` ({r['outcome']}, {r['agency']}, went in {r['submitted']}): "
                  f"{', '.join(r['missing'])}")
        return 0

    span = f" ({args.period[0]}-{args.period[1]})" if args.period else ""
    print(f"## Grant applications{span}\n")
    counts = Counter(r["outcome"] for r in rows)
    decided = counts["Funded"] + counts["Declined"]
    print(f"{len(rows)} applications: {counts['Funded']} funded, {counts['Declined']} declined, "
          f"{counts['Pending']} pending, {counts['Withdrawn']} withdrawn."
          + (f" Funded {counts['Funded']} of {decided} decided ({100 * counts['Funded'] / decided:.0f}%)."
             if decided else ""))
    awarded = sum(r["amount"] or 0 for r in rows if r["outcome"] == "Funded")
    print(f"Awarded: {money(awarded)}.\n")
    print("| Went in | Agency and program | Title | Role | Amount | Tenure | Outcome | Decided |")
    print("|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['submitted'] or r['year']} | {cell(r['agency'])} | {cell(r['title'])} | {r['role']} "
              f"| {money(r['amount'])} | {r['tenure'].replace('/', '–')} | {r['outcome']} | {r['decided']} |")
    print("\nAmount: awarded if funded, otherwise requested.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
