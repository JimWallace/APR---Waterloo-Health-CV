# Jim Wallace's CV

LaTeX CV in the University of Waterloo Faculty of Health format. One source, two PDFs:

- `main.tex` compiles to the plain Faculty of Health CV.
- `apr.tex` compiles `main.tex` with the `apr` option: adds the "A Note on…" sections and colours
  review-period items (see the header of `aprcv.sty`). Never put content in `apr.tex`.
- `scholar.bib` holds publications, talks and software. `main.tex` decides which heading each
  entry prints under with `\addtocategory{<category>}{key, key, …}` near the top.
- `data/trainees.yaml` lists my trainees (students/postdocs) and the spellings used for them.
- `2pages.tex` / `8pages.tex` are older NSERC-format variants; leave them alone unless asked.

The repo is mirrored to Overleaf (see `.github/workflows/overleaf-sync.yml`). GitHub `main` is
the source of truth; never force-push `main`.

## Hard rules

1. **Never invent or "fill in" bibliographic facts.** Every author list, title, venue, year,
   pages and DOI must come from a record you retrieved this run (DOI landing page, Crossref,
   DBLP, OpenAlex, ACM DL, publisher page) or from something I wrote in an issue. If a fact
   can't be confirmed, leave it out and say so in the PR.
2. **Never delete or rewrite existing CV content** (entries, table rows, narrative) unless the
   task is explicitly to correct it and the correction is supported by a retrieved record or
   by me. Corrections to existing entries always go in their own commit.
3. **Do not edit the narrative sections** ("A Note on …", inside `\ifAPR … \fi`) in automated
   runs. Suggest changes in the PR description instead.
4. **Trainee marks are my call.** Add `*` only for people in `data/trainees.yaml`. Never add a
   person to `data/trainees.yaml` yourself; ask in the PR ("Is X your trainee?") and label it
   `needs-review`.
5. Keep diffs minimal: no reformatting, re-sorting or whitespace churn in files you touch.

## Conventions

**Bib entries** (`scholar.bib`)
- Key: `familyYYYYfirstword` in lower case, e.g. `wong2026ipvprevention`. Keys must be unique:
  `python3 scripts/check_cv.py` fails on duplicates (biber silently drops the second copy).
- My name is always `\textbf{James R. Wallace}`.
- Trainee: `*` straight after the family name — `Wong*, Veen` or `Veen Wong*`. Not on the given
  name (`Homaeian, L.*` loses the mark under `giveninits`).
- Presenter of a talk or paper: `{\dag}` after the name (after `*` if both): `Gauthier*{\dag}, Robert P`.
- Include `doi` whenever one exists; ACM entries use `@inproceedings` (conference proceedings)
  or `@article` (PACM / journals) as the ACM DL export does.
- Accepted-but-unpublished work: add `note = {To appear}` and no DOI; the weekly run backfills
  the DOI when it appears.

**Which heading** (`\addtocategory` in `main.tex`; each printed entry in exactly one of these)
- `journal`: journal articles, including Proceedings of the ACM (PACM HCI, CSCW, CHI PLAY,
  GROUP, ISS) and JMIR etc.
- `conference`: full and short papers in conference proceedings (CHI, DIS, GI, CHI EA, LBWs,
  workshop papers published in proceedings).
- `presentations`: self-initiated talks/posters without archival proceedings. `invited`: invited talks.
- `technicalreports`, `other`, `patent`, `software` as named.

**APR colours** (`main.tex`, block after the categories; rules in `aprcv.sty`)
- Bib entries in the review period (`\setreviewperiod`) are research-green automatically.
  `aprinclude` treats an entry as in the period (e.g. a 2027 paper accepted during it);
  `aprnone` turns highlighting off for one entry. Only I add keys to either.
- If any author is my trainee (`*`) or a trainee presented (`\dag`), also add the key to
  `apralsoteaching`.
- Non-bib items use `\hlteaching[years]{…}`, `\hlresearch`, `\hlservice`, `\hlaward`, or the
  `\hl…row{years}` forms at the start of each grant-table row. Always give `[years]`.

**Where non-publication items go** (all in `main.tex`)
- Awards → ACADEMIC AWARDS AND DISTINCTIONS (newest first, `\hlaward[YYYY]{…}`).
- Reviewing, PCs, editorial roles, organizing → SCHOLARLY AND PROFESSIONAL ACTIVITIES lists.
- Grants → RESEARCH GRANTS AND CONTRACTS table: match the existing row format exactly. End
  each row of a grant with `\\*` (keeps the grant on one page) and the blank row after it
  with `\\`.
- Supervision → GRADUATE STUDENT SUPERVISION. Service → SERVICE.

**Page breaks** are set in `cv-layout.tex`. Put `\keepwithnext` before a new heading that is
followed by a list; never use `\newpage` (use `\sectionbreak`).

## Checks

- `python3 scripts/check_cv.py` — deterministic checks; errors fail CI. Run it after every edit.
- `python3 scripts/check_cv.py --keys k1,k2` — the same, reporting only on the keys you touched.
- `latexmk -pdf main.tex && latexmk -pdf apr.tex` — if TeX is installed; CI compiles both anyway.
- Verifier sub-agents in `.claude/agents/` check changes independently. The `cv-verify` skill
  says how to run them.

## Pull requests

- The weekly scheduled job follows `automation/weekly-update.md`, works on a branch
  `cv/weekly-YYYY-MM-DD`, and labels its PR either `auto-merge` (every check and verifier
  passed, no open questions) or `needs-review` (plus a "Questions for Jim" section).
  `cv/` PRs merge only with the `auto-merge` label. When unsure, choose `needs-review`.
- Any other PR opened under Jim's GitHub account — including one you open for him in a
  chat — merges automatically once CI passes. Open it as a draft, or label it
  `needs-review`, if he should look first.
- Every PR body has a table of the changes (what, where, source).
- `gh pr create` and other GraphQL-based `gh` commands can be blocked in Claude sessions;
  use the REST API (`gh api repos/JimWallace/APR---Waterloo-Health-CV/pulls …`).
- The repo is public: never put email text, rejections, or private details in commits,
  PRs or issues.

## Sources I use

- DBLP person id: `65/4889`
- OpenAlex author id: resolved by name each run; pin it as the repo variable `OPENALEX_AUTHOR_ID`
- ORCID: not set yet
- Google Scholar can't be queried automatically; don't try.
- The "CV sources" workflow saves DBLP/Crossref records on the `cv-sources` branch weekly
  (`git fetch origin cv-sources`); use them when your session can't reach those sites.
