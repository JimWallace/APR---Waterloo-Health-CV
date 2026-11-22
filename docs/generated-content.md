# Generated text and counts: design

Issue #144. How the CV keeps its interdisciplinary counts current, and how new venues and
funders get tagged without Jim or a chat session remembering to do it. Builds on PR #143
(the venue profile).

## What is generated now

| Output | Generator | Reads | Prints |
|---|---|---|---|
| `data/venue-profile.tex` | `scripts/venue_profile.py` | `data/venues.yaml`, `scholar.bib`, `main.tex` | journal articles by field (both PDFs) |
| `data/funders.tex` | `scripts/funder_profile.py` | `data/funders.yaml`, `grants.bib` | the health-funder sentence (APR funding note) |
| `data/cv-numbers.tex` | `scripts/cv_numbers.py` | all of the above, `data/citation-impact.yaml` | `\cvnumber{…}` in the narratives |
| `data/citation-impact.tex` | `scripts/citation_impact.py` | `data/citation-impact.yaml` | the SciVal line under top-cited papers |

`python3 scripts/generate.py` reruns all four; `--check` reports what is out of step, and
`check_cv.py` calls it once (W-generated) instead of one check per file. Everything it reads
is in the repository, so CI gets the same answer as a laptop.

Left out on purpose: `software_stats.py` (clones repositories over the network; the weekly
run calls it), a SciVal import (only Jim has exports) and the committee counts (the template
counts `committees.bib` while the PDF builds, so they cannot go stale).

## 1. One model for "field"

**One vocabulary per kind of thing, one loader, one entry point; a small module per output.**

- Venues: `data/venues.yaml`, sections `journals` (matched by name or `aka`) and
  `proceedings` (matched by `match` substrings of booktitle, journal or series, since a
  conference's proceedings title changes every year). `field`: health, hci, computing,
  multidisciplinary.
- Funders: `data/funders.yaml`, one record per funder with every `agency` spelling used in
  `grants.bib`. `sector`: health, nse, ssh, multidisciplinary, government, industry,
  university, unclassified. The sector is who funds the work, not its topic, so Waterloo's
  own CIHR Research Incentive Fund is `university`, not `health`.
- Co-authors: a list Jim maintains (question 5), not a third tagging scheme.

Venues and funders are different things (a venue's field is a judgement about its scope; a
funder's sector is a fact about its mandate), so they keep separate files and vocabularies,
but share the reader (`cvlib.load_tagged`, PyYAML when present, a plain reader otherwise so
CI needs no installs) and the `source` field that records the evidence. Each output keeps
its own small module, as `software_stats.py` and `citation_impact.py` do, because each has
its own wording; `generate.py` is the single entry point and the single check.

Every proceedings entry must match a series (as every journal must), so "not tagged" can't
quietly mean "not health". Today: 58 proceedings entries, 2 at health venues
(PervasiveHealth, ICHEC); 24 journal articles, 9 in health journals; 35 funded grants, 6
from health funders.

## 2. Tagging new venues and funders in the weekly run

`automation/weekly-update.md` step f3 has the rules; in short:

| Case | Evidence | Label |
|---|---|---|
| A new spelling of a listed venue or funder | the entry itself | `auto-merge` |
| A new venue | its scope statement **and** its OpenAlex source's largest topic share (≥ 50%) agree, both retrieved this run | `auto-merge` |
| A new venue, sources disagree, share < 50%, one source unreachable, or first of a new field | | `needs-review` + question |
| A new funder that is a granting council or health research charity | its own mandate page | `auto-merge` |
| Any other new funder | | `sector: unclassified` + question |
| Changing an existing tag | from Jim | correction commit, `needs-review` |

The change table cites the URLs; the record keeps them in `source`. `diff-auditor` fails a
new record with no source or a generated file that isn't what `generate.py` writes;
`apr-classifier` checks that the field or sector fits the evidence; `citation-verifier`
can fetch the cited pages when a reviewer wants the evidence re-read.

**Needs Jim: an OpenAlex API key.** OpenAlex now refuses keyless requests once the shared
daily budget for an IP address is spent (it was spent when this was written, from a cloud
session). Without a key the venue rule falls back to one source, which is `needs-review`.
A free key, stored as the repository secret `OPENALEX_API_KEY` (and in the cloud
environment's secrets for the weekly session), fixes this; `fetch_candidates.py`, which also
calls OpenAlex, should send it too. Getting one needs Jim's email, so only Jim can.

## 3. Numbers in the narratives

The narratives stay Jim's text; their counts come from `data/cv-numbers.tex`:
`\cvnumber{review-works-trainee-first}` prints 28. A count earns a name when it changes as
the record grows:

| Kept as `\cvnumber` | Value now | Narrative |
|---|---|---|
| `review-works`, `review-works-trainee-first`, and per group (journal, conference, presentations) | 34 / 28; 5/4, 11/9, 18/15 | Graduate Supervision |
| `scival-papers`, `scival-top`, `scival-top-share`, `scival-last-year` | 63, 12, 19%, 2025 | Research Contributions (commented out) |
| `scival-top-trainee-first` | 5 | Graduate Supervision |
| `journals(-health)`, `proceedings(-health)`, `grants-funded(-health)` | 24/9, 58/2, 35/6 | available; not quoted yet |

All of these reproduced the hand-typed values exactly before they were swapped in, so both
PDFs print the same text as before. Not worth a name: fixed facts (the workshop's 41 of 173,
grant amounts, an acceptance rate) and figures the repository doesn't hold (SciVal's topic
totals: "134 citations", "387 citations", "18 papers"; the Chickadee and SCP figures). Those
stay typed; if Jim wants them checked, the SciVal topic export would have to be imported
like the publication export.

**How the checker catches a hard-coded copy.** `cv_numbers.HINTS` pairs each count with the
phrase Jim uses for it (`first authors on \d+ of the \d+`). A digit in that phrase is
W-numbers ("print it with \cvnumber{…}"). The patterns match only the current wording, so a
rewritten sentence never warns falsely; the cost is that a new sentence needs a new hint.
`\cvnumber` of an undefined name is an error (E-numbers), and prints **??** in the PDF.

In automated runs, rule 3 still holds: the agent never edits a narrative, but a narrative
that uses `\cvnumber` updates itself when `generate.py` runs.

## 4. One entry point

`scripts/generate.py` (above). The weekly run and `add-cv-item` call it after every edit;
CI runs its check through `check_cv.py`. No make target: the repository has no Makefile and
Overleaf ignores one.

## 5. Co-author field mark

**Feasible only as a list Jim keeps.** OpenAlex gives a co-author's institution but almost
never their department; ORCID employment records sometimes name the department but are
self-reported and often missing or out of date; neither says "primary appointment in a health
unit". So:

- `data/coauthors.yaml`: names (and spellings) of co-authors whose primary appointment is in
  a health, clinical or public health unit, as `data/trainees.yaml` is for trainees. Only Jim
  adds people. The weekly run may *propose* one in the PR, citing an ORCID employment record
  or a faculty page that names the unit, never adding it itself.
- `check_cv.py` warns when a listed co-author appears without the mark, like the trainee
  check.
- The template needs a new mark (Mentis uses one): an author suffix like the trainee `*` and
  presenter `\dag`, for example `\healthmark` printing a small superscript (‡ is free), and a
  line in the legend that explains `*` and `\dag`. That is a template feature (a new minor
  version), so it waits for Jim's go-ahead on the symbol and the wording.

## The template

What should move to the template repository, and in what order:

1. **Now (draft PR in the template repository):** `\setcvnumber{name}{value}` and
   `\cvnumber{name}` in `uwhealthcv.sty`, so a CV's generated numbers have a documented home,
   an undefined name gives a LaTeX warning as well as **??**, and the example shows one.
   `data/cv-numbers.tex` defines both with `\providecommand` until that release reaches this
   CV, so nothing here waits for it.
2. **After Jim agrees the scope:** the co-author mark (question 5).
3. **Once the generators have run a few weeks here:** port `generate.py`, `venue_profile.py`,
   `funder_profile.py`, `cv_numbers.py`, the tagging step and the tests to `starter/`, with
   fictional `venues.yaml` and `funders.yaml`, so other CVs get them. Their only
   person-specific parts are the review-period groups and HINTS (Jim's wording), which
   would move to `starter/cv.toml`.

## Open questions for Jim

- Proceedings at health venues: print a line like the journals one ("2 of the 58 papers and
  extended abstracts in conference proceedings appeared at health venues")? The count is
  there (`\cvnumber{proceedings-health}`); I left the printed line alone.
- `chen2019design` is a PervasiveHealth demo/poster but sits in `conference`; should it be in
  `abstracts`?
- Funders I could not tag with confidence (`unclassified`, never printed): Graham Seed Fund,
  NAR Catalyst, CIRTA. Also check: Propel CDPI, Games Institute and Global Futures as
  `university`; Global Water Futures as `nse`.

## Missing data: the review copy

Jim, 2026-11-22: "make sure that missing data is obvious, maybe a different highlight colour
just for us, so that I can address any missing data in any entry before it goes in."

- `gaps.tex` compiles the APR version with the template's `gaps` mode (`\def\cvshowgaps{}`,
  template v0.10.0). Missing data prints in orange, a colour none of the four APR highlights
  use: an orange **Missing** tag and the list under the entry ("Missing: DOI, pages"), and
  an orange box in a grant's blank amount, tenure, agency, title or role cell or for an
  undefined `\cvnumber`. `main.pdf` and `apr.pdf` are unchanged: without the mode the
  template prints none of it.
- What counts as missing is the CV's rule, not the template's: `scripts/gaps.py` writes
  `data/gaps.tex` (`\setentrygap{key}{…}`) from the records, so it stays in step through
  `generate.py` and `check_cv.py` like the other generated files. Today: 59 entries
  (unresolved acceptance rates, three in-press papers, old abstracts without DOIs, students'
  start years and programs, defended committees without titles, four courses without SCP).
- Since 2026-11-22 it also checks the "so what?" facts (`CLAUDE.md` → Entry detail): an
  award's tier, how many took part in a workshop or meetup, the attendance and submissions
  of an event Jim chaired in the review period, and an editorial role's load. The weekly
  run's step k fills what a source states and opens a `cv-item` issue for the rest.
- A gap that can't be filled (a term with no SCP survey) goes in `data/gaps.yaml`, Jim's
  list, like `data/metrics.yaml`'s `none`.
- CI builds `Wallace-CV-gaps.pdf` on every PR (artifact and the `cv-preview` prerelease,
  never `cv-latest`) and lists the gaps in the job summary; the weekly PR says how many
  entries have gaps and which it filled.
- Until the template release with `gaps` mode reaches `template/`, `data/gaps.tex` defines
  `\setentrygap` and `\cvgap` as no-ops, so the review copy builds but shows no marks.
