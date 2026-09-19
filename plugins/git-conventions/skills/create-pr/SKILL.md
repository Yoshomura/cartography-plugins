---
name: create-pr
description: Create or update a GitHub pull request with the mandatory conventions - the project's pull request label when it declares one, and a body ending on the Co-authored-by Claude signature (never the "Generated with Claude Code" footer). Use for EVERY PR created or edited via gh, whatever triggers it. The conventions are executed by the pr-opener agent; never run a raw `gh pr create`.
license: MIT
---

# Create Pull Request

The conventions every pull request follows. **The executor is the `pr-opener` agent**: it
runs the checks, writes the body and calls `gh`. This skill states the conventions the agent
applies and what the main session does before launching it.

## Mandatory rules

1. **Label**: when the project declares a pull request label (in its `CLAUDE.md`, or the
   caller names one in the agent's prompt), always pass it with `--label <label>` on
   `gh pr create` (or `gh pr edit <n> --add-label <label>` for an existing PR). If the label
   does not exist in the repository, report it and create the PR without it, never with
   another label in its place. When no label is declared anywhere, open the PR without one.
2. **Signature**: the PR body ends with exactly:

   ```
   Co-authored-by: Claude <claude@anthropic.com>
   ```

   NEVER use the footer `🤖 Generated with [Claude Code](https://claude.com/claude-code)` in a
   PR body.

## Sequence

1. **Main session**: the branch is committed (through the `committer` agent) and the user has
   explicitly confirmed the push. The main session pushes (`git push -u origin <branch>`);
   the agent never does.
2. **Main session** launches `pr-opener` with the intent of the branch (what it delivers and
   why), the checks that were run, and the label when the project declares one.
3. **`pr-opener`**: verifies `gh auth status`, that the branch is not the base, that local and
   remote heads match; determines the base from the repository's default branch; writes title
   and body; creates or updates the PR with `--body-file`.
4. Title: Conventional Commits style, English, imperative, no trailing period, scope from the
   branch ticket id or the last branch segment.
5. Body: `## Summary`, `## Why` (when an intent was supplied), `## Changes`, `## Verification`
   (when checks were supplied), then the signature line. Omit a section rather than filling
   it with a placeholder.

## Base branch

The repository's default branch, read from `gh repo view`. Another base only if the user says
so.
