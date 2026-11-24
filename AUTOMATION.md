# How this repo updates itself

| When | What runs | Result |
|---|---|---|
| Sundays 18:07 (Toronto) | `CV sources` workflow | Fetches DBLP, OpenAlex and Crossref records and saves them on the `cv-sources` branch, so Claude can check entries even where it can't reach those sites. |
| Weekly (your scheduled Claude task) | `automation/weekly-update.md` | Claude adds new papers and DOIs, open `cv-item` issues and items from your Outlook mail and calendar, with leads from Slack (acceptances, review recognitions, PC roles, talks, session chairs, trainee scholarships, nominations, submitted grants, review panels, external reviews, media, training…), fills in missing acceptance rates and journal impact factors (`scripts/missing_metrics.py`, refreshing impact factors each summer), has sub-agents verify every change (plus `chizen-figures` for figures), and opens one PR on a `cv/` branch. It also follows up last week's PRs: answer its questions in a PR comment and the next run applies them. |
| Weekly, Monday 9:00 (a task on your Mac) | `automation/documents-update.md` | Claude reads the documents added to your iCloud CV folder that week (notices of award, award letters, SCP reports, decision letters, committee paperwork), read-only, adds what they record and opens a `cv/documents-` PR. It runs on the Mac because iCloud can't be reached from the cloud; if the Mac was asleep, it runs when it wakes. |
| Every PR | `CV build` | Deterministic checks (`scripts/check_cv.py`), compiles both PDFs, fails on any error and on any warning not in `scripts/warnings-baseline.txt` (see `scripts/warning_ratchet.py`), reports what changed in the PDF text, blocks PRs labelled `needs-review`. A PR that adds lines to the baseline or changes the checks fails the `ratchet` job, so you merge it by hand. |
| `CV build` passes | `CV auto-merge` | Merges PRs you open (including ones Claude opens for you in a chat) automatically. Merges the weekly job's `cv/` PRs only if they're labelled `auto-merge`. Draft PRs and `needs-review` PRs never merge. |
| Every push to `main` | `CV build` → release | Latest PDFs at Releases → `cv-latest` (Wallace-CV.pdf, Wallace-CV-APR.pdf). |
| Tuesdays | `Template update` | If the template repository (`cv.toml` [template]) has a newer release, opens a PR updating `template/` to it: `auto-merge` for a patch release (or a minor release from 1.0 on), `needs-review` when the release can change the interface (see `template/CHANGELOG.md`). |
| Push to `main`, and every 3 hours | `Overleaf sync` (optional) | Pushes `main` to Overleaf; edits made in Overleaf come back as an auto-merging PR. |

The weekly job labels a PR `auto-merge` only when the checker passes, every verifier it ran
(`.claude/agents/`) passes, and every change is a verified publication, a DOI, a review
recognition or a reviewing/PC role. Grants, supervision, other awards, corrections, possible
new trainees and anything unverifiable get `needs-review` and a "Questions for Jim" list.
Private things it finds in email (rejections, conditional acceptances, invitations) go only in
its final message to you, never in the public repo.

## The scheduled task

Create a weekly scheduled task in Claude (Monday morning, after the Sunday `CV sources` run)
with this prompt:

> Update my CV. Attach the GitHub repo JimWallace/APR---Waterloo-Health-CV with push access,
> clone it, and follow automation/weekly-update.md in it exactly. Use my Microsoft 365
> connector for the mail and calendar steps. Don't merge the pull request yourself.

The task needs your GitHub connection (to push and open PRs) and the Microsoft 365 connector.
For the Slack step (step 2d2), its cloud environment also needs a Slack **user** token
(`xoxp-…`, scopes `search:read`, `channels:history`, `groups:history`, `im:history`,
`mpim:history`, `users:read`, `files:read`) under Network secrets; without one the step is
skipped. Slack gives leads only; the CV entries still come from official records.

## The documents task (on your Mac)

`automation/documents-update.md` runs in Claude Code on your Mac, in your local clone of this
repo, and reads your iCloud CV folder in place. It needs Claude Code (`claude`), `gh` signed in
to GitHub with push access, `git` and `python3`, and the folder set to **Keep Downloaded** in
Finder. Change the two paths at the top, then save this as
`~/Library/LaunchAgents/ca.uwaterloo.cv-documents.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>ca.uwaterloo.cv-documents</string>
  <key>ProgramArguments</key><array>
    <string>/bin/zsh</string><string>-lc</string>
    <string>
REPO="$HOME/src/APR---Waterloo-Health-CV"
DOCS="$HOME/Library/Mobile Documents/com~apple~CloudDocs/CV"
cd "$REPO" &amp;&amp; claude -p "Follow automation/documents-update.md in this repository exactly. The documents folder is $DOCS (read-only). The local clone is $REPO. Don't merge the pull request yourself."   --add-dir "$DOCS"   --allowedTools "Bash(git:*)" "Bash(gh api:*)" "Bash(python3 scripts/*)" "Bash(find:*)" "Bash(ls:*)" Read Grep Glob Agent "Edit(./**)" "Write(./**)"   --disallowedTools "Edit(/$DOCS/**)" "Write(/$DOCS/**)"
    </string>
  </array>
  <key>StartCalendarInterval</key><dict>
    <key>Weekday</key><integer>1</integer><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer>
  </dict>
  <key>StandardOutPath</key><string>/tmp/cv-documents.log</string>
  <key>StandardErrorPath</key><string>/tmp/cv-documents.log</string>
</dict></plist>
```

Then `launchctl load ~/Library/LaunchAgents/ca.uwaterloo.cv-documents.plist`. To run it now:
`launchctl start ca.uwaterloo.cv-documents`. Its final message is in `/tmp/cv-documents.log`.
`--add-dir` lets Claude read the folder; the `--disallowedTools` rules forbid writing to it,
and with `-p` any command not in `--allowedTools` is refused rather than asked about.

## One-time setup

1. **Actions permissions** — Settings → Actions → General → Workflow permissions: choose
   "Read and write permissions" and tick "Allow GitHub Actions to create and approve pull requests".
2. **Labels** — `auto-merge`, `needs-review`, `cv-item`
   (`gh label create auto-merge -c 0E8A16; gh label create needs-review -c D93F0B; gh label create cv-item -c 1D76DB`).
3. **First records** — Actions → CV sources → Run workflow, so the first weekly run has data.
4. **Optional variables** (Settings → Secrets and variables → Actions → Variables):
   `ORCID`, `OPENALEX_AUTHOR_ID` (the CV sources log shows the one it resolved), `CONTACT_EMAIL`.
5. **Optional, once things work** — a ruleset on `main` requiring a pull request and the
   status checks `lint` and `compile` (not `gate` or `ratchet`; they only run on some PRs, and
   `ratchet` failing means "merge by hand", which a required check would forbid). Don't require
   approvals, or nothing can auto-merge. Skip this if you use Overleaf option A below:
   Overleaf's GitHub button pushes straight to `main`, which the ruleset would block.
6. **Optional: instant `@claude`** — add a `CLAUDE_CODE_OAUTH_TOKEN` secret (from
   `claude setup-token`, uses a Claude subscription) and install https://github.com/apps/claude.
   Without it the `Claude` workflow does nothing and `cv-item` issues wait for the weekly run.

## Overleaf: pick one

**A. Keep Overleaf's GitHub button (no setup).** After PRs merge, open Overleaf and use
Menu → GitHub → *Pull GitHub changes into Overleaf* before editing, and *Push Overleaf changes
to GitHub* when done. Your pushes go straight to `main`. If both sides changed, Overleaf pushes
to a dated branch; open a PR from it and it auto-merges once CI passes (if it merges cleanly).

**B. Automatic mirror (Overleaf's Git integration).**
1. Overleaf → Account Settings → Git integration → create a token. Add it as the repo secret
   `OVERLEAF_GIT_TOKEN`.
2. Add the variable `OVERLEAF_PROJECT_ID` (the id in `overleaf.com/project/<id>`).
3. In Overleaf, unlink the GitHub sync for this project, so there is one sync path, not two.
4. Actions → Overleaf sync → Run workflow. The first run opens a one-time PR joining the two
   histories (it changes no files); once it merges, `main` mirrors to Overleaf from then on.
   If the LaTeX differs between the two at that moment, the run stops and says how to proceed.

Edit tooling (`.github/`, `.claude/`, `automation/`, `scripts/`, `data/`, `CLAUDE.md`) on
GitHub, not Overleaf: the sync keeps the GitHub copies of those. Overleaf comments and tracked
changes can be lost when files change underneath them through Git, so resolve them before a sync.
