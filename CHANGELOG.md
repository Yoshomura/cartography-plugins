# Changelog

Released versions, newest first, one section per plugin version, headed `## <plugin> <version>`.
Each section is the body of that release, published by `.github/workflows/release.yml` under
the tag `<plugin>-<version>`. The criterion for choosing between major, minor
and patch is in the [README](README.md#which-of-the-three-is-a-human-ruling).

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
