#!/usr/bin/env python3
"""Development stats for the software listed in data/software.yaml.

Clones each repository (full history, file contents of the latest commit only)
and writes data/software-stats.tex: one \\setentrydetail{key}{...} line per
entry, printed under the entry in both PDFs.

    python3 scripts/software_stats.py                 # clone into a temporary directory
    python3 scripts/software_stats.py --repos-dir D   # reuse (and fetch) clones in D
    python3 scripts/software_stats.py --json          # also print the numbers

What is counted, so the numbers can be explained to a reader:
  releases  tags matching the entry's release_tags (default: every tag)
  commits   commits on the default branch, less those by exclude_authors
  code      non-blank lines in tracked source files (CODE_EXTENSIONS) in the
            latest commit, less exclude_paths; files matching test_paths count
            as automated tests instead
  period    month of the first and the latest counted commit
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "software.yaml"
OUT_TEX = ROOT / "data" / "software-stats.tex"

CODE_EXTENSIONS = {
    ".swift", ".py", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".rb", ".r", ".R", ".sh", ".html", ".css", ".scss", ".sql",
}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout


def clone(url: str, dest: Path) -> None:
    env = {**os.environ, "GIT_LFS_SKIP_SMUDGE": "1", "GIT_TERMINAL_PROMPT": "0"}
    if (dest / ".git").exists():
        subprocess.run(["git", "-C", str(dest), "fetch", "-q", "--tags", "--force", "origin"],
                       check=True, env=env)
        subprocess.run(["git", "-C", str(dest), "reset", "-q", "--hard", "origin/HEAD"],
                       check=True, env=env)
    else:
        # blob:none: the whole history, but only the latest commit's file contents
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", url, str(dest)],
                       check=True, env=env)


def load_config() -> dict:
    import yaml
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}


def round_lines(n: int) -> int:
    if n >= 10000:
        return round(n, -3)
    if n >= 1000:
        return round(n, -2)
    return n


def measure(repo: Path, cfg: dict) -> dict:
    excluded = set(cfg.get("exclude_authors") or [])
    commits = []  # (YYYY-MM) of each counted commit
    for line in git(repo, "log", "--format=%an\t%ad", "--date=format:%Y-%m").splitlines():
        author, month = line.split("\t")
        if author not in excluded:
            commits.append(month)
    if not commits:
        raise SystemExit(f"{repo.name}: no commits left after exclude_authors")

    tag_re = re.compile(cfg.get("release_tags") or ".")
    releases = []
    for line in git(repo, "for-each-ref", "refs/tags",
                    "--format=%(refname:short)\t%(creatordate:format:%Y-%m)").splitlines():
        tag, month = line.split("\t")
        if tag_re.search(tag):
            releases.append(month)

    excludes = [f":(exclude){p}" for p in cfg.get("exclude_paths") or []]
    test_re = re.compile(cfg["test_paths"]) if cfg.get("test_paths") else None
    code = tests = 0
    for path in git(repo, "ls-files", "-z", "--", ".", *excludes).split("\0"):
        if not path or Path(path).suffix not in CODE_EXTENSIONS:
            continue
        f = repo / path
        if f.is_symlink() or not f.is_file():
            continue
        n = sum(1 for ln in f.read_bytes().splitlines() if ln.strip())
        if test_re and test_re.search(path):
            tests += n
        else:
            code += n

    return {"commits": len(commits), "releases": len(releases), "code": code, "tests": tests,
            "first": min(commits), "last": max(commits)}


def month_name(ym: str) -> tuple[str, str]:
    y, m = ym.split("-")
    return MONTHS[int(m) - 1], y


def period(first: str, last: str) -> str:
    (m1, y1), (m2, y2) = month_name(first), month_name(last)
    if first == last:
        return f"{m1} {y1}"
    if y1 == y2:
        return f"{m1} -- {m2} {y2}"
    return f"{m1} {y1} -- {m2} {y2}"


def plural(n: int, word: str) -> str:
    return f"{n:,} {word}{'' if n == 1 else 's'}"


def sentence(s: dict) -> str:
    parts = []
    if s["releases"]:
        parts.append(plural(s["releases"], "release"))
    parts.append(plural(s["commits"], "commit"))
    parts.append(f"{round_lines(s['code']):,} lines of code")
    if s["tests"]:
        parts.append(f"{round_lines(s['tests']):,} lines of automated tests")
    listed = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return f"Developed {period(s['first'], s['last'])}: {listed}."


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repos-dir", type=Path, help="keep clones here and reuse them")
    ap.add_argument("--json", action="store_true", help="print the numbers as JSON")
    args = ap.parse_args()

    config = load_config()
    tmp = None
    repos_dir = args.repos_dir
    if repos_dir is None:
        tmp = tempfile.TemporaryDirectory()
        repos_dir = Path(tmp.name)
    repos_dir.mkdir(parents=True, exist_ok=True)

    lines = ["% Generated by scripts/software_stats.py from data/software.yaml; do not edit.",
             "% Printed under each entry in PUBLICATIONS > Software (\\setentrydetail, template)."]
    report = {}
    for key, cfg in config.items():
        dest = repos_dir / key
        clone(cfg["repo"], dest)
        s = measure(dest, cfg)
        lines.append(f"\\setentrydetail{{{key}}}{{{sentence(s)}}}")
        report[key] = {k: s[k] for k in ("releases", "commits", "code", "tests", "first", "last")}
    OUT_TEX.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if tmp:
        tmp.cleanup()
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        for key, r in report.items():
            print(f"{key}: {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
