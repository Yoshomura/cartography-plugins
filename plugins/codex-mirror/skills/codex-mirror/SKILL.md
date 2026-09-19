---
name: codex-mirror
description: Regenerate or check the Codex mirror of a project's Claude Code setup - every agent of .claude/agents/ and of each enabled plugin as a .codex/agents/*.toml, .claude/skills/ copied to .agents/skills/, models mapped through a table. Use after editing or adding an agent or a skill, after installing or updating a plugin that ships agents, when the SessionStart hook reports a stale mirror, and as a gate step with --check. Never edits a Claude Code definition; the mirror is derived, never the source.
license: MIT
allowed-tools:
  - Bash(python *sync-codex.py*)
  - Bash(ls *)
  - Read
  - Glob
---

# Codex mirror

Codex reads its subagents from `.codex/agents/*.toml` and nowhere else: not from a plugin, not
from `.claude/agents/`. A project that runs the same agents under Claude Code and under Codex
therefore needs a second copy of each definition, and a second copy maintained by hand drifts.
This skill derives the copy from the source, every time, and checks that it has been derived.

**`.claude/` is the source. `.codex/agents/` and `.agents/skills/` are generated.**

```
.claude/agents/<name>.md            ─┐
<plugin>/agents/<name>.md            ├─ sync-codex.py ─►  .codex/agents/<name>.toml
  (every plugin enabled in           │
   .claude/settings.json)           ─┘
.claude/skills/                     ─── sync-codex.py ─►  .agents/skills/
```

## Run it

The script lives in this plugin, at `${CLAUDE_PLUGIN_ROOT}/skills/codex-mirror/scripts/sync-codex.py`.
From the project root:

| Purpose | Command |
|---|---|
| Regenerate | `python "${CLAUDE_PLUGIN_ROOT}/skills/codex-mirror/scripts/sync-codex.py"` |
| Gate: fail if anything is stale | `python "${CLAUDE_PLUGIN_ROOT}/skills/codex-mirror/scripts/sync-codex.py" --check` |
| Session start: report only | `python "${CLAUDE_PLUGIN_ROOT}/skills/codex-mirror/scripts/sync-codex.py" --hook` |

`${CLAUDE_PLUGIN_ROOT}` is set while this skill runs. From a context that does not have it, such
as a project's gate script, locate the installed copy: newest version under
`~/.claude/plugins/cache/cartography-plugins/codex-mirror/` when installed through Claude Code,
`~/.codex/plugins/cache/cartography-plugins/codex-mirror/` when installed through Codex. Python
3.11 or newer.

`--check` exits 1 on any generated file that is missing, stale or orphaned, and prints each one
on a `RED` line. `--hook` prints the same lines and always exits 0: it is what the plugin's
`SessionStart` hook runs, so a session opens knowing the mirror is out of date without being
blocked by it. Regenerating stays a deliberate command.

## What the script decides, once, for every agent

- **Rules.** Codex does not load `.claude/rules/*.md` by their `paths:` frontmatter. When the
  project has that directory, every generated agent is told to glob the rules and read the
  ones that match what it is about to touch.
- **Skills.** Named as in the source. The project's own skills are found in `.agents/skills/`;
  a plugin's skills are installed in Codex through the plugin. `<plugin>:<skill>` reads as
  `<skill>`.
- **Sandbox.** An agent whose declared `tools:` contain nothing that writes (no `Write`,
  `Edit`, `NotebookEdit`, `Bash`, `PowerShell`) gets `sandbox_mode = "read-only"` and is told
  to return its report instead of writing it. An agent with no `tools:` line has every tool and
  is not read-only.
- **Model and effort.** `model:` and `effort:` go through the table in
  `references/models.toml`: `opus`, `sonnet`, `haiku`, `fable` to a Codex slug; `low` to
  `max` to `model_reasoning_effort`. A Claude model with no entry produces a `WARN` and no
  `model` line, so the agent inherits the session model rather than naming a model Codex does
  not know.
- **`${CLAUDE_PLUGIN_ROOT}`.** A plugin agent that names it is told which installed root it
  means under Codex.
- **Shadowing.** A `.claude/agents/<name>.md` shadows a plugin agent of the same name, as it
  does under Claude Code. Two plugins shipping the same agent name is an error.

## Project overrides: `.codex/mirror.toml`

Same sections as `references/models.toml`, only the keys that change:

```toml
[models]
fable = "gpt-6-astra"          # another slug for one Claude model

[agents.gatekeeper]
sandbox_mode = "read-only"     # force read-only on an agent whose tools could write
model = "gpt-5.6-luna"         # one agent on another model
effort = "medium"
```

Absent, the plugin's table applies in full: a project that adopts the plugin gets working TOML
without configuring anything.

## Who owns a generated file

The first line of each `.codex/agents/*.toml` says who maintains it.

| First line | Owner | The script |
|---|---|---|
| `# generated from <source> by codex-mirror; ...` | this script | rewrites it when the source changes, removes it when the source disappears |
| `# codex-mirror: manual` | the project | never touches it, lists it as `INFO` |
| anything else | unknown, written before the plugin | never touches it, reports it as `WARN` once per run until the project chooses |

To take an agent over and let it diverge from its Claude Code definition, replace the first
line with `# codex-mirror: manual`. The divergence is then a declared decision, visible in the
file and in every `--check`, and the two runtimes no longer run the same agent: say so in the
project's instructions as well. Deleting the marker hands the file back to the script.

## Models that retire

Codex keeps the model list it fetched last in `~/.codex/models_cache.json`, with a retirement
date and a replacement for models on their way out. The script compares the table to it and
prints a `WARN` for a slug that is gone or retiring, with the replacement Codex names. The file
is an internal cache, not a documented interface: when it is absent or unreadable, nothing is
reported and nothing fails. The table in this plugin stays the source; the cache is the
detector. Updating a slug in the table is a patch release of this plugin, or one line in the
project's `.codex/mirror.toml` until then.

## Adopting the plugin in a project

1. Enable it in `.claude/settings.json` under `enabledPlugins`, next to the plugins whose
   agents should reach Codex. The `SessionStart` hook starts reporting at the next session.
2. Under Codex, add the marketplace once per machine and enable the plugins in the project's
   `.codex/config.toml`:

   ```
   codex plugin marketplace add Yoshomura/cartography-plugins --ref <plugin>-<version>
   ```

   ```toml
   [plugins."codex-mirror@cartography-plugins"]
   enabled = true
   ```

   Codex runs a plugin's hook only after the user has reviewed and trusted it, through
   `/hooks`. Until then the check is the gate's job.
3. Run the regeneration once, commit `.codex/agents/` and `.agents/skills/`: Codex reads the
   committed files, it does not run the script.
4. Add `--check` to the project's gate, so a definition edited without regenerating turns the
   gate red.

## Limits

Never edit a `.claude/agents/*.md`, a plugin's `agents/*.md` or a `.claude/skills/` file from
this skill: the mirror is derived from them, and a fix belongs in the source. Never delete a
file that does not carry the generated header. Never write a model slug that is not in the
table or in the project's override.
