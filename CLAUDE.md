# Jim Wallace's CV

LaTeX CV in the University of Waterloo Faculty of Health format. The repo has two halves:

- **The template** (`template/`): the Faculty of Health format and the APR highlighting
  (`uwhealthcv.sty`, `aprcv.sty`, the formatting and page-break files, the ACM biblatex style,
  badge images) plus a fictional example CV. No personal data. It has its own `README.md` and
  `CLAUDE.md`; read them before changing anything there.
- **My CV** (everything else): content and my settings. `latexmkrc` puts `template/` on TeX's
  search path, so `main.tex` just says `\usepackage{uwhealthcv}`.

One source, two PDFs:

- `main.tex` compiles to the plain Faculty of Health CV.
- `apr.tex` compiles `main.tex` with the `apr` option: adds the "A Note on…" sections and colours
  review-period items (see the header of `template/aprcv.sty`). Never put content in `apr.tex`.
- `scholar.bib` holds publications, talks and software. `main.tex` decides which heading each
  entry prints under with `\addtocategory{<category>}{key, key, …}` near the top.
- `grants.bib` holds grants (`@grant`), `supervision.bib` my students (`@supervision`) and
  `awards.bib` the ACADEMIC AWARDS AND DISTINCTIONS list (`@award`) and
  `service.bib` the SERVICE lists and `activities.bib` the SCHOLARLY AND PROFESSIONAL
  ACTIVITIES lists (both `@service`).
  The fields are described in `template/uwhealthcv.dbx`. They print sorted, and the APR
  colours come from their dates, so there are no years to keep in step by hand.
- `apr-formatting.tex` holds my settings for the APR version (highlight strength and style).
- My trainees are everyone in `supervision.bib` plus `data/trainees.yaml`, which adds the other
  trainees (undergraduates, RAs) and extra spellings. The checker flags a supervised student
  whose name is spelled differently in the two.
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
4. **Trainee marks are my call.** Add `*` only for my trainees (`supervision.bib` or
   `data/trainees.yaml`). Never add a person to either file yourself; ask in the PR ("Is X your trainee?") and label it
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
- A paper or talk that won an award: `icon = {award}` (the rosette in the margin; in the APR
  version it is filled pink when the entry is in the review period), the award in bold in
  `note`, e.g. `note = {\textbf{Best Paper Honourable Mention Award}}`, and an `@award` in
  `awards.bib` with `work = {<that key>}`. The checker fails if either half is missing. If a
  trainee won it, add the award's key to `apralsoteaching` too.
- Include `doi` whenever one exists; ACM entries use `@inproceedings` (conference proceedings)
  or `@article` (PACM / journals) as the ACM DL export does.
- Accepted-but-unpublished work: add `note = {To appear}` and no DOI; the weekly run backfills
  the DOI when it appears.
- Refereed work that has no DOI at all (a poster or abstract with no archival proceedings):
  `nodoi = {<reason>}`. It does not print; it tells `check_cv.py` not to ask for a DOI. Only I
  decide that a work has none.

**Which heading** (`\addtocategory` in `main.tex`; each printed entry in exactly one of these)
- `journal`: journal articles, including Proceedings of the ACM (PACM HCI, CSCW, CHI PLAY,
  GROUP, ISS) and JMIR etc.
- `conference`: full and short papers in conference proceedings (CHI, DIS, GI, CHI EA, LBWs,
  workshop papers published in proceedings).
- `presentations`: self-initiated talks/posters without archival proceedings. `invited`: invited talks.
- `technicalreports`, `other`, `patent`, `software` as named.
- `unprinted`: entries I keep in `scholar.bib` but do not print. Listing a key here records
  that decision, so `check_cv.py` stops warning that it does not appear. Only I add keys.

**APR colours** (`main.tex`, block after the categories; rules in `template/aprcv.sty`)
- Bib entries in the review period (`\setreviewperiod`) are research-green automatically.
  `aprinclude` treats an entry as in the period (e.g. a 2027 paper accepted during it);
  `aprnone` turns highlighting off for one entry. Only I add keys to either.
- If any author is my trainee (`*`) or a trainee presented (`\dag`), also add the key to
  `apralsoteaching`.
- Grants are highlighted when their `date` range overlaps the period; students when they are
  `status = {In progress}` or their `date` is in the period. Nothing to add by hand.
- Awards are highlighted when their year is in the period. Other non-bib items use `\hlteaching[years]{…}`, `\hlresearch`, `\hlservice`, `\hlaward`.
  Always give `[years]`.

**Where non-publication items go**
- Awards → ACADEMIC AWARDS AND DISTINCTIONS (newest first, `\hlaward[YYYY]{…}`).
- Reviewing, PCs, editorial roles, organizing → a `@service` entry in `activities.bib` with `level`
  grantreferee, journal, organizing, programcommittee or referee (the SCHOLARLY AND PROFESSIONAL
  ACTIVITIES lists). A chair role that is also scholarship stays in `service.bib` with
  `level = {discipline, organizing}`, so it prints in both sections. Only the ACM membership
  line of that section is still hand-written in `main.tex`.
- Awards → an `@award` in `awards.bib` (`title` as it should print, `date` = the year,
  `count` for "3 ×" lines). Order within a year follows the file.
- Service → a `@service` entry in `service.bib`: `title` as it prints, `level` (one of the
  `\printservice{…}` lists in `main.tex`: school, faculty, university, discipline) and
  `date = {2023/2025}` for the years served (`2021/` for an ongoing role: "2021 -- Present",
  sorted first). A `level` may name several lists, comma-separated. Optional `years` prints instead of the range
  ("2017, 2019 -- 2021"); optional `role` prints after the years ("General Chair"). The lists
  sort newest first and are highlighted from the dates; a leadership role that is also
  scholarship goes in `apralsoresearch`.
- Grants → a `@grant` entry in `grants.bib`. List investigators in the order given, with
  `\me` for me and `role` for my role; `amount` is digits only; `date = {2026/2028}` is the
  tenure. Order in the file doesn't matter.
- Supervision → a `@supervision` entry in `supervision.bib`: `author = {Family, Given}`,
  `degree` (one of the `\printsupervision{…}` lists in `main.tex`), and `status = {In progress}`
  until they finish, then `date`, `title` and, when I know it, `position`. Committee
  membership and external examining stay as lines in `main.tex`.

**Markup** comes from the template (`template/uwhealthcv.sty`): headings are `\cvsection{…}`,
labels over a list `\cvsubheading{…:}`, list items `\cvitem …` inside `cvlist`, lettered parts
`\cvpart{…}` inside `cvparts` (letters are automatic), students `\item …` inside
`\begin{cvdegree}{PhD}`, bibliography headings `\printcategory[J]{journal}`. Copy the
neighbouring entry; don't write raw `itemize`/`\setlength` blocks.

**Page breaks** are set in `template/cv-layout.tex`. Put `\keepwithnext` before a new heading
that is followed by a list; never use `\newpage` (use `\sectionbreak`).

## Checks

- `python3 scripts/check_cv.py` — deterministic checks; errors fail CI. Run it after every edit.
  Warnings fail too unless `scripts/warnings-baseline.txt` lists them, and a listed warning
  that no longer occurs fails until its line is deleted (`--prune-baseline`). Fix a new warning
  rather than adding it to the baseline: a PR that adds baseline lines cannot auto-merge.
- `python3 scripts/check_cv.py --keys k1,k2` — the same, reporting only on the keys you touched.
- `latexmk -pdf main.tex && latexmk -pdf apr.tex` — if TeX is installed; CI compiles both anyway.
  Then `python3 scripts/warning_ratchet.py main apr` applies the same baseline to the LaTeX and
  biber warnings (CI does this too, on TeX Live 2026 like Overleaf, and reports what changed in
  the PDF text). A local TeX Live 2023 (Debian) can differ slightly; CI is the reference.
- After a template change, also build `template/example/` (`example.tex`, `example-apr.tex`);
  CI does, and fails if `template/` mentions me.
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
