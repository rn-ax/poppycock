# poppycock

Shared config other `rn-ax` repos build on instead of repeating themselves.

## Settings app

`.github/settings.yml` is the shared base config for the [Settings app](https://github.com/repository-settings/app). Other repos point their own `.github/settings.yml` at this one with `_extends: poppycock` to inherit common repository defaults.

The `branches` protection block in that config has no effect while a repo stays private under the `rn-ax` org's GitHub Free plan — branch protection (and rulesets) for private repos requires GitHub Team, or making the repo public. `gh api repos/<org>/<repo>/branches/main/protection` confirms this with a 403: "Upgrade to GitHub Pro or make this repository public to enable this feature." The block is kept in the config so protection takes effect automatically if either condition changes later.

## Renovate preset

`default.json` is the shared [Renovate](https://docs.renovatebot.com/) config. Other repos point at it with:

```json
{
  "extends": ["github>rn-ax/poppycock"]
}
```

It groups GitHub Actions and `mise` tool-version updates into weekly PRs and keeps action refs pinned to a commit SHA with a version comment (the `@<sha> # v4` convention used across this org).
