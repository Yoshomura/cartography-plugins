# commit-message

The shape of a commit message, and the check that refuses any other shape before `git commit`.
The `committer` agent runs on it; a direct invocation of the skill follows the same steps.

`SKILL.md` is the procedure: scope from the branch, type from its prefix, gitmoji from the
type, details from the staged diff. This file is for a human: what the skill owns, how it uses
it, and how to check a message by hand.

## What it owns

```
scripts/check_message.py     exit 1 on any deviation from the shape, naming each one
```

## The shape

```
<type>(<scope>): <gitmoji> <short description>

+ <detail>
+ <detail>

Co-authored-by: Claude <claude@anthropic.com>
```

The blank line after the subject is not decoration: git reads everything before the first
blank line as the subject, and without it the whole body lands in `git log --oneline`. The
attribution is the last line, exactly. The description is 50 characters at most, imperative,
lowercase, no trailing period.

## How the skill uses it

1. Writes the message to a file, never inline: a shell mangles the gitmoji and the backticks,
   and an inline message cannot be checked.
2. Runs `check_message.py` on that file. Red: fix the message and check again. Nothing is
   committed on a red result, whatever wrote the message.
3. Runs `git commit -F` on the checked file.

The check is what makes the shape hold regardless of the model doing the writing. It was added
after messages had slipped out of shape in practice: a long subject with the details swallowed
into it, then details without their `+` and blank lines between them. Both fail the check now,
each with the line named.

## Running it by hand

```
python "${CLAUDE_PLUGIN_ROOT}/skills/commit-message/scripts/check_message.py" <message file>
git log -1 --format=%B > /tmp/m.txt && python "${CLAUDE_PLUGIN_ROOT}/skills/commit-message/scripts/check_message.py" /tmp/m.txt
```

The second form checks the last commit's message. Standard library only.

## What it never does

Stage, push, or rewrite history: that is the `committer` agent's contract, and the skill only
shapes the message. Judge the content: a message that states a purpose the diff does not
support passes the check and is still wrong; the intent comes from the caller.
