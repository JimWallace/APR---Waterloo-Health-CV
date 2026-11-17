---
name: cv-verify
description: Verify CV changes with the deterministic checker and four independent verifier sub-agents, then decide the PR label. Use after any edit to scholar.bib or main.tex, or with "full" to audit every bib entry.
allowed-tools: Read, Grep, Glob, Edit, Agent, Bash(python3 scripts/check_cv.py:*), Bash(git diff:*), Bash(git log:*), Bash(git status:*), Bash(curl:*)
---

# Verify CV changes

Arguments: none (verify the current branch against `origin/main`), or `full` (audit every entry).

## 1. Scope
- Normal: keys = bib keys added or changed in `git diff origin/main...HEAD -- scholar.bib`,
  plus keys whose `\addtocategory` membership changed in `main.tex`. Also note any other
  `main.tex` hunks (awards, service, grants…).
- `full`: every key in `scholar.bib`, in batches of about 15.

## 2. Deterministic checks first
Run `python3 scripts/check_cv.py`. Fix every **error** before going on (they mean the PDF is
wrong). Warnings on keys you touched: fix them if the fix is definite; otherwise carry them
into the PR as questions. Leave warnings on untouched keys alone.

## 3. Independent verifiers — in parallel, in one message
Launch these sub-agents together. Give each only the inputs listed (the key list, the diff,
the change table) and **not** your reasoning about why the change is right: they are useful
because they check from scratch.
- `citation-verifier` — keys (for `full`, one agent per batch, all batches in parallel)
- `trainee-checker` — keys
- `apr-classifier` — keys + diff (skip in `full` mode)
- `diff-auditor` — your draft change table (skip in `full` mode)

## 4. Act on the verdicts
- FIX rows that come with a retrieved source URL: apply exactly that fix, then re-run step 2
  and re-run only the verifier that raised it, on only those keys. At most two rounds.
- A FIX without a source, or verifiers disagreeing: don't apply it; it becomes a question.
- In `full` mode, corrections to existing entries go in one commit titled
  "Corrections from full audit" and the PR is always `needs-review`.

## 5. Decide the label
`auto-merge` only if all are true:
- `check_cv.py` exits 0;
- every verifier's final VERDICT is PASS;
- no UNVERIFIABLE item is a new entry (a forthcoming paper Jim told you about in an issue,
  marked `note = {To appear}`, is fine);
- no change to existing entries other than DOI backfills confirmed by `citation-verifier`.

Otherwise `needs-review`, with a **Questions for Jim** section listing each open item in one
line he can answer yes/no.

## 6. Report
Put in the PR body: the change table (what / where / source), one line per verifier with its
verdict, and the questions. Paste full verifier tables in a collapsed `<details>` block.
