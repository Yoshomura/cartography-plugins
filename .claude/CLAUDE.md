# cartography-plugins

A Claude Code plugin marketplace: `plugins/<plugin>/` holds each plugin, and
`.claude-plugin/marketplace.json` is the catalog. The README describes the plugins, their
install and the release process.

## Versioning: two semantic versions, both tagged at the merge

- **Every version is a Semantic Versioning 2.0.0 string**, `X.Y.Z`, never a `v` prefix.
- **The repository version** is what a consumer pins with `ref`. It lives in no file: its tag is
  `X.Y.Z`, computed at the merge from the pull request's release label.
- **A plugin version** is the `version` of the plugin's `plugins/<plugin>/.claude-plugin/plugin.json`,
  never of `.claude-plugin/marketplace.json`. Every pull request that changes `plugins/<plugin>/`
  raises it; the merge tags it `<plugin>--vX.Y.Z`. Never write a version number in a pull
  request body: the tags are computed.
- **Release labels**: every pull request carries exactly one of `release:major`,
  `release:minor`, `release:patch`, `release:none`, set by `create-pr` (run by `pr-manager` or
  the main session). Under any level but `none`, its body carries a `## Release notes` section,
  the notes of the GitHub release. `release:none` only when nothing under `plugins/` or
  `.claude-plugin/` changes.
- **The levels are the human's ruling**: propose the plugin levels and the repository level
  from the README table (`## Versioning`), then ask. Never pick them silently. The repository
  level is at least the highest plugin move; a plugin removed from the catalog is a major.
- **The merge publishes**: `.github/workflows/release.yml` raises the highest repository tag by
  the label's level (`1.0.0` when no release exists), tags the merge commit with it and with
  `<plugin>--vX.Y.Z` for every plugin version not yet tagged, and publishes the release. It
  never commits; `master` changes only through a merged pull request. Never tag by hand, never
  move or reuse a published tag.

## Tests

Run every suite before committing a change to a plugin:

```
python -m unittest discover -s tests/cartography
python -m unittest discover -s tests/feature-spec
python -m unittest discover -s tests/c4
python -m unittest discover -s tests/packaging
```
