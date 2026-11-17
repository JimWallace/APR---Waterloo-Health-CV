# How this repo updates itself

| When | What runs | Result |
|---|---|---|
| Mondays 06:17 (Toronto) | `CV weekly update` | Claude checks DBLP/OpenAlex/Crossref for new papers and DOIs and handles open `cv-item` issues, has four sub-agents verify every change, and opens one PR. First Monday of the month it also re-checks every entry. |
| You open an "Add to my CV" issue, or write `@claude …` on an issue/PR | `Claude` | Claude adds the item, verifies it, opens a PR. |
| Every PR | `CV build` | Deterministic checks (`scripts/check_cv.py`), compiles both PDFs, blocks PRs labelled `needs-review`. |
| `CV build` passes on a PR labelled `auto-merge` | `CV auto-merge` | Merges it. Claude never merges anything itself. |
| Every push to `main` | `CV build` → release | Latest PDFs at Releases → `cv-latest` (Wallace-CV.pdf, Wallace-CV-APR.pdf). |
| Push to `main`, and every 3 hours | `Overleaf sync` (optional) | Pushes `main` to Overleaf; edits made in Overleaf come back as an auto-merging PR. |

Claude labels a PR `auto-merge` only when the checker passes and all four verifiers
(`.claude/agents/`) pass with nothing unverifiable. Anything else gets `needs-review` and a
"Questions for Jim" list. Corrections to existing entries and full audits are always `needs-review`.

## One-time setup

1. **Claude GitHub App** — install it on this repo: https://github.com/apps/claude
   (or run `/install-github-app` in Claude Code, which also does step 2).
2. **Secret `CLAUDE_CODE_OAUTH_TOKEN`** — run `claude setup-token` on your computer (uses your
   Claude subscription) and add the token under Settings → Secrets and variables → Actions.
   To use an API key instead, add `ANTHROPIC_API_KEY` and change the `claude_code_oauth_token`
   line in `cv-weekly-update.yml` and `claude.yml` to `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`.
3. **Actions permissions** — Settings → Actions → General → Workflow permissions: choose
   "Read and write permissions" and tick "Allow GitHub Actions to create and approve pull requests".
4. **Labels** —
   `gh label create auto-merge -c 0E8A16; gh label create needs-review -c D93F0B; gh label create cv-item -c 1D76DB`
5. **Optional, recommended once things work** — a ruleset on `main` requiring a pull request
   and the status checks `lint` and `compile` (not `gate`; it only runs on some PRs). Don't
   require approvals, or nothing can auto-merge.
6. **Optional variables** (Settings → Secrets and variables → Actions → Variables):
   `ORCID`, `OPENALEX_AUTHOR_ID` (the weekly run log shows the one it resolved), `CONTACT_EMAIL`.
7. **Try it** — Actions → CV weekly update → Run workflow.

## Overleaf: pick one

**A. Keep Overleaf's GitHub button (no setup).** After PRs merge, open Overleaf and use
Menu → GitHub → *Pull GitHub changes into Overleaf* before editing, and *Push Overleaf changes
to GitHub* when done. If both sides changed, Overleaf pushes to a dated branch; open a PR from
it (or ask `@claude` to merge it).

**B. Automatic mirror (Overleaf's Git integration).**
1. Overleaf → Account Settings → Git integration → create a token. Add it as the repo secret
   `OVERLEAF_GIT_TOKEN`.
2. Add the variable `OVERLEAF_PROJECT_ID` (the id in `overleaf.com/project/<id>`).
3. In Overleaf, unlink the GitHub sync for this project, so there is one sync path, not two.
4. Actions → Overleaf sync → Run workflow. The first run opens a one-time PR joining the two
   histories (it changes no files); once it merges, `main` mirrors to Overleaf from then on.
   If the LaTeX differs between the two at that moment, the run stops and says how to proceed.

Edit tooling (`.github/`, `.claude/`, `scripts/`, `data/`, `CLAUDE.md`) on GitHub, not Overleaf:
the sync always keeps the GitHub copies of those. Overleaf comments and tracked changes can be
lost when files change underneath them through Git, so resolve them before a sync.
