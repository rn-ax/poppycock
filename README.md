# poppycock

Shared config other `rn-ax` repos build on instead of repeating themselves.

## Settings app

`.github/settings.yml` is the shared base config for the [Settings app](https://github.com/repository-settings/app). Other repos point their own `.github/settings.yml` at this one with `_extends: poppycock` to inherit common repository defaults.

## Renovate preset

`default.json` is the shared [Renovate](https://docs.renovatebot.com/) config. Other repos point at it with:

```json
{
  "extends": ["github>rn-ax/poppycock"]
}
```

It groups GitHub Actions and `mise` tool-version updates into weekly PRs and keeps action refs pinned to a commit SHA with a version comment (the `@<sha> # v4` convention used across this org).
