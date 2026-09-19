# Changelog

Released versions, newest first, one section per plugin version, headed `## <plugin> <version>`.
Each section is the body of that release, published by `.github/workflows/release.yml` under
the tag `<plugin>-<version>`. The criterion for choosing between major, minor
and patch is in the [README](README.md#which-of-the-three-is-a-human-ruling).

## feature-spec 1.1.0

**The specification gets a second pass, and the word is "specification".**

- **spec-second-pass** agent, `fable`. Reads the idea and the specification the first pass
  wrote, redoes the challenge and the analysis with a fresh context, and amends the same file
  with what the first pass left out. Every addition is marked `(second pass)`; a decision taken
  with the user is never reversed, a disagreement becomes an open question; what was written
  correctly is not rewritten.
- **spec-writer** moves from `fable` to `opus`, and is now explicitly the first pass.
- **workflow-feature-spec** skill: a `Second pass` section with its four rules and its
  checklist; a project may declare its own template in its `CLAUDE.md`, which replaces the
  shipped one; a project without an idea inbox skips the archive step; the cartography of the
  project, when it has one, joins the material the challenge grounds itself in.
- "spec" becomes "specification" in every sentence of the agents, the skill and the template
  (`# Specification: <topic>`). The identifiers a consuming repository pins do not move: the
  agent names, the skill name, the default paths `docs/specs/spec-<topic>.md` and
  `notes-before-spec-<topic>.md`.

Minor: an agent and a skill section added, nothing removed or renamed. A specification written
with 1.0.0 stays valid; the second pass can be run on it.

## codex-mirror 1.0.0

First release of the `codex-mirror` plugin.

- **codex-mirror** skill with `scripts/sync-codex.py`. Derives `.codex/agents/<name>.toml`
  from every agent of `.claude/agents/` and of every plugin enabled in `.claude/settings.json`,
  read from the installed copy of the plugin; copies `.claude/skills/` to `.agents/skills/`.
  `--check` exits 1 on a missing, stale or orphaned generated file; `--hook` reports and exits
  0.
- **Runtime differences declared once**: rules not auto-loaded by Codex, read-only sandbox for
  an agent whose tools cannot write, `${CLAUDE_PLUGIN_ROOT}` resolved to the installed root, a
  project agent shadowing a plugin agent of the same name.
- **Model table** `references/models.toml`, Claude model name to Codex slug and Claude effort
  to `model_reasoning_effort`, overridable per project and per agent in `.codex/mirror.toml`.
  Compared at each run to the list Codex caches in `~/.codex/models_cache.json`: a retiring
  slug is reported with the replacement Codex names.
- **Ownership markers**: the generated header, or `# codex-mirror: manual` for a file the
  project maintains and lets diverge. A file with neither is never touched.
- **SessionStart hook** at `startup` and `resume`: reports a stale mirror into the session,
  never regenerates.

## git-conventions 1.0.0

First release of the `git-conventions` plugin.

- **committer** agent. Writes a Conventional Commits + Gitmoji message for the staged changes,
  runs the shape check, commits with `-F`. Never stages, never pushes, never rewrites history,
  never commits on the default branch.
- **pr-opener** agent. Opens or updates the pull request of an already pushed branch from its
  commits and diff. Label from the caller or the project, never hardcoded. Never pushes,
  merges or commits.
- **commit-message** skill with `scripts/check_message.py`, exit 1 on any deviation from the
  shape.
- **create-pr** skill. The conventions the agent executes.

## feature-spec 1.0.0

First release of the `feature-spec` plugin.

- **spec-writer** agent. Turns a raw idea into a functional spec, conception only.
- **workflow-feature-spec** skill. Mode selection, challenge, interview, write; hard rules
  (no invented fact, no settled open reflection, no publication); the spec template shipped
  in `references/`. Paths are defaults a project can override.

## cartography 1.1.0

**The cartographer can refresh an artifact in place.**

In 1.0.0 it could only write through the shell, which meant emitting a whole file to change one
row. `Edit` now joins its tool list, so a refresh pass rewrites the affected rows and leaves
everything else untouched, which is what the validator checks.

Creating a file is still a copy of the template followed by filling the rows. The agent has no
`Write`, so it cannot produce an artifact that never went through the template.

The manifest also names Yoshomura as author.

Nothing else changed. A repository pinned to 1.0.0 keeps working exactly as before, and moving
to 1.1.0 invalidates no artifact already committed.

## cartography 1.0.0

First release.

- **cartographer** agent. Maps a repository by functionality rather than by code, and produces
  three artifacts from a single reading: `map.md` for what lives where, one
  `details/<SCENARIO>.md` per usecase, and `refusals.md` for what comes back when the
  deployable says no.
- **scout** agent. Answers one question at one coordinate and returns code. It never explores,
  so it cannot be used as a search agent.
- **cartography** skill. The binding format of the three artifacts, with a template for each.
- **validator**. Checks the form and never the content: frontmatter keys, section order, the
  header blockquote character for character, the case counter, the summary length, orphan
  detail entries, and a banned vocabulary that catches purpose, judgment and supposition.
