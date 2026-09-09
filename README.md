# cartography-plugins

A Claude Code plugin marketplace holding one plugin, `cartography`.

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
        "ref": "v1.1.0"
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
commit. Keep marketplace auto-update disabled, otherwise a background refresh walks past the
pin.

Two things to know when adopting it:

- A project-declared plugin from an external source does not install itself. The repository
  records the requirement; each developer still runs `claude plugin install`.
- A project's own `.claude/agents/` **overrides** a plugin agent of the same name. Delete the
  local `cartographer.md` and `scout.md` when adopting the plugin, or the plugin's versions
  never take effect.

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

## Business-agnostic, by construction

No domain term appears in the plugin or in its templates. That is deliberate and it is the
criterion the architecture it serves sets for a shared technical library: if another company,
with entirely different business rules, could use it as-is, it carries no business rule.

## Versioning

The version lives in `plugins/cartography/.claude-plugin/plugin.json` and **nowhere else**.
Setting it in the marketplace entry as well would be silently ignored, the manifest value
always winning, and a stale manifest would mask it.

Tag a release when the format changes, so a consuming repository can pin it.
