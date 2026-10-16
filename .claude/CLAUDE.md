# cartography-plugins

A Claude Code plugin marketplace: `plugins/<plugin>/` holds each plugin, and
`.claude-plugin/marketplace.json` is the catalog. The README describes the plugins, their
install and the release process.

## Versioning: always semver

- **Every version is a Semantic Versioning 2.0.0 string**: `MAJOR.MINOR.PATCH`, optionally
  `-prerelease` and `+build`, never a `v` prefix, never a plugin-name prefix. This holds for
  the repository version (`version` in `.claude-plugin/marketplace.json`), each plugin version
  (`version` in `plugins/<plugin>/.claude-plugin/plugin.json`), every tag, and every `ref`
  that pins this marketplace. `python3 .github/scripts/semver.py valid <version>` checks one.
- **The tag is the repository version, exactly**, posted by `.github/workflows/release.yml`.
  Never tag by hand, never move or reuse a published tag. The older `<plugin>-X.Y.Z` tags and
  `1.1.0` stay as they are; no new tag takes their form.
- **A change under `plugins/<plugin>/` raises that plugin's version and the repository
  version**; a catalog change raises the repository version. A raised repository version gets
  its `## X.Y.Z` section in `CHANGELOG.md`, with a `### <plugin> <version>` subsection per
  plugin it changes.
- **The level is the human's ruling**: propose one from the README table
  (`## Versioning`), then ask. Never pick it silently.

## Commits and pull requests

They go through the `commit-and-pr` plugin of yoshomura-git-managment, declared in
`.claude/settings.json`: the `committer` and `pr-manager` agents, on a branch, never on
`master`. Install it once with `/plugin install commit-and-pr@yoshomura-git-managment`.
