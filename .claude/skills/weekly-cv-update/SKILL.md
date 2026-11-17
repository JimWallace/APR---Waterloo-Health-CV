---
name: weekly-cv-update
description: Weekly unattended CV update. Reads .cv-work/candidates.json (new publications and DOI backfills from DBLP/OpenAlex/Crossref) and open cv-item issues, adds what is verifiably Jim's, verifies it, and opens one labelled PR. Pass "full" to also audit every entry.
allowed-tools: Read, Grep, Glob, Edit, Write, Agent, WebFetch, WebSearch, Skill, Bash(python3 scripts/check_cv.py:*), Bash(python3 scripts/fetch_candidates.py:*), Bash(git:*), Bash(gh pr:*), Bash(gh issue:*), Bash(gh label:*), Bash(curl:*), Bash(latexmk:*), Bash(date:*)
---

# Weekly CV update

Nobody is watching this run. Don't stop to ask; put questions in the PR and label it
`needs-review`. Follow `CLAUDE.md` (especially the hard rules).

## 1. Gather
- `.cv-work/candidates.json` (written by the workflow before you start). If it is missing,
  run `python3 scripts/fetch_candidates.py`. Note any `source_errors` for the PR.
- Open issues labelled `cv-item` that have no linked PR:
  `gh issue list --label cv-item --state open --json number,title,body`.
- `python3 scripts/check_cv.py --json` for the baseline (pre-existing warnings are not yours to fix).

## 2. Triage candidates (`new`)
For each record decide, and keep a one-line reason:
- **Is it Jim's?** DBLP records come from his disambiguated profile and are reliable. An
  OpenAlex/Crossref-only record needs a Waterloo affiliation or a coauthor already in his CV;
  otherwise it's a question, not an addition.
- **Already in the CV in another form?** A preprint of a paper already listed, an extended
  abstract vs full paper, a title that changed between submission and publication: compare
  authors + venue + year, not just title. If it's the published version of an entry marked
  "To appear", update that entry rather than adding a new one.
- **Worth listing?** Skip errata, front matter, proceedings volumes, and dataset deposits
  unless they match an existing pattern in the CV.

## 3. Edit (branch `cv/weekly-YYYY-MM-DD`)
- New entries: build each from the retrieved record (DOI metadata first), using the
  conventions in `CLAUDE.md`: key format, `\textbf{James R. Wallace}`, `*` for authors in
  `data/trainees.yaml`, DOI. Add the key to exactly one heading and, if in the review period
  with a trainee, to `apralsoteaching`. Append new entries next to similar entries; don't re-sort.
- DOI backfills from `doi_backfill`: add the `doi` field and drop `note = {To appear}` only
  if the record clearly is that paper.
- `cv-item` issues: handle each as the `add-cv-item` skill describes; reference "Closes #N".
- Commit additions and corrections separately.

## 4. Verify
Run the `cv-verify` skill (with `full` if this run was started with `full`). Then, if
`latexmk` is available, compile `main.tex` and `apr.tex` and fix any error you caused.

## 5. Open the PR
- If nothing changed: don't open a PR. Print a short summary (records seen, why each
  candidate was skipped) and stop.
- Otherwise push the branch and `gh pr create --base main` with title
  `CV update YYYY-MM-DD: <n> added, <m> updated`, the body from `cv-verify`, and the label it
  chose (`auto-merge` or `needs-review`; create missing labels with `gh label create`).
- Write the branch name to `.cv-work/branch` (the workflow uses it to start CI).
