# Changelog

Released versions, newest first, one section per plugin version, headed `## <plugin> <version>`.
Each section is the body of that release, published by `.github/workflows/release.yml` under
the tag `<plugin>-<version>`. The criterion for choosing between major, minor
and patch is in the [README](README.md#which-of-the-three-is-a-human-ruling).

## feature-spec 2.1.0

**Business rules, Gherkin scenarios and a checker.**

- "Rule" becomes **business rule**, with identifiers `<FEATURE>-<USE-CASE>-BUSINESS-RULE-<n>`:
  a rule is also an instruction file of a coding agent harness, and the two must never be
  confused. The use case template's section is `## Business rules`.
- Each **scenario** carries a short title, one sentence of 120 characters at most, usable as a
  ticket title, and its Given / When / Then in a `gherkin` block, which says what the sentence
  says and nothing more.
- New `scripts/check_specification.py`: checks the shape of a feature folder or of a whole
  specification folder (identifiers and numbering, sections, use cases listed by the feature,
  scenario sentence and Gherkin). Fixtures and a unittest runner under `tests/feature-spec/`.

Minor: a template section is renamed and a checker is added; a specification written with
2.0.0 keeps its content and needs its `Rules` sections and `RULE` identifiers renamed to pass the
checker.

## cartography 2.1.0

**Business rules and test identifiers.** Format version 2.1.0.

- The vocabulary of the format, the templates and the cartographer speaks of **business rules**:
  the rules table reads `# | Business rule | Specified as`, and `Specified as` holds the
  identifier of a scenario, a business rule or an invariant.
- The tested counter also reads the group, `describe` block or module the tests sit in, and
  compares identifiers ignoring case and treating `-` and `_` as the same character, so that a
  language whose names accept no hyphen, such as Rust, is counted.

Minor: no section, key or column count changes; every artifact written with format 2.0.0 still
passes the validator.

## feature-spec 2.0.0

**A specification organized by feature and use case.** The skill no longer writes one spec file
per idea, `docs/specs/spec-<topic>.md`: it writes one feature, by default under
`docs/specifications/<feature>/`.

- **Vocabulary**: a feature is a functionality; a use case is one goal reached by one means, so
  two means of reaching the same goal are two use cases; a scenario is one way a use case
  unfolds, nominal, variant or failure; a rule belongs to one use case and is written in it
  even when another use case states the same rule; an invariant is a rule of the feature whose
  divergence would be a defect (security, personal data, accessibility), written once.
- **Files**: the feature file `<feature>/<feature>.md` holds the goal, the facts, the
  invariants, the list of use cases, the decisions log, the out of scope and the open
  questions; one file per use case holds its goal, rules and scenarios; the index
  `docs/specifications/features.md` lists the features.
- **Identifiers**: upper case, in full words, fixed: `SIGNIN`, `SIGNIN-PASSKEY`,
  `SIGNIN-PASSKEY-RULE-1`, `SIGNIN-PASSKEY-SCENARIO-2`, `SIGNIN-INVARIANT-1`. Tests start with
  the identifier they cover.
- Worked examples and edge cases become scenarios: a scenario is a worked example with
  validated values.
- One idea is one feature, new or changed in place.

Major: the template `references/spec.template.md` is replaced by `references/feature.template.md`
and `references/use-case.template.md`, and the default output path changes.

## cartography 2.0.0

**Cartography is reverse engineering, whatever the technology, compared with a specification
organized by feature and use case.** Format version 2.0.0.

The vocabulary follows the specification: a detail entry describes the implementation of one
**use case**, its rules point at the identifier of a **scenario**, a **rule** or an
**invariant**, and its counters count scenarios.

- Detail entries are named `details/<USE-CASE>.md`; their frontmatter keys `scenario` and
  `usecase` become `use-case` (the use case identifier, may be empty) and `implementation`
  (the existing file with source `code`, the name with source `functionality`).
- The map section `## Usecases` becomes `## Use cases`, with the columns
  `Use case | Scenarios | Implementation | What it answers`; Inbound and Outbound list
  `Use cases`.
- The rules table reads `# | Rule | Specified as`; the refusal table reads
  `... | Specified as | Use cases | ...`.
- The blockquotes and the `What it answers` source line speak of the use case, not the
  scenario.
- A validator fixture proves an artifact written with the former vocabulary is refused.

The plugin was written for one C# hexagonal codebase, and its format, templates, validator and
agents assumed it. It now describes any existing system, from one of two sources declared by a
new optional frontmatter key, `source`, equal variants of the same work:

- **`source: code`**: existing code in any language. The implementation is the path of the
  existing file implementing the use case (`.cs`, `.ts`, `.py`, `.java`, `.go`, `.kt`...), never
  a file to create. The validator checks only that it is a file path with an extension.
- **`source: functionality`**: a functionality observed or described, with no code to read: a
  product studied from the outside, a user interface, network traffic, a specification,
  documentation. The implementation is a plain name, unique in the set (case-insensitive); a value
  holding `/` or ending on a file extension is refused. `What it does` opens on
  `> Source: the functionality. Observed, not interpreted.`, and the detail and refusal
  blockquotes have their own exact text. Anchors read `— observed YYYY-MM-DD`, tested may be
  `0`, and refusals record `—` for an exception or a code the functionality does not show.

Also:

- **One template set per source**: `map`, `detail-entry` and `refusals` each come as
  `<artifact>.code.template.md` and `<artifact>.functionality.template.md`, with neutral
  placeholders. The former `<artifact>.template.md` files are gone.
- The tested counter rests on the scenario identifier carried by test names or identifiers of
  whatever framework the repository uses; the .NET `DisplayName` was one example.
- The `cartographer` and `scout` agents assume no language and no folder layout. The scout
  accepts an observed coordinate and returns the observed evidence as well as code.
- The validator checks that every file of a set declares the map's source.
- Validator fixtures and a unittest runner under `tests/cartography/`.

Major: the template paths under `${CLAUDE_PLUGIN_ROOT}` moved, the plugin changes nature, from
mapping one kind of codebase to reverse engineering any system, and the vocabulary of the
format changes. An artifact set written with format 1.x is refused by the validator until its
keys, its map section and its columns are renamed; its content stays valid.

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
