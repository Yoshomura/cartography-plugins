# cartography-plugins

A Claude Code plugin marketplace holding two workspace-agnostic plugins: `cartography` and
`feature-spec`. The first is described below; the other has its own section further down.

The commit and pull request conventions this repository follows, and the `committer` and
`pr-manager` agents that apply them, come from the `commit-and-pr` plugin of
[yoshomura-git-managment](https://github.com/Yoshomura/yoshomura-git-managment), declared in
`.claude/settings.json`. The `git-conventions` plugin that used to live here was merged into it;
its `git-conventions-1.0.0` tag stays published for the repositories that pin it.

## What the plugin does

It maps a repository by **functionality**, not by code, and it produces three artifacts that
answer three questions asked at three different moments:

| Artifact | Question | Read |
|---|---|---|
| `docs/map.md` | Where is what, what enters, what leaves | Whole, for impact analysis |
| `docs/details/<SCENARIO>.md` | What one usecase does, and the rules it applies | One at a time, when designing |
| `docs/refusals.md` | What comes back when the deployable says no | Whole, when integrating |

They are committed and **not normative**. The documentation of the system stays the source of
truth; these are measuring instruments, and each says so in its own header.

## What it ships

| Component | Name | Role |
|---|---|---|
| Agent | `cartographer` | The judgment: what to attach to what, what to report, what never to write |
| Agent | `scout` | A lookup at one coordinate, answering one question, returning code |
| Skill | `cartography:cartography` | The format: specification, templates, validator |

The agent and the skill are separated on purpose. A shape reproduced from memory drifts run
after run until two repositories stop being comparable; judgment cannot be templated at all.
They change at different rates, so they live in different files.

## Install

```
/plugin marketplace add Yoshomura/cartography-plugins
/plugin install cartography@cartography-plugins
```

To declare it for a repository, commit this to that repository's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "cartography-plugins": {
      "source": {
        "source": "github",
        "repo": "Yoshomura/cartography-plugins",
        "ref": "2.0.0"
      }
    }
  },
  "enabledPlugins": {
    "cartography@cartography-plugins": true
  }
}
```

The `ref` is what makes the version a property of the **repository** rather than of the
developer's machine: each repository pins its tag, bumps it alone, and the bump is a reviewable
commit. A tag is a release of the whole marketplace, so a repository using several of its
plugins pins one tag and takes them all as they stand at that tag. Keep marketplace
auto-update disabled, otherwise a background refresh walks past the pin.

Two things to know when adopting it:

- A project-declared plugin from an external source does not install itself. The repository
  records the requirement; each developer still runs `claude plugin install`.
- A project's own `.claude/agents/` **overrides** a plugin agent of the same name. Delete the
  local `cartographer.md` and `scout.md` when adopting the plugin, or the plugin's versions
  never take effect.

## The other plugin

### feature-spec

A raw product idea becomes a functional spec through a mandatory sequence: mode selection
(interactive or silent), challenge, interview, write.

| Component | Name | Role |
|---|---|---|
| Agent | `spec-writer` | The conception agent. Grounds the idea in the project's reference material, never invents a missing fact, never settles an open reflection, never publishes |
| Skill | `feature-spec:workflow-feature-spec` | The sequence, the hard rules, the checklist, and `references/spec.template.md` |

Default paths are `docs/Features TODO/` for the idea inbox, `docs/specs/spec-<topic>.md` for
the spec and `docs/archives/<year>/<topic>/notes-before-spec-<topic>.md` for the archived idea.
A project overrides them in its `CLAUDE.md`. What happens to a spec afterwards (validation,
publication, ticket derivation) belongs to the host project.

Install it the same way as `cartography`:

```
/plugin install feature-spec@cartography-plugins
```

The same override caveat applies: a project's own `.claude/agents/spec-writer.md` shadows
the plugin's version.

## The validator

```
python "${CLAUDE_PLUGIN_ROOT}/skills/cartography/scripts/validate.py" docs
```

It checks the **form**, never the content: frontmatter keys, a header blockquote copied
character for character, sections present and in order, the case counter, the summary length,
the refusal mechanisms, orphan detail entries, and a list of banned vocabulary — purpose,
judgment and supposition, the three ways an observation turns into an invention.

Exit 0 when everything conforms, 1 otherwise.

**Consider committing a copy of the validator in each mapped repository.** Shipped only here,
a wrong plugin version validates its own output; committed beside the artifacts, it catches a
map produced by the wrong version, which pinning alone does not cover.

## Security scanning

Every push to `master` and every pull request touching `plugins/` runs
[skill-scanner](https://github.com/cisco-ai-defense/skill-scanner), which looks for prompt
injection, data exfiltration and malicious code patterns in skill and agent content.

```
skill-scanner scan-all plugins/cartography/skills --recursive --fail-on-severity high
skill-scanner scan-all plugins/cartography/agents --recursive --lenient --fail-on-severity high
```

`--lenient` on the agents: they are not skills and carry no `SKILL.md`. The scanner version is
pinned in the workflow, so an update to it is a deliberate commit rather than a run that turns
red on a repository which has not changed.

**HIGH and CRITICAL block the merge. Everything below is reported and does not.** The scanner
describes itself as best-effort, and a gate that fires on every INFO is a gate people learn to
ignore.

The job log carries the findings in full, and each run attaches an HTML report per target as an
artifact. This repository is private on a personal account, where code scanning needs a GitHub
Code Security licence, so nothing here uploads SARIF: it would only be useful to a machine that
ingests it, and there is none.

⚠️ Best-effort detection. A scan returning nothing does not mean the plugin is free of threats.

## Business-agnostic, by construction

No domain term appears in the plugin or in its templates. That is deliberate and it is the
criterion the architecture it serves sets for a shared technical library: if another company,
with entirely different business rules, could use it as-is, it carries no business rule.

## Versioning

**Every version is a Semantic Versioning 2.0.0 string**, `MAJOR.MINOR.PATCH` with an optional
`-prerelease` and `+build`, and no `v` prefix: semver defines the version as `X.Y.Z`, and
`v1.1.0` is a tag name rather than a version. `.github/scripts/semver.py` validates every one
and orders them by semver precedence.

Two levels of version, each in one place and nowhere else:

| Version | Lives in | Read by |
|---|---|---|
| The repository's | `version` in `.claude-plugin/marketplace.json` | The tag, the release, every `ref` that pins this marketplace |
| Each plugin's | `version` in `plugins/<plugin>/.claude-plugin/plugin.json` | Claude Code, to decide that an installed plugin changed |

Setting a plugin's version in its marketplace entry as well would be silently ignored, the
manifest value always winning, and a stale manifest would mask it.

### The tag is a consequence, not an act

A `ref` checks out the whole repository at one commit, so the release unit is the repository.
`.github/workflows/release.yml` posts its version as the tag, exactly, on every push to
`master`: `2.0.0`. Nothing in the workflows names a plugin: a new one is covered the day its
manifest exists. Nobody tags by hand, and a tag that already exists is **never moved**: the job
fails instead. A repository pinned to a tag must receive the same bytes forever, and a tag that
slides is the one failure the pin exists to prevent.

The same workflow refuses a pull request that changes `plugins/<plugin>/` without raising that
plugin's version, that changes a plugin or the catalog without raising the repository version,
or that raises the repository version without its `## X.Y.Z` section in `CHANGELOG.md`. Content
merged without a bump publishes no tag, so no consuming repository can ever reach it: it is
merged and unreachable, which is worse than not merged.

Before 2.0.0 each plugin was tagged on its own, as `<plugin>-X.Y.Z` (`cartography-1.1.0`,
`feature-spec-1.0.0`, `git-conventions-1.0.0`), and the single-plugin era left `1.1.0`. Those
tags stay published and are never moved or reused; they are not semantic versions, and no new
tag takes that form.

### Which of the three is a human ruling

The workflow checks that each number is semver and goes up. It says nothing about the level,
because the level is a statement about what a repository pinned to the previous tag would
suffer, and only a person knows that. A plugin moves by the level of its own change; the
repository moves by the highest level among the plugins it releases, and a plugin removed from
the catalog is a major. The criterion is short enough to be read rather than debated:

| Level | What justifies it |
|---|---|
| **major** | A plugin, an agent or a skill removed or renamed, a `${CLAUDE_PLUGIN_ROOT}` path moved, a format change that invalidates artifacts already committed in a consuming repository |
| **minor** | A plugin, an agent, a skill, a tool or a format section added, artifacts already committed staying valid |
| **patch** | Wording, a comment, a validator fix that changes no format |

The install snippets above carry the tag literally. They are documentation, not declarations,
so nothing breaks the day one drifts. The workflow checks that each `ref` is the repository
version for that reason.
