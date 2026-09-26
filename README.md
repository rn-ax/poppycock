# poppycock

Shared config other `rn-ax` repos build on instead of repeating themselves.

## Settings app

`settings.yml` (repo root) is the shared base config for the [Settings app](https://github.com/repository-settings/app). Other repos point their own `.github/settings.yml` at this one with `_extends: poppycock` to inherit common repository defaults. `.github/settings.yml` here is poppycock's own repo-specific override (it needs `private: false` since the base template defaults every repo to private).

## EditorConfig

`.editorconfig` is a plain reference copy, not something other repos can remotely extend -- [EditorConfig](https://editorconfig.org/) has no include/inherit mechanism, so a new repo copies this file directly rather than pointing at it. Every `rn-ax` repo has one.

## Renovate preset

`default.json` is the shared [Renovate](https://docs.renovatebot.com/) config. Other repos point at it with:

```json
{
  "extends": ["github>rn-ax/poppycock"]
}
```

It groups GitHub Actions and `mise` tool-version updates into weekly PRs and keeps action refs pinned to a commit SHA with a version comment (the `@<sha> # v4` convention used across this org).

## HA integration CI

`.github/workflows/ha-integration-ci.yml` is a reusable (`workflow_call`) workflow for Home Assistant custom-integration repos (`ha-inteno-router`, `ha-gym-tracker`, ...). It runs hassfest and HACS validation, then, on push to `main` once both pass, tells the user's Home Assistant instance to sync that repo to the latest commit via HACS's websocket API. Callers use it with a thin `ci.yml`:

```yaml
name: CI

on: push

jobs:
  ci:
    permissions:
      contents: read
      pull-requests: write
    uses: rn-ax/poppycock/.github/workflows/ha-integration-ci.yml@main
    secrets: inherit
```

`secrets: inherit` passes through `HOME_ASSISTANT_URL` / `HOME_ASSISTANT_TOKEN` automatically -- these live as org-level secrets on `rn-ax` (scoped to the repos that need them via `--repos`), not duplicated per repo. The calling job's `permissions` block is required too -- GitHub intersects it with what the reusable workflow declares per-job, and without `pull-requests: write` here HACS's PR comment won't actually get posted. Pass `hacs_category: plugin` (or similar) as an `inputs:` override for a repo whose HACS category isn't `integration`.
