---
name: commit-message
description: Generate a Conventional Commits + Gitmoji commit message from the current git branch name and staged changes, and create the git commit. Use for EVERY commit created in this repository, whatever triggers it - the user asking for a commit or a commit message, and just as much any workflow-driven commit Claude makes on its own (delivering a feature after a green gate, session workflow step 5, archiving a spec, a docs or chore commit). Never run a raw `git commit` without going through this skill.
allowed-tools:
  - Bash(git branch --show-current)
  - Bash(git diff --cached *)
  - Bash(git status *)
  - Bash(git log *)
  - Bash(git commit *)
---

# Conventional Commit + Gitmoji generator

Produce a commit message that follows Conventional Commits with a Gitmoji prefix on the subject line. The message is derived from the current branch name and the staged diff.

## Who the caller is

Everywhere below, **the caller** is whoever this skill's context belongs to, and the word
`user` in these rules means that caller. It is a human when the skill is loaded in a session
someone is typing into. It is the **calling agent** when the skill is preloaded in a subagent
such as `committer`, and then "ask the user" means report back and stop, not prompt a person.

The skill itself asks nothing and decides nothing: it is text in someone else's context.

## Where the intent comes from

A staged diff shows **what** changed. It does not show **why**, and the why is what a commit
message is for: a decision taken, a constraint discovered, a document read. None of it appears
in the diff.

The caller supplies that intent in its request. Build the body from it and use the diff to
make it accurate and specific.

**When no intent is supplied**, write from the staged diff alone and say so when returning. Do
not invent a reason. A message stating a purpose the diff does not support is worse than a
plain description of the change: it reads as knowledge and it is a guess.

This skill has two modes:

- **Draft mode**: return only the commit message.
- **Commit mode**: create the message and run `git commit` with the generated message. Enter this mode when the user explicitly asks to commit, or when the session permission mode is auto (bypass permissions) — in that case commit directly without asking for confirmation.

## Steps

1. **Get the current branch name** with `git branch --show-current`.

2. **Extract the scope** from the branch name:
   - If the branch contains a ticket pattern such as `XXXX-1234`, use the ticket id as the scope.
   - Otherwise use the last segment of the branch after the last `/`.
   - **If the branch holds no `/`**, such as `master` or `main`, omit the scope entirely and
     write `<type>: <gitmoji> <short description>`. The branch name of a trunk says nothing
     about what the commit touches, and a scope that names it is noise.

   Examples:
   - `feature/XXXX-1254` → `XXXX-1254`
   - `fix/XXXX-1254` → `XXXX-1254`
   - `feature/nikko/toto/sample-doc-v-2` → `sample-doc-v-2`
   - `bugfix/user-authentication` → `user-authentication`

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

5. **Analyse the staged changes** with `git diff --cached` and write a meaningful short description and body details.

## Commit rules

- Commit when the user explicitly asks to commit, or without asking when the session permission mode is auto (bypass permissions).
- Outside auto mode, never commit without an explicit ask: return the draft only.
- Commit only the staged changes.
- If nothing is staged, do not invent a commit; ask the user to stage files first.
- Use the generated subject and body as the commit message. Git **trailers** may follow the
  body, after a blank line: `Co-Authored-By`, `Signed-off-by`, `Refs`. They are a git
  convention, not part of the message, and they never replace a detail line.
- **A `Co-Authored-By` trailer names the model that actually wrote the message**, in the form
  `Co-Authored-By: Claude <Model> <noreply@anthropic.com>`. Write the model you are running
  on, not the one of whoever called you: a subagent on Haiku writes `Claude Haiku`, a session
  on Opus writes `Claude Opus`. Naming a model that did not do the work is a false attribution,
  and GitHub records it as a co-author on the commit.
- Keep the short description under 50 characters.
- Use the imperative mood (`add` not `added`).
- Do not end the subject line with a period.

## Output format

### Draft mode

```
<type>(<scope>): <gitmoji> <short description>

+ <detail 1>
+ <detail 2>
+ <detail N>
```

⚠️ **The blank line after the subject is mandatory.** Git reads everything up to the first
blank line as the subject. Without it the whole block becomes one subject of several hundred
characters, which breaks `git log --oneline`, the commit list on the forge, and the
under-50-characters rule above.

### Commit mode

Run `git commit` with the generated message, then return a concise confirmation containing the commit hash and the final subject line.

## Examples

Branch `feature/XXXX-1254`, new feature:

```
feat(XXXX-1254): ✨ add user authentication endpoint

+ add login and logout endpoints
+ implement JWT token generation
+ add password validation
```

Branch `feature/nikko/toto/sample-doc-v-2`, documentation:

```
docs(sample-doc-v-2): 📝 update sample documentation

+ add new examples
+ improve code snippets
```

Branch `fix/XXXX-789`, bug fix:

```
fix(XXXX-789): 🐛 resolve null reference in user service

+ add null check before accessing user properties
+ add unit test for edge case
```

## Rules

- Return only the commit message in draft mode, with no surrounding explanation.
- Do not hardcode any project prefix such as SQRA; use the branch ticket id or a generic scope derived from the branch.
- Keep detail lines concise and specific.
- Prefer the staged diff over the working tree when describing the change.
