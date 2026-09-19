"""Check a commit message file against the commit-message skill's format. Exit 1 on any deviation.

    python "${CLAUDE_PLUGIN_ROOT}/skills/commit-message/scripts/check_message.py" <message file>

The format is a shape, and a shape can be checked, whatever wrote it:

    <type>(<scope>): <gitmoji> <short description>
    <blank line>
    + <detail>
    + <detail>
    <blank line>
    Co-authored-by: Claude <claude@anthropic.com>

The blank line after the subject is what keeps git from swallowing the details into the
subject. The attribution is the last line, exactly. Nothing else is allowed anywhere.
"""

import io
import re
import sys

TYPES = ("feat", "fix", "docs", "refactor", "test", "chore", "perf", "style", "build", "ci", "revert")
GITMOJI = {"✨", "🐛", "📝", "♻️", "♻", "✅", "🔧", "⚡", "⚡️", "💄", "📦", "👷", "⏪"}
ATTRIBUTION = "Co-authored-by: Claude <claude@anthropic.com>"
MAX_DESCRIPTION = 50
SUBJECT = re.compile(r"^(?P<type>[a-z]+)\((?P<scope>[^()\s]+)\): (?P<emoji>\S+) (?P<description>.+)$")


def check(text):
    problems = []
    lines = text.rstrip("\n").split("\n")
    if len(lines) < 5:
        return ["the message needs a subject, a blank line, at least one '+ ' detail, a blank line and the attribution"]

    subject, blank, *rest = lines
    match = SUBJECT.match(subject)
    if not match:
        problems.append("subject must read '<type>(<scope>): <gitmoji> <description>', found %r" % subject)
    else:
        if match.group("type") not in TYPES:
            problems.append("unknown type %r, expected one of %s" % (match.group("type"), ", ".join(TYPES)))
        if match.group("emoji") not in GITMOJI:
            problems.append("unknown gitmoji %r" % match.group("emoji"))
        description = match.group("description")
        if len(description) > MAX_DESCRIPTION:
            problems.append("description is %d characters, %d at most: %r" % (len(description), MAX_DESCRIPTION, description))
        if description.endswith("."):
            problems.append("the subject must not end with a period")
        if description[0].isupper():
            problems.append("the description starts lowercase, found %r" % description)
    if blank != "":
        problems.append("line 2 must be blank: git reads everything before the first blank line as the subject")

    if rest[-1] != ATTRIBUTION:
        problems.append("the last line must be exactly %r, found %r" % (ATTRIBUTION, rest[-1]))
    if len(rest) < 2 or rest[-2] != "":
        problems.append("a blank line must separate the details from the attribution")
    details = rest[:-2] if len(rest) >= 2 else []
    if not details:
        problems.append("at least one '+ ' detail line is required")
    for number, line in enumerate(details, 3):
        if line == "":
            problems.append("line %d: blank line inside the details; details are consecutive" % number)
        elif not line.startswith("+ "):
            problems.append("line %d: a detail starts with '+ ', found %r" % (number, line))
        elif len(line) < 4:
            problems.append("line %d: empty detail" % number)
    return problems


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    text = io.open(argv[1], encoding="utf-8").read()
    problems = check(text)
    for problem in problems:
        print("ERROR: %s" % problem)
    print("commit message: %s" % ("conforms" if not problems else "%d problem(s)" % len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
