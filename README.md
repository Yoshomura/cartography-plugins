# cartography-plugins

A Claude Code plugin marketplace holding three workspace-agnostic plugins: `cartography`,
`git-conventions` and `feature-spec`. The first is described below; the other two have their
own section further down.

## What the plugin does

It reverse engineers an existing system and maps it by **functionality**, not by code, and it
produces three artifacts that answer three questions asked at three different moments:

| Artifact | Question | Read |
|---|---|---|
| `docs/map.md` | Where is what, what enters, what leaves | Whole, for impact analysis |
| `docs/details/<USE-CASE>.md` | What the implementation of one use case does, and the rules it applies | One at a time, when designing |
| `docs/refusals.md` | What comes back when the deployable says no | Whole, when integrating |

They are committed and **not normative**. The specification of the system stays the source of
truth; these are measuring instruments, and each says so in its own header.

The specification they are compared with is organized by **feature** (a functionality) and
**use case** (one goal reached by one means), each use case holding its **scenarios** and
**rules**, each feature its **invariants**, all with fixed identifiers such as
`SIGNIN-PASSKEY-SCENARIO-2`. The `feature-spec` plugin writes that specification.

The system is read from one of two sources, declared by the `source` key of every artifact and
equal variants of the same reverse engineering:

| `source` | What is read | The implementation is |
|---|---|---|
| `code` | Existing code, in any language and any folder layout | the path of the existing file implementing the use case |
| `functionality` | A functionality observed or described: a product studied from the outside, a user interface, network traffic, a specification, documentation | a name, the title of the use case, unique in the set |

An absent `source` reads `code`.

## What it ships

| Component | Name | Role |
|---|---|---|
| Agent | `cartographer` | The judgment: what to attach to what, what to report, what never to write |
| Agent | `scout` | A lookup at one coordinate, answering one question, returning code or the observed evidence |
| Skill | `cartography:cartography` | The format: specification, one template set per source, validator |

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
        "ref": "cartography-2.0.0"
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
commit. Tags are named `<plugin>-<version>`, so a repository using several plugins of this
marketplace pins one tag and takes the versions of the others as they stand at that tag. Keep marketplace auto-update disabled, otherwise a background refresh walks past the
pin.

Two things to know when adopting it:

- A project-declared plugin from an external source does not install itself. The repository
  records the requirement; each developer still runs `claude plugin install`.
- A project's own `.claude/agents/` **overrides** a plugin agent of the same name. Delete the
  local `cartographer.md` and `scout.md` when adopting the plugin, or the plugin's versions
  never take effect.

## The other two plugins

### git-conventions

Commit and pull request conventions, executed by two narrow agents so that neither the staged
diff nor the branch diff enters the caller's context.

| Component | Name | Role |
|---|---|---|
| Agent | `committer` | Writes the message for the staged changes, checks its shape, commits. Never stages, pushes or rewrites history, never commits on the default branch |
| Agent | `pr-opener` | Writes title and body from the commits, opens or updates the pull request. Requires the branch to be pushed already; never pushes, merges or commits |
| Skill | `git-conventions:commit-message` | The shape `<type>(<scope>): <gitmoji> <description>`, `+ ` details, `Co-authored-by` attribution, and `scripts/check_message.py` that refuses any other shape |
| Skill | `git-conventions:create-pr` | The pull request conventions: optional project label, body sections, signature line, never the "Generated with Claude Code" footer |

The pull request label is not hardcoded: it comes from the caller's prompt or from the
project's `CLAUDE.md`, and a project that declares none gets a pull request without a label.

```
python "${CLAUDE_PLUGIN_ROOT}/skills/commit-message/scripts/check_message.py" <message file>
```

### feature-spec

A raw product idea becomes one feature of the functional specification through a mandatory
sequence: mode selection (interactive or silent), challenge, interview, write.

| Component | Name | Role |
|---|---|---|
| Agent | `spec-writer` | The conception agent. Grounds the idea in the project's reference material, never invents a missing fact, never settles an open reflection, never publishes |
| Skill | `feature-spec:workflow-feature-spec` | The vocabulary, the sequence, the hard rules, the checklist, and the templates `references/feature.template.md` and `references/use-case.template.md` |

The specification is organized by feature and use case:

```
docs/specifications/
├── features.md                       index of the features
└── sign-in/                          one folder per feature
    ├── sign-in.md                    goal, facts, invariants, use cases, decisions, open questions
    └── sign-in-with-passkey.md       one file per use case: goal, rules, scenarios
```

A use case is one goal reached by one means: two means of reaching the same goal are two use
cases. Invariants, rules and scenarios carry fixed identifiers in full words
(`SIGNIN-INVARIANT-1`, `SIGNIN-PASSKEY-RULE-1`, `SIGNIN-PASSKEY-SCENARIO-2`), and tests start
with the identifier they cover.

Default paths are `docs/Features TODO/` for the idea inbox, `docs/specifications/<feature>/`
for the specification and `docs/archives/<year>/<feature>/notes-before-spec-<feature>.md` for
the archived idea. A project overrides them in its `CLAUDE.md` or `AGENTS.md`. What happens to
a specification afterwards (validation, publication, ticket derivation) belongs to the host
project.

Install either one the same way as `cartography`:

```
/plugin install git-conventions@cartography-plugins
/plugin install feature-spec@cartography-plugins
```

The same override caveat applies: a project's own `.claude/agents/committer.md`,
`pr-opener.md` or `spec-writer.md` shadows the plugin's version.

## The validator

```
python "${CLAUDE_PLUGIN_ROOT}/skills/cartography/scripts/validate.py" docs
```

It checks the **form**, never the content: frontmatter keys, a header blockquote copied
character for character from the set of the file's source, sections present and in order, the
scenario counter, the implementation (a file path of any language with source `code`, a unique
plain name with source `functionality`), the anchors of an observed functionality, the summary length, the
refusal mechanisms, orphan detail entries, and a list of banned vocabulary — purpose, judgment
and supposition, the three ways an observation turns into an invention.

Its fixtures live in `tests/cartography/fixtures/`, one folder per set, `pass-*` or `fail-*`:

```
python -m unittest discover -s tests/cartography -v
```

Exit 0 when everything conforms, 1 otherwise.

**Consider committing a copy of the validator in each mapped repository.** Shipped only here,
a wrong plugin version validates its own output; committed beside the artifacts, it catches a
map produced by the wrong version, which pinning alone does not cover.

## Security scanning

Every push to `main` and every pull request touching `plugins/` runs
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

## Business- and technology-agnostic, by construction

No domain term appears in the plugin or in its templates, and no language, framework or folder
convention either. That is deliberate and it is the criterion the architecture it serves sets
for a shared technical library: if another company, with entirely different business rules and
another stack, could use it as-is, it carries no business rule and no technology choice.

## Versioning

Each plugin's version lives in its own `plugins/<plugin>/.claude-plugin/plugin.json` and
**nowhere else**. Setting it in the marketplace entry as well would be silently ignored, the
manifest value always winning, and a stale manifest would mask it.

### The tag is a consequence, not an act

`.github/workflows/release.yml` discovers every manifest under `plugins/*/` on every push to
`master` and posts the matching `<plugin>-X.Y.Z` tag for each: `cartography-1.1.0`,
`git-conventions-1.0.0`. The version part is the semantic version itself, with no `v`: semver
defines a version as `X.Y.Z`, and `v1.1.0` is a tag name rather than a version. The plugin
name is the prefix that lets several plugins share one repository, each on its own line of
versions. Nothing in the workflows names a plugin: a new one is covered the day its manifest
exists. Nobody tags by hand, and a tag that already exists is **never moved**: the job fails
instead. A repository pinned to a tag must receive the same bytes forever, and a tag that
slides is the one failure the pin exists to prevent.

The same workflow refuses a pull request that changes `plugins/<plugin>/` while leaving that
plugin's version alone, and a bump without a `## <plugin> <version>` section in
`CHANGELOG.md`. Content merged without a bump publishes no tag, so no consuming repository
can ever reach it — it is merged and unreachable, which is worse than not merged.

### Which of the three is a human ruling

The workflow checks that the number exists and that it goes up. It says nothing about its
level, because the level is a statement about what a repository pinned to the previous tag
would suffer, and only a person knows that. The criterion is short enough to be read rather
than debated:

| Level | What justifies it |
|---|---|
| **major** | An agent or a skill removed or renamed, a `${CLAUDE_PLUGIN_ROOT}` path moved, a format change that invalidates artifacts already committed in a consuming repository |
| **minor** | An agent, a skill, a tool or a format section added, artifacts already committed staying valid |
| **patch** | Wording, a comment, a validator fix that changes no format |

The install snippets above carry literal tags. They are documentation, not declarations, so
nothing breaks the day one drifts. The workflow compares each `ref` to its plugin's manifest
for that reason.
