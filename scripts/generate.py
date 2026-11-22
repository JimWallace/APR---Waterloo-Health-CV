#!/usr/bin/env python3
"""Rerun every offline generator: the one command to run after changing the record.

    python3 scripts/generate.py            # rewrite every generated file
    python3 scripts/generate.py --check    # exit 1, naming them, if any is out of step

Each generator reads only files in this repository, so the output is the same on every
machine and CI can check it (check_cv.py calls check() and warns W-generated):

    data/venue-profile.tex    scripts/venue_profile.py   data/venues.yaml, scholar.bib, main.tex
    data/funders.tex          scripts/funder_profile.py  data/funders.yaml, grants.bib
    data/cv-numbers.tex       scripts/cv_numbers.py      all of the above, data/citation-impact.yaml
    data/citation-impact.tex  scripts/citation_impact.py data/citation-impact.yaml

Left out: scripts/software_stats.py (clones repositories over the network; the weekly run
calls it) and importing a SciVal export (python3 scripts/citation_impact.py EXPORT.csv,
which Jim supplies). The committee counts need no generator: the template counts
committees.bib when the PDF is built. Never edit a generated file by hand.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import citation_impact  # noqa: E402
import cv_numbers  # noqa: E402
import funder_profile  # noqa: E402
import venue_profile  # noqa: E402
from cvlib import ROOT  # noqa: E402

# (module, input it needs to run at all); each module has OUT and build(root).
GENERATORS = [
    (venue_profile, Path("data") / "venues.yaml"),
    (funder_profile, Path("data") / "funders.yaml"),
    (cv_numbers, None),
    (citation_impact, Path("data") / "citation-impact.yaml"),
]


def results(root: Path = ROOT):
    """[(output path, text or None, problems)] for each generator whose input exists."""
    out = []
    for mod, needs in GENERATORS:
        if needs is not None and not (root / needs).exists():
            continue
        text, problems = mod.build(root)
        out.append((mod.OUT, text if not problems else None, problems))
    return out


def check(root: Path = ROOT) -> tuple[list[str], list[str]]:
    """(problems in the inputs, generated files that are out of step)."""
    problems, stale = [], []
    for path, text, probs in results(root):
        problems += [p for p in probs if p not in problems]
        if text is not None:
            f = root / path
            if not f.exists() or f.read_text(encoding="utf-8") != text:
                stale.append(str(path))
    return problems, stale


def main(argv: list[str]) -> int:
    if "--check" in argv:
        problems, stale = check()
        for p in problems:
            print(p, file=sys.stderr)
        for s in stale:
            print(f"{s} is out of step; run python3 scripts/generate.py", file=sys.stderr)
        return 1 if problems or stale else 0
    status = 0
    for path, text, problems in results():
        if problems:
            print(f"{path}: not written:\n  " + "\n  ".join(problems), file=sys.stderr)
            status = 1
            continue
        f = ROOT / path
        old = f.read_text(encoding="utf-8") if f.exists() else None
        if old != text:
            f.write_text(text, encoding="utf-8")
        print(f"{path}: {'unchanged' if old == text else 'written'}")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
