# Changelog

Released versions, newest first, one section per plugin version, headed `## <plugin> <version>`.
Each section is the body of that release, published by `.github/workflows/release.yml` under
the tag `<plugin>-<version>`. The criterion for choosing between major, minor
and patch is in the [README](README.md#which-of-the-three-is-a-human-ruling).

## cartography 2.0.0

**Cartography is reverse engineering, whatever the technology.** Format version 1.1.0.

The plugin was written for one C# hexagonal codebase, and its format, templates, validator and
agents assumed it. It now describes any existing system, from one of two sources declared by a
new optional frontmatter key, `source`, equal variants of the same work:

- **`source: code`**: existing code in any language. The usecase is the path of the existing
  file implementing it (`.cs`, `.ts`, `.py`, `.java`, `.go`, `.kt`...), never a file to
  create. The validator checks only that it is a file path with an extension.
- **`source: functionality`**: a functionality observed or described, with no code to read: a
  product studied from the outside, a user interface, network traffic, a specification,
  documentation. The usecase is a plain name, unique in the set (case-insensitive); a value
  holding `/` or ending on a file extension is refused. `What it does` opens on
  `> Source: the functionality. Observed, not interpreted.`, and the detail and refusal
  blockquotes have their own exact text. Anchors read `— observed YYYY-MM-DD`, tested may be
  `0`, and refusals record `—` for an exception or a code the functionality does not show.

Also:

- **One template set per source**: `map`, `detail-entry` and `refusals` each come as
  `<artifact>.code.template.md` and `<artifact>.functionality.template.md`, with neutral
  placeholders. The former `<artifact>.template.md` files are gone.
- The tested counter rests on the case ID carried by test names or identifiers of whatever
  framework the repository uses; the .NET `DisplayName` was one example.
- The `cartographer` and `scout` agents assume no language and no folder layout. The scout
  accepts an observed coordinate and returns the observed evidence as well as code.
- The validator checks that every file of a set declares the map's source.
- Validator fixtures and a unittest runner under `tests/cartography/`.

Major: the template paths under `${CLAUDE_PLUGIN_ROOT}` moved, and the plugin changes nature,
from mapping one kind of codebase to reverse engineering any system. The format itself only
grows: an artifact set written with format 1.0.0 carries no `source`, reads as `source: code`,
and still passes the validator unchanged.

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
