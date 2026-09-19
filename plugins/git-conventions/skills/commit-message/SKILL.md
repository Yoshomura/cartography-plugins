---
name: commit-message
description: Generate a Conventional Commits + Gitmoji commit message from the current git branch name and staged changes, and create the git commit. Use for EVERY commit created in a repository where this plugin is enabled, whatever triggers it - the user asking for a commit or a commit message, and just as much any workflow-driven commit Claude makes on its own. Never run a raw `git commit` without going through this skill.
license: MIT
allowed-tools:
  - Bash(git branch --show-current)
  - Bash(git diff --cached *)
  - Bash(git status *)
  - Bash(git log *)
  - Bash(git commit *)
  - Bash(python *check_message.py *)
---

# Conventional Commit + Gitmoji generator

Produce a commit message that follows Conventional Commits with a Gitmoji prefix on the subject
line. The message is derived from the current branch name and the staged diff.

This skill has two modes:

- **Commit mode (default)**: create the message and run `git commit` with the generated
  message, without asking for confirmation.
- **Draft mode**: return only the commit message, without committing. Enter this mode ONLY when
  the user explicitly asks for a draft, a silent run, or "just the message".

## Who the caller is

Everywhere below, **the caller** is whoever this skill's context belongs to. It is a human when
the skill is loaded in a session someone is typing into. It is the **calling agent** when the
skill is preloaded in a subagent such as `committer`, and then "ask the user" means report back
and stop, not prompt a person.

## Steps

1. **Get the current branch name** with `git branch --show-current`.

2. **Extract the scope** from the branch name:
   - If the branch contains a ticket pattern (uppercase key, dash, digits, such as `ABC-1234`
     or `XY-3`), use the ticket id as the scope.
   - Otherwise use the last segment of the branch after the last `/`.
   - **If the branch holds no `/`**, such as `master` or `main`, omit the scope entirely and
     write `<type>: <gitmoji> <short description>`. The branch name of a trunk says nothing
     about what the commit touches, and a scope that names it is noise.

   Examples:
   - `feat/ABC-1254` → `ABC-1254`
   - `fix/XY-3` → `XY-3`
   - `feat/user-export` → `user-export`
   - `docs/onboarding-guide` → `onboarding-guide`

3. **Determine the commit type** from the branch prefix:
   - `feat/` or `feature/` → `feat`
   - `fix/` or `bugfix/` → `fix`
   - `hotfix/` → `fix`
   - `docs/` → `docs`
   - `refactor/` → `refactor`
   - `test/` → `test`
   - `chore/` → `chore`
   - `perf/` → `perf`
   - `ci/` → `ci`
   - `style/` → `style`
   - `build/` → `build`
   - Any other prefix, or no prefix → infer from the staged changes content.

4. **Pick the Gitmoji** matching the type:
   - `feat` → ✨
   - `fix` → 🐛
   - `docs` → 📝
   - `refactor` → ♻️
   - `test` → ✅
   - `chore` → 🔧
   - `perf` → ⚡
   - `style` → 💄
   - `build` → 📦
   - `ci` → 👷
   - `revert` → ⏪

5. **Analyse the staged changes** with `git diff --cached` and write a meaningful short
   description and body details. Name what the change does for the project, not the files it
   touches. If the project's own instructions (its `CLAUDE.md`) state how changes are named or
   which type applies to which kind of change, those instructions win over the generic mapping
   above.

6. **Write the message to a file, check it, then commit with `-F`.** Never build the message
   inline: a shell mangles the gitmoji and the backticks, and an inline message cannot be
   checked.

   ```
   python "${CLAUDE_PLUGIN_ROOT}/skills/commit-message/scripts/check_message.py" <message file>
   git commit -F <message file>
   ```

   The check exits 1 on any deviation from the format below and names it. A message that fails
   the check is fixed and checked again; it is never committed, whatever wrote it. The format is
   a shape, and the script is what makes the shape hold regardless of the model running this.

## Where the intent comes from

A staged diff shows **what** changed. It does not show **why**, and the why is what a commit
message is for: a decision taken, a constraint discovered, a document read. None of it appears
in the diff.

The caller supplies that intent in its request. Build the body from it and use the diff to make
it accurate and specific.

**When no intent is supplied**, write from the staged diff alone and say so when returning. Do
not invent a reason. A message stating a purpose the diff does not support is worse than a plain
description of the change: it reads as knowledge and it is a guess.

## Commit rules

- Commit by default: invoking this skill means "make the message AND commit", no confirmation
  needed.
- Skip the commit and return the draft only when the user explicitly asked for a draft or a
  message-only run.
- Commit only the staged changes.
- If nothing is staged, do not invent a commit; ask the caller to stage files first.
- Never commit on the repository's default branch (`master` or `main`): say so and stop.
- Use the generated subject and body as the exact commit message.
- Keep the short description under 50 characters.
- Use the imperative mood (`add` not `added`).
- Do not end the subject line with a period.
- One blank line after the subject, always: git reads everything before the first blank line as
  the subject, and without it the whole body lands in `git log --oneline`.
- The last line is the attribution, exactly `Co-authored-by: Claude <claude@anthropic.com>`,
  separated from the details by one blank line. Never the `Generated with Claude Code` footer.

## Output format

The complete shape, the only one the check accepts:

```
<type>(<scope>): <gitmoji> <short description>

+ <detail 1>
+ <detail 2>
+ <detail N>

Co-authored-by: Claude <claude@anthropic.com>
```

### Commit mode (default)

Write that message to a file, run the check, run `git commit -F` on it, then return a concise
confirmation containing the commit hash and the complete message.

### Draft mode (on explicit request only)

Return the message in that exact shape, and nothing else.

## Examples

Branch `feat/ABC-1254`, new feature:

```
feat(ABC-1254): ✨ add user export endpoint

+ add the export endpoint returning the user's data as CSV
+ enforce the per-day export quota
+ cover the quota rule with unit tests

Co-authored-by: Claude <claude@anthropic.com>
```

Branch `docs/onboarding-guide`, documentation:

```
docs(onboarding-guide): 📝 describe the local setup

+ list the required tools and their versions
+ add the first-run checklist

Co-authored-by: Claude <claude@anthropic.com>
```

Branch `fix/XY-789`, bug fix:

```
fix(XY-789): 🐛 resolve null reference in user service

+ add a null check before accessing the profile
+ add a unit test for the missing-profile case

Co-authored-by: Claude <claude@anthropic.com>
```

## Rules

- Return only the commit message in draft mode, with no surrounding explanation.
- Do not assume a project prefix; use the branch ticket id whatever its key, or a generic scope
  derived from the branch.
- Product vocabulary stays in its own language: a domain term the project uses as an identifier
  is not prose to translate.
- Keep detail lines concise and specific.
- Prefer the staged diff over the working tree when describing the change.
