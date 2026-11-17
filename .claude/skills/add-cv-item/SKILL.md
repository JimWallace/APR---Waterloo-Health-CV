---
name: add-cv-item
description: Add one item Jim reports (paper, talk, award, reviewing/PC role, grant, supervision, service) to the CV from an issue or chat message, verify it, and open a labelled PR.
allowed-tools: Read, Grep, Glob, Edit, Write, Agent, WebFetch, WebSearch, Skill, Bash(python3 scripts/check_cv.py:*), Bash(python3 scripts/fetch_candidates.py:*), Bash(git:*), Bash(gh pr:*), Bash(gh issue:*), Bash(gh label:*), Bash(gh api:*), Bash(curl:*), Bash(latexmk:*)
---

# Add a CV item

The request comes from Jim (an issue body or comment). What he says about his own roles,
awards, grants and students is the source; cite it as "issue #N".

1. **Classify** the item and find where it goes (`CLAUDE.md` → "Where non-publication items
   go" and "Which heading"). Read the neighbouring lines and copy their format exactly.
2. **Publications and talks:** look for a public record (DOI, DBLP, publisher, program page).
   If found, build the bib entry from it. If not yet public, use what Jim wrote and add
   `note = {To appear}`. Mark trainees per `data/trainees.yaml`; if Jim names a new trainee,
   add them to `data/trainees.yaml` (he told you, so this one is allowed) and say so in the PR.
3. **Other items:** add to the right list in `main.tex` with the matching `\hl…[years]` macro.
   Grants: one row per line of the existing table format, `\hl…row{years}` on each row,
   `\\*` at the end of each row of the grant and `\\` on the blank row after it.
   Amounts, agencies, roles and dates come only from Jim's message; ask in the PR if any is missing.
4. Branch `cv/issue-<N>-<slug>`, commit, run the `cv-verify` skill, push, open the PR with
   "Closes #N" and the label `cv-verify` chose, and reply on the issue with the PR link and
   any questions. If `gh pr create` fails, use the REST API as in
   `automation/weekly-update.md` step 7. The repo is public: no email text or private details.
