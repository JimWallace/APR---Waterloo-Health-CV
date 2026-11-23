---
name: add-cv-item
description: Add one item Jim reports (paper, talk, award, reviewing/PC role, grant, supervision, service) to the CV from an issue or chat message, verify it, and open a labelled PR.
allowed-tools: Read, Grep, Glob, Edit, Write, Agent, WebFetch, WebSearch, Skill, Bash(python3 scripts/check_cv.py:*), Bash(python3 scripts/generate.py:*), Bash(python3 scripts/warning_ratchet.py:*), Bash(python3 scripts/fetch_candidates.py:*), Bash(git:*), Bash(gh pr:*), Bash(gh issue:*), Bash(gh label:*), Bash(gh api:*), Bash(curl:*), Bash(latexmk:*)
---

# Add a CV item

The request comes from Jim (an issue body or comment). What he says about his own roles,
awards, grants and students is the source; cite it as "issue #N".

1. **Classify** the item and find where it goes (`CLAUDE.md` → "Where non-publication items
   go" and "Which heading"). Read the neighbouring lines and copy their format exactly.
2. **Publications and talks:** look for a public record (DOI, DBLP, publisher, program page).
   If found, build the bib entry from it. If not yet public, use what Jim wrote and add
   `note = {In press}`. Mark trainees per `supervision.bib` and `data/trainees.yaml`; if Jim names a new
   trainee, add them (a supervised student to `supervision.bib`, anyone else to
   `data/trainees.yaml`; he told you, so this one is allowed) and say so in the PR.
   Add the full information available now: DOI, pages, award, and the acceptance rate
   (conference/PACM) or journal impact factor, as `CLAUDE.md` → "Acceptance rates and impact
   factors" says. The acceptance email usually states the rate; search Outlook for it if the
   connector is available. If no figure exists or can be found, add a `data/metrics.yaml` line
   so `scripts/missing_metrics.py` retries it later.
3. **Grants, students and awards:** add a `@grant` entry to `grants.bib`, a `@supervision`
   entry to `supervision.bib` or an `@award` entry to `awards.bib` (with a `level`, and with `work = {key}` and
   `icon = {award}` on that entry when it is for a paper or talk) (fields in `template/uwhealthcv.dbx`, examples in each file). No
   highlighting to add: it follows the dates. Amounts, agencies, roles, dates, titles and
   students' positions come only from Jim's message; ask in the PR if any is missing.
   `grants.bib` records every application, funded or not: a pending one has
   `status = {Submitted}`, a rejected one `{Rejected}`, each with `submitted` and (once decided)
   `decided` (`CLAUDE.md` → Grants); `python3 scripts/grant_report.py --missing` lists gaps.
   **Service:** add a `@service` entry to `service.bib` (`title`, `level`, `date`); reviewing,
   program committees, editorial and organizing roles go in `activities.bib` the same way.
   **Other items:** add to the right list in `main.tex` with the matching `\hl…[years]` macro.
   Submitted grants, trainee scholarships, nominations, review panels, external reviews,
   session chairs, media, training, mentoring, leaves and student start years each have a
   place in `CLAUDE.md` → "Where non-publication items go"; a kind with no list yet gets its
   heading added to `main.tex` in the same commit.
4. **Entry detail:** give the item the facts `CLAUDE.md` → "Entry detail" names for its kind
   now, while the sources are fresh (attendance and submissions for a chair role, how many
   took part in a workshop, an award's tier, an editorial load), from Jim's message, the
   venue or Outlook; never estimate. `python3 scripts/gaps.py --list` shows what the entry
   still lacks; ask Jim for it in the PR, or on the issue.
5. Run `python3 scripts/generate.py` and commit what it rewrites with the item. A new venue
   or funder stops it: tag it as `automation/weekly-update.md` step f3 says, with the
   evidence in the PR's change table (Jim's word in the issue is evidence too).
6. Branch `cv/issue-<N>-<slug>`, commit, run the `cv-verify` skill, push, open the PR with
   "Closes #N" and the label `cv-verify` chose, and reply on the issue with the PR link and
   any questions. If `gh pr create` fails, use the REST API as in
   `automation/weekly-update.md` step 7. The repo is public: no email text or private details.
