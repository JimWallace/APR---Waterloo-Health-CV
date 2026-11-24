# Weekly CV update — instructions for the scheduled job

Jim runs a weekly scheduled Claude task that points here. Nobody is watching the run: don't
stop to ask. Put questions in the PR (label `needs-review`) and private notes in your final
message. Read `CLAUDE.md` first; its hard rules apply throughout.

Jim asks that the verification in step 5 be done by independent sub-agents.

## 0. Set up

1. Get the repo `JimWallace/APR---Waterloo-Health-CV` with push access (attach it if your
   session needs that), clone it, and create the branch `cv/weekly-YYYY-MM-DD` from `main`.
2. GitHub access: use `gh api` (REST). `gh pr create` and other GraphQL-based commands may be
   blocked in Claude sessions; every step below has a REST form.
3. **Records.** `git fetch origin cv-sources` and read, with `git show origin/cv-sources:<path>`:
   `candidates.json`, `records/index.json`, `records/crossref/*.json`, `records/dblp-person.xml`.
   These were fetched by the "CV sources" workflow on GitHub, which can reach DBLP and
   Crossref when your session may not. If `records/index.json` is more than 3 days old or
   missing, start that workflow and wait for it (poll every 30 s, up to 10 min):
   `gh api repos/JimWallace/APR---Waterloo-Health-CV/actions/workflows/cv-sources.yml/dispatches -f ref=main`
   If it still fails, try `python3 scripts/fetch_candidates.py`; if that can't connect either,
   carry on with steps 2–3 and say in the PR that publication sources were unavailable.
4. Run `python3 scripts/check_cv.py --json` for the baseline. Pre-existing warnings are not
   this run's job.

## 1. Follow up last week's PRs

List open PRs from `cv/` branches (`gh api 'repos/JimWallace/APR---Waterloo-Health-CV/pulls?state=open'`).
For each:
- Read Jim's comments on it. Where he has answered a question, apply the answer on that
  PR's branch, push, update the body, and switch the label to `auto-merge` if nothing is left open.
- If its CI failed (`gh api repos/…/commits/<head sha>/check-runs`), fix the cause on its branch.
Don't duplicate an item that is still waiting in an open PR.

## 2. Collect this week's items

a. **Publications** — `candidates.json`: `new` (works not in `scholar.bib`) and `doi_backfill`.

b. **Issues** — open issues labelled `cv-item`:
   `gh api 'repos/JimWallace/APR---Waterloo-Health-CV/issues?labels=cv-item&state=open'`.
   What Jim writes about his own roles, awards, grants and students is a source ("issue #N").

c. **Outlook** — with the Microsoft 365 connector, search Jim's mail since the last weekly
   PR was opened (or the last 8 days). Useful searches, each limited to that window:
   `accepted`, `acceptance`, `camera-ready`, `congratulations`, `decision on your submission`,
   `special recognition`, `outstanding review`, `best paper`, `honourable mention`,
   `program committee`, `associate chair`, `associate editor`, `thank you for reviewing`,
   `agreed to review`, `notice of award`, `funding decision`, `invited talk`, `keynote`,
   `thesis defence`, `examination committee`, `comprehensive exam`.
   Take an item only when an official message (from the venue, journal, agency or university
   office, or Jim's own confirmation) states it outright. If the connector isn't available,
   skip this and say so in your final message.

   **The rest of the record** (added November 2026, after comparing Jim's CV with SPHS full
   professors'). Also search the same window for these, and file them as `CLAUDE.md` → "Where
   non-publication items go" says. Every one of them is `needs-review`.
   - Invited talks, keynotes, seminars, guest lectures, panels: `invite you to speak`,
     `seminar`, `guest lecture`, `panelist`, `keynote`. The talk goes under `invited` once it
     has happened.
   - Session chair, moderator, discussant: `session chair`, `chair a session`, `moderator`.
   - Trainee scholarships and awards: `scholarship`, `OGS`, `CGS`, `Vanier`, `award`, with
     the names in `supervision.bib`. Only an award letter (or the student forwarding it)
     counts, not an application. Scholarships go in the student's `note`; prizes are
     `level = {trainee}` awards.
   - Nominations for Jim (teaching or supervision awards): `nomination`, `nominated`. Only
     once the nomination has been submitted.
   - Grant applications: `ResearchNet`, `compliance review`, `application submitted`,
     `submitted the complete application`, `thank you for applying`, `your application`,
     `application received`, `letter of intent`, `notice of intent`, `full application`,
     `invited to submit`, `cover sheet`, and decisions (`notice of decision`, `funding
     decision`, `notice of award`, `results`, `extension`). Applications reach Jim through
     the agencies, the University's research offices (`uwcihr@`, `uwsshrc@`, `uwnserc@`,
     `mitacs@`), foundations, companies and form receipts, and he is often a co-applicant on
     someone else's team: those count too. (In 2025–26 they included CIHR, SSHRC, NSERC
     CREATE and RTI, NFRF, Mitacs, ALS Canada–Brain Canada, Breast Cancer Canada,
     Digital Science, Google, Microsoft Research and Anthropic.)
     `grants.bib` is the record of **every** application Jim makes, funded or not, and the
     ground truth for his reporting (`CLAUDE.md` → Grants). Keep it complete:
     1. **New submission** you find: add its `@grant` at the end of `grants.bib` with
        `status = {Submitted}`, `submitted` (the date it went in) and what the record states
        (agency and program, team, role, title, amount, years). Open an issue labelled
        `grant-application` (agency, program, competition, date) asking Jim for what's
        missing; Jim can also open one with the "Grant application" issue form.
     2. **Every run**, for each open `grant-application` issue: apply the details Jim has
        given (in the issue or a comment) to its entry. A Submitted entry that went in during
        the review period goes in `aprinclude`. Submitted entries print under "Submitted"
        with blank cells for what is still missing, so filling those gaps is what to chase.
     3. **Decisions**: search the mail for each Submitted entry's decision. Funded: drop
        `status`, set the awarded amount and tenure from the notice of award, add `decided`,
        and "Closes #N". Rejected or withdrawn: `status = {Rejected}` (or `{Withdrawn}`) and
        `decided`, and "Closes #N". Jim decided (22 November 2026) that declines are
        recorded in full, in this public repo; still quote no email text.
     4. A funded change to an existing grant (an extension, a top-up, a new end date) is a
        correction to its entry: its own commit, from the agency's letter.
     5. In your final message, give the output of `python3 scripts/grant_report.py --missing`
        (details still to collect) and any Submitted entry more than nine months old with no
        decision found.
   - Review panels and expert or advisory committees: `review panel`, `committee member`,
     `expert panel`, `Delphi`, `advisory board`.
   - External tenure, promotion and program reviews: `external referee`, `external
     assessment`, `tenure and promotion`, `program review`. Institution and year only.
   - Media: `interview`, `podcast`, `Waterloo News`, `Daily Bulletin`, `UW Current`,
     `reporter`. Add a piece once it is published (find it on the outlet's site); an
     interview that hasn't run yet is a note in your final message.
   - Training and professional development: `certificate`, `training`, `completed`, `TCPS`,
     `bias in peer review`, `equitable recruitment`, `CTE`.
   - Undergraduate research students (URA, Hallman, Globalink, co-op, honours thesis,
     independent study): add them only when Jim confirms the student and role (ask in the
     PR, and never add a person to `data/trainees.yaml` yourself).

   **PCS reviewing.** Also search `precisionconference.com` in the same window. Links in PCS
   mail contain `/<venue code>/committee/` when Jim holds a committee role (associate chair,
   associate editor, program committee) and `/<venue code>/reviewer/` when he reviews as an
   external referee. Count the distinct submissions per venue and role, and compare with
   `activities.bib`: a venue and year missing from the referee or program committee lines is a
   new item (extend the line's years); a committee load that the entry's `note` doesn't give
   yet goes in the PR as a question for Jim. **Backfill:** while a review-period line (any
   level) still has no review count in its `note`, search PCS mail for that venue and year
   with no date limit, count the distinct submissions, and propose the count in the PR
   (`needs-review`). Do one or two venues per run. Record counts only, never submission numbers,
   titles or other people's names (see "Private" under step 3).

d. **Calendar** — with the same connector, list Jim's calendar events in the same window.
   Look for talks he gave (invited talks, keynotes, seminars, panels), sessions he chaired,
   thesis defences and examinations he sat on, training he took, and committee or
   program-committee meetings that show a role.
   A calendar entry alone shows that something was scheduled, not that it happened or what
   his role was: add an item only when a matching email or issue confirms it, or the event
   itself names him as speaker/examiner and its date has passed. Otherwise make it a
   question for Jim. Meeting content, attendees and private appointments stay private.

e. **Missing metrics** — run `python3 scripts/missing_metrics.py`. Take every entry under
   "Missing" (usually papers added since the last run) and the three oldest "Unresolved" ones,
   and look up the acceptance rate or impact factor as `CLAUDE.md` → "Acceptance rates and
   impact factors" says. Check the decision letter in Outlook first (search the venue and year
   with `acceptance rate`, `submissions`, `accepted`), then the front matter, editorial or
   publisher page. Entries the script lists as "Now in scholar.bib" lose their
   `data/metrics.yaml` line.
   **Each July–September** (after Clarivate's June JCR release), also refresh every
   `Journal Impact Factor (YYYY)` note whose year is older than the newest release, from the
   journal's publisher page.

f. **Software stats** — run `python3 scripts/software_stats.py`. It clones the repositories in
   `data/software.yaml` (public GitHub; no token needed) and regenerates
   `data/software-stats.tex` (the line under each software entry). Commit the result on its own
   ("Software stats YYYY-MM-DD"); the numbers come from the repositories, so list it in the
   change table with the repositories as the source. If a clone fails, leave the file as it
   is and say so in the PR.

f2. **Generated files** — after every edit, run `python3 scripts/generate.py` and commit what
   it rewrites with the change that caused it (`check_cv.py` warns W-generated until you do).
   It rewrites the venue profile, the health-funder sentence, the counts the narratives
   quote (`data/cv-numbers.tex`) and the citation-impact lines; the narratives print the
   counts with `\cvnumber{…}`, so a new paper or grant updates them without touching
   Jim's text. List each rewritten file in the change table with "scripts/generate.py" as
   the source. `data/gaps.tex` (the review copy's orange "Missing:" lines) is one of the
   files it rewrites: say in the PR how many entries have gaps
   (`python3 scripts/gaps.py --list`) and which this PR filled. A W-numbers warning (a number hard-coded in a narrative) is Jim's to fix:
   suggest the `\cvnumber` in the PR (hard rule 3).

f3. **Tag new venues and funders** — a journal article or `conference`/`abstracts` entry
   whose venue isn't in `data/venues.yaml`, or a grant whose `agency` isn't in
   `data/funders.yaml`, stops its generator (W-venues, W-funders). Propose the tag from
   evidence; don't ask Jim every time. Give every new record a `source` (the URLs, or
   "Jim, issue #N") and put the same evidence in the change table.
   - **Venue `field`** (health, hci, computing; multidisciplinary for journals). Look up
     (1) the venue's own scope statement (the journal's aims-and-scope page; for a
     conference, its call for papers or the ACM DL series page) and (2) its OpenAlex source
     (`https://api.openalex.org/sources?search=<name>&api_key=$OPENALEX_API_KEY`, the
     `topic_share` field): the domain or field holding the largest share. Health: Health
     Sciences, or Medicine, Nursing or Health Professions. HCI: the Human-Computer
     Interaction subfield. **Auto-merge** when both sources are retrieved this run and agree,
     and the top share is at least 50%. **needs-review** (a "Questions for Jim" line: "Is
     <venue> a health venue? Scope says …; OpenAlex …") when they disagree, the top share is
     under 50%, a source can't be reached (OpenAlex needs the API key; without it, one
     source is not enough), or the venue would be the first of a new field. A spelling of a
     listed venue goes in its `aka` or `match` (auto-merge, the entry itself as the source).
   - **Funder `sector`** (who funds the work, not its topic). A new spelling of a listed
     funder goes in its `agency` list (auto-merge). A new funder: **auto-merge** only when it
     is a granting council or a health research charity whose own mandate page (cite it)
     names its sector (CIHR and PHAC: health; NSERC: nse; SSHRC: ssh). A university's own
     fund is `university` whatever its name ("UW CIHR RIF"); companies and
     industry-partnership programs are `industry`. Anything else: `sector: unclassified`
     (never printed, never blocks) and a question in the PR (`needs-review`).
   - Changing an existing record's field or sector is a correction: its own commit, from
     Jim, `needs-review`.

g. **Software DOIs** — Jim's repositories get a Zenodo DOI when a release is archived. For
   each software entry under `\addtocategory{software}` in `main.tex` that has a GitHub URL
   and no `doi`, look the repository up on Zenodo
   (`https://zenodo.org/api/records?q="<owner>/<repo>"&all_versions=true`) and DataCite
   (`https://api.datacite.org/dois?query=relatedIdentifiers.relatedIdentifier:*<owner>/<repo>*`).
   A record whose related identifier is that repository is a match: replace the entry's
   `howpublished`/`url` with `doi = {<conceptdoi>}` (the concept DOI, which resolves to the
   latest version, not one release's DOI), as was done for `wallace_chickadee`. It is a
   correction to an existing entry, so it gets its own commit. Leave other entries that cite
   the same repository (e.g. the `wallace2026interdisciplinary` report) for Jim to decide.

h. **Citation figures** — never query Google Scholar (it can't be done reliably and isn't
   allowed). Read the date on the Google Scholar line at the top of PUBLICATIONS in
   `main.tex`, and `exported:` in `data/citation-impact.yaml` (SciVal). When either is more
   than a year old, or it is October to December of an odd year (the APR is due at the end of
   December), ask Jim in your final message for a new Google Scholar screenshot or SciVal
   export. Update the Google Scholar line only from figures Jim gives (an issue, a comment or
   an attached screenshot), with the date he took them, as its own commit
   (`needs-review`); a SciVal export goes through `scripts/citation_impact.py`.

i. **Deployment impact** — `data/impact.tex` tracks, in its `% Search:` comments, work that
   is used beyond its paper (Quantum Cats, …). For each name, search Jim's mail
   (same window as 2c) and the web (news and outreach pages of the organizations using it:
   IQC, museums, science centres, school boards). A new venue, programme, release or reach
   figure goes on that entry's line only when an official page or message from the organization
   deploying it states it outright; give it on the `% Source:` comment. Anything else (a partner
   that is "interested", a figure from a colleague's email, plans) is a question for Jim.
   Adding a line to the existing one is an addition; changing what it already says is a
   correction (its own commit). Also check that the entry's URL still resolves to the work,
   and report a dead or redirected link as a question.

j. **New deployments to track** — look for work of Jim's that others now use and that
   `data/impact.tex` doesn't track yet:
   - **Mail** (same window as 2c): `exhibit`, `exhibition`, `museum`, `science centre`,
     `outreach`, `classroom`, `curriculum`, `teachers`, `educator`, `deploy`, `deployment`,
     `adopt`, `pilot`, `rollout`, `partners`, `permission to use`, `using your`, `port`,
     `relaunch`, `licence`, `featured`, plus the title of each entry under
     `\addtocategory{software}` in `main.tex`.
   - **Web**: each software title and repository, and the titles of Jim's papers that
     describe a system, game or toolkit, with words like museum, exhibition, classroom,
     school, hospital, public health unit, deployed or adopted. On GitHub, forks or
     dependents of his repositories by an organization (not an individual).
   A candidate is real when an organization other than Jim's lab (a university institute, museum,
   school board, health agency, company) uses or distributes the work, and a public page from
   it or an official message says so. For each one:
   - If the work has a `scholar.bib` entry, add a tracking block to `data/impact.tex`
     (`% Search:`, `% Source:`, and a line only with what that source states), as for
     Quantum Cats.
   - If it doesn't (the game or tool itself was never listed), add its entry as `CLAUDE.md`
     says for software, with authors only from a credits list, README or page you retrieved,
     then the block.
   - Always put it in "Questions for Jim" ("Track X? Its deployment line says …") and label
     the PR `needs-review`: which works are tracked is Jim's call, so he confirms each new one.
   A colleague's mention of interest, a plan or a pending agreement is not a deployment yet:
   note it in your final message only.

k. **Entry detail** (`CLAUDE.md` → Entry detail) — run `python3 scripts/gaps.py --list`.
   For each gap there (review-period entries first), look for a source that states the fact:
   - **Mail** (no date window; the event may be months old), with the entry's title or
     acronym and year plus: `attendees`, `participants`, `registrations`, `registered`,
     `attendance` (attendance); `submissions`, `accepted`, `acceptance rate`, `front matter`,
     `welcome` (submissions, rates);
     `assigned`, `meta-reviews`, `papers to handle` (editorial loads). Prefer the
     organizers' or chairs' own message after the event (a thank-you, a report, a financial
     closing) to a count from before it; a pre-event count is not attendance.
   - **Web**: the conference site, its proceedings or programme page, the venue's awards
     page, and university news about it (the Games Institute's CHI PLAY 2023 article gave
     that conference's submissions). The ACM Digital Library can't be fetched from Claude
     sessions; when a fact is only in front matter or an editorial there, ask Jim.
   Add a fact only as its source states it, with the source in a `%` comment above the
   entry. Adding to a `note` is an addition; changing what it already says is a correction
   (its own commit). Rerun `python3 scripts/generate.py`, which rewrites `data/gaps.tex`.
   For each review-period gap still open, make sure an open `cv-item` issue asks for it:
   search the open issues for the entry's key first, and add one only if none mentions it
   (one per entry, labels `cv-item` and `apr-2027`; say what is missing, where it goes and
   where Jim can find it, as in #152–#155). A gap Jim says can't be filled is his to add to
   `data/gaps.yaml`; suggest the line in the PR. List the gaps filled and the issues opened
   in the change table and the final message.

## 3. Triage

For each item keep a one-line reason (it goes in the PR, or in your final message if private).

- **Is it Jim's?** DBLP records come from his disambiguated profile. An OpenAlex/Crossref-only
  record needs a University of Waterloo affiliation or a coauthor already on his CV.
- **Already on the CV in another form?** Preprint vs published version, extended abstract vs
  full paper, a changed title: compare authors, venue and year, not just the title. The
  published version of an entry marked "In press" updates that entry (DOI, pages) instead of
  adding a new one.
- **Final?** Add papers only on final acceptance. Conditional acceptances and revise-and-resubmit
  are not CV items yet: mention them only in your final message.
- **Private — never in the repo, the PR or an issue** (the repo is public): rejections (except
  grant decisions, which `grants.bib` records: step 2c), declined or pending invitations, nominations not yet submitted, media
  interviews not yet published, the names of tenure and promotion candidates, reviewing assignments for specific papers, program committee
  discussions, anything about a student beyond the name and degree that goes on the CV, email
  text, and other people's contact details. Cite an email source only as, for example,
  "acceptance email from CHI 2027 PC chairs, 2026-11-20".
- Skip errata, front matter, proceedings volumes and dataset deposits unless the CV already
  lists that kind of thing.

## 4. Edit

Follow `CLAUDE.md` → Conventions. In short:
- **Bib entries** from the retrieved record (Crossref record from `cv-sources` first, then the
  publisher page): key `familyYYYYfirstword`, `\textbf{James R. Wallace}`, `*` only for people
  in `data/trainees.yaml`, `doi` when there is one, `note = {In press}` when not yet published.
  Add the key to exactly one heading, and to `apralsoteaching` if a trainee is an author and the
  entry is in the review period. A workshop proposal or meetup Jim co-organized
  (a CHI EA record: `CLAUDE.md` → "Teaching, research or service" says how to recognise one)
  starts its `note` with `Workshop proposal.` or `Meetup.` and goes in that bullet's APR lists;
  when a record could be either, or a paper, label the PR `needs-review` and ask. Append next to similar entries; don't re-sort.
  A new paper is added with its full information when it is available: DOI, pages, award,
  and its acceptance rate (conference/PACM) or impact factor (journal), usually from the
  acceptance email you found in step 2c. If none can be found yet, add its
  `data/metrics.yaml` line (`none` or `unresolved`).
- **Metrics** (step 2e) → the entry's `note`, as `CLAUDE.md` describes; the `data/metrics.yaml`
  line for each entry you looked up: delete it when you add a figure, otherwise add or
  re-date it. Commit metrics separately from new entries.
- **Review recognitions** → `awards.bib`: if the venue and year already has an `@award`, raise
  its `count`; otherwise add one with `title = {Special recognition for VENUE YYYY Papers
  (exceptional reviews)}` and `date = {YYYY}` (no count for a single one). Order within a year
  follows the file.
- **Reviewing / PC / editorial roles** → the matching list under SCHOLARLY AND PROFESSIONAL
  ACTIVITIES; extend an existing line's years rather than adding a duplicate line, and update
  its `\hlservice[years]`.
- **Grants** → a `@grant` entry in `grants.bib`; **students** → a `@supervision` entry in
  `supervision.bib` (see the comments at the top of each file). **Other awards** → an `@award` entry in
  `awards.bib`; for a paper or talk, also `icon = {award}` on that entry (see the top of
  `awards.bib`).
- **The rest of the record** (step 2c): trainee awards and scholarships, nominations,
  submitted grants, review panels, external reviews, session chairs, media, training,
  mentoring, leaves and student start years, each as `CLAUDE.md` → "Where non-publication
  items go" says. Each award needs a `level`. A kind with no list yet gets its heading
  added to `main.tex` in the same commit.
- Commit additions and corrections to existing entries separately.

## 5. Verify

Follow `.claude/skills/cv-verify/SKILL.md` (read it as a file if the skill isn't loaded).
Launch the verifiers in parallel in one message, giving them only the keys, the diff and
your change table — not your reasoning:
`citation-verifier`, `trainee-checker`, `apr-classifier`, `diff-auditor`, and
`chizen-figures` (with the changed files) when the diff touches `figures/` or `data/*.csv`, or adds a figure anywhere else.
If those agent types aren't available in your session, start general-purpose sub-agents
instead, each with the full text of the matching `.claude/agents/<name>.md` (below its
front matter) as its instructions, followed by the inputs.
If `latexmk` is available, compile `main.tex` and `apr.tex` and run
`python3 scripts/warning_ratchet.py main apr`; CI does both regardless. A warning your change
adds fails CI: fix it, or label the PR `needs-review` and ask. A warning your change fixes
(e.g. a DOI you backfilled) must leave `scripts/warnings-baseline.txt`:
`python3 scripts/check_cv.py --prune-baseline`, or delete the line CI names.

## 6. Label

`auto-merge` only when `scripts/check_cv.py` passes, every verifier that ran returns PASS, and every
change is one of:
- a new publication confirmed against a retrieved record (Crossref/DBLP/publisher page), or
  one Jim reported in an issue, marked `In press`;
- a DOI backfill confirmed by `citation-verifier`;
- a software entry's URL replaced by the concept DOI of the Zenodo record for that repository;
- a review recognition, or a reviewing/PC/editorial role, stated in an official email or by Jim;
- an acceptance rate for the paper's own track, stated in its decision letter, the program
  chairs' email, the front matter or the venue's site; a journal impact factor (new or
  refreshed) stated on the publisher's or Clarivate's page; a `data/metrics.yaml` line;
- a new venue, venue spelling, funder or funder spelling tagged as step f3 allows
  auto-merge, and the files `scripts/generate.py` rewrote.

A rate or impact factor from a third-party compilation or aggregator site, or from a track
you inferred, is `needs-review`.

Everything else is `needs-review`, with a **Questions for Jim** section of one-line yes/no
questions: corrections to existing entries, grants (submitted ones included), supervision
changes (start years and scholarships included), awards other than review recognitions,
nominations, review panels, external reviews, session chairs, media, training, possible
new trainees, review-count backfills, anything unverifiable.

## 7. Open the PR (REST)

```
git push -u origin cv/weekly-YYYY-MM-DD
gh api repos/JimWallace/APR---Waterloo-Health-CV/pulls -f base=main \
  -f head=cv/weekly-YYYY-MM-DD -f title="CV update YYYY-MM-DD: <n> added, <m> updated" \
  -F body=@<body file>
gh api repos/JimWallace/APR---Waterloo-Health-CV/issues/<PR number>/labels -f 'labels[]=<label>'
```
(Create a missing label with `gh api repos/…/labels -f name=<label> -f color=<hex>`.)
Body: the change table (what / where / source), one line per verifier verdict, the questions,
and full verifier tables in a collapsed `<details>` block. Add "Closes #N" for each issue
handled, and comment the PR link on those issues.

Don't merge. The "CV auto-merge" workflow merges `auto-merge` PRs once CI passes.
If nothing needs changing, open no PR.

## 8. Final message (private to Jim)

Short: the PR link and its label (or "no changes"); items skipped and why, including private
ones such as conditional acceptances; the grant details still to collect (step 2c); any request for new citation figures (step 2h); questions; any source that was
unavailable.
