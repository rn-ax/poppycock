# poppycock

Shared config other `rn-ax` repos build on instead of repeating themselves — see `README.md` for what's actually here (the Renovate preset, the Settings app base config, the reusable HA integration CI workflow).

## This repo is public

Nothing here should ever reveal a secret, a private hostname/IP, or anything identifying beyond the `rn-ax` org itself. Concretely, before committing or opening a PR:

- No API keys, tokens, or credentials of any kind — the `deploy` job in `ha-integration-ci.yml` reaches a real Home Assistant instance via secrets that stay in each *calling* repo (`HOME_ASSISTANT_URL`/`HOME_ASSISTANT_TOKEN`, passed through with `secrets: inherit`), never hardcoded or logged here.
- No real private-network hostnames or IPs (e.g. a `.lan` address, a home router's admin IP) in code, comments, or workflow logs.
- No personal GitHub handles where the org handle (`@rn-ax`) already satisfies whatever needs a `codeowners`-style field.
- Commit history counts too, not just current file content — something committed and later removed is still public once pushed. If anything sensitive ever lands here, it needs history rewritten (`git filter-repo` + force-push) and coordinating with whoever owns this repo, not just a follow-up commit that deletes it.

## Pinning GitHub Actions

Every `uses:` reference in any workflow in this repo (and in any repo that consumes this one's shared workflow) is pinned to a full commit SHA with a trailing `# <tag-or-branch>` comment, e.g. `actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4` — never a mutable ref like `@main`, `@master`, or a bare `@v4` tag, since any of those can be force-moved to point at different (and unreviewed) code after the fact.

Renovate's `helpers:pinGitHubActionDigests` preset (in `default.json`) keeps these pins current automatically going forward, but it only *updates* an existing pin — it doesn't retroactively pin a reference that's still on a mutable ref. When adding a new `uses:` line to a workflow, resolve and pin its SHA by hand at that point rather than leaving it unpinned for Renovate to "fix later": `gh api repos/<owner>/<repo>/commits/<tag-or-branch> --jq .sha`.

For an action with a real tagged release (most of them), the comment names that tag: `# v4`, `# 22.5.0` — whatever the tag is actually called, not a normalized `v`-prefixed guess. For a third-party action that's only ever used at a branch HEAD because it doesn't tag releases (e.g. `home-assistant/actions`, which HA's own docs say to use at `@master`), it still gets pinned to a SHA — the comment just names that branch instead of a tag: `# master`. Either way, the comment should let someone cross-reference it back to a real tag or branch on the upstream repo, not just be a version-shaped label.

The one exception is a reference to something the `rn-ax` org itself owns and reviews — e.g. `uses: rn-ax/poppycock/.github/workflows/ha-integration-ci.yml@main` in a calling repo's `ci.yml`. Those can stay on a live branch ref unpinned: the SHA-pinning convention exists to guard against a third party silently changing what a mutable tag points to, which isn't a risk for a repo already inside this org's own review process.

## scripts/hacs_deploy.py vs. the inline copy in ha-integration-ci.yml

`ha-integration-ci.yml`'s `deploy` job embeds its own copy of this script's logic as an inline `shell: python3 {0}` block rather than checking out and running `scripts/hacs_deploy.py` directly. This isn't a style choice: that job runs in the *calling* repo's context (e.g. `ha-gym-tracker`), and poppycock is private, so a real `actions/checkout` of poppycock from a different repo's workflow run has no read access to it — the calling repo's own `GITHUB_TOKEN` doesn't span other repos in the org. Inlining sidesteps needing that checkout at all, since GitHub resolves a reusable workflow's own YAML content without requiring the job's token to read the repo it lives in.

`scripts/hacs_deploy.py` still exists as a real, lintable, locally-runnable file for development and manual testing (`mise.toml` pins the Python version for it) — it's just not what CI actually executes. Keep the two copies in sync by hand whenever either one changes.
