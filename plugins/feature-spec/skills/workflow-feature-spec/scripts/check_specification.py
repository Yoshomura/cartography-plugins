"""Check the shape of a functional specification organized by feature and use case.

    python check_specification.py <feature folder or specification folder>

A feature folder holds its feature file, named after the folder, and one file per use case. A
specification folder holds feature folders: each one is checked. Exit code 0 when every file
passes, 1 otherwise.

Checks the form, never the content: identifiers and their numbering, sections and their order,
the use cases listed by the feature, and every scenario's sentence and Given / When / Then.
Standard library only.
"""

import io
import os
import re
import sys

IDENTIFIER = r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*"
FEATURE_ID = re.compile(r"^- \*\*Feature ID\*\*: `(" + IDENTIFIER + r")`$", re.M)
USE_CASE_ID = re.compile(r"^- \*\*Use case ID\*\*: `(" + IDENTIFIER + r")`$", re.M)
STATUS = re.compile(r"^- \*\*Status\*\*: (\S+)", re.M)
TABLE_LINK = re.compile(r"^\| `(" + IDENTIFIER + r")` \| \[[^\]]+\]\(([^)#]+\.md)\)", re.M)
SENTENCE_MAX = 120

FEATURE_SECTIONS = ["Goal", "Invariants", "Use cases"]
USE_CASE_SECTIONS = ["Goal", "Business rules", "Scenarios"]
GHERKIN_KEYWORDS = ("Given", "When", "Then", "And", "But")


class Report(object):
    def __init__(self):
        self.errors = []

    def error(self, path, message):
        self.errors.append((path, message))


def read(path):
    return io.open(path, encoding="utf-8").read()


def sections(text):
    return re.findall(r"^## (.+)$", text, flags=re.M)


def section_body(text, name):
    match = re.search(r"^## " + re.escape(name) + r"$", text, flags=re.M)
    if not match:
        return ""
    rest = text[match.end():]
    following = re.search(r"^## ", rest, flags=re.M)
    return rest[: following.start()] if following else rest


def check_order(text, expected, path, report):
    found = [s for s in sections(text) if s in expected]
    if found != expected:
        report.error(path, "sections %s must appear in that order, found %s" % (expected, found))


def check_numbering(headings, prefix, path, report):
    """Headings `### <prefix>-<n>` are numbered 1, 2, 3... with no gap."""
    numbers = []
    for heading in headings:
        match = re.match(re.escape(prefix) + r"-(\d+)\b", heading)
        if not match:
            report.error(path, "the heading %r does not start with %s-<n>" % (heading, prefix))
            continue
        numbers.append(int(match.group(1)))
    if numbers != list(range(1, len(numbers) + 1)):
        report.error(path, "%s identifiers are numbered %s, expected 1 to %d with no gap" % (prefix, numbers, len(numbers)))


def check_status(text, path, report):
    match = STATUS.search(text)
    if match and match.group(1) not in ("draft", "ready"):
        report.error(path, "the status must be draft or ready, found %r" % match.group(1))


def check_scenario(block, heading, path, report):
    lines = [line.rstrip() for line in block.split("\n")]
    content = [line for line in lines if line.strip()]
    if not content or content[0].startswith("```"):
        report.error(path, "%s has no sentence before its Given / When / Then" % heading)
        return
    sentence = content[0]
    if len(sentence) > SENTENCE_MAX:
        report.error(path, "%s: the sentence is %d characters, %d at most" % (heading, len(sentence), SENTENCE_MAX))
    if content[1:2] and not content[1].startswith("```"):
        report.error(path, "%s: the sentence must be one paragraph, followed by its gherkin block" % heading)
    try:
        start = content.index("```gherkin")
        end = content.index("```", start + 1)
    except ValueError:
        report.error(path, "%s has no closed ```gherkin block" % heading)
        return
    steps = content[start + 1:end]
    keywords = [step.split(" ", 1)[0] for step in steps]
    for step, keyword in zip(steps, keywords):
        if keyword not in GHERKIN_KEYWORDS or len(step.split(" ", 1)) < 2:
            report.error(path, "%s: the step %r does not start with Given, When, Then, And or But" % (heading, step))
    main = [k for k in keywords if k in ("Given", "When", "Then")]
    if main != ["Given", "When", "Then"]:
        report.error(path, "%s: the gherkin block needs one Given, one When and one Then, in that order, found %s" % (heading, main))


def check_use_case(path, feature_id, report, seen):
    text = read(path)
    match = USE_CASE_ID.search(text)
    if not match:
        report.error(path, "no '- **Use case ID**: `<ID>`' line")
        return None
    use_case_id = match.group(1)
    if not use_case_id.startswith(feature_id + "-"):
        report.error(path, "the use case ID %s does not start with the feature ID %s-" % (use_case_id, feature_id))
    check_status(text, path, report)
    check_order(text, USE_CASE_SECTIONS, path, report)

    rules = re.findall(r"^### (.+)$", section_body(text, "Business rules"), flags=re.M)
    check_numbering(rules, use_case_id + "-BUSINESS-RULE", path, report)
    if re.search(r"\b" + re.escape(use_case_id) + r"-RULE-\d", text):
        report.error(path, "write BUSINESS-RULE, never RULE alone: a rule is also an instruction file of a harness")

    body = section_body(text, "Scenarios")
    parts = re.split(r"^### (.+)$", body, flags=re.M)
    headings = parts[1::2]
    if not headings:
        report.error(path, "the use case has no scenario")
    check_numbering(headings, use_case_id + "-SCENARIO", path, report)
    for heading, block in zip(headings, parts[2::2]):
        if not re.match(re.escape(use_case_id) + r"-SCENARIO-\d+: \S", heading):
            report.error(path, "the heading %r must read <ID>-SCENARIO-<n>: <short title>" % heading)
        check_scenario(block, heading.split(":", 1)[0], path, report)

    for identifier in [use_case_id] + [h.split(":", 1)[0].split(" ", 1)[0] for h in rules + headings]:
        if identifier in seen:
            report.error(path, "the identifier %s is used twice, also in %s" % (identifier, seen[identifier]))
        seen[identifier] = path
    return use_case_id


def check_feature(folder, report):
    name = os.path.basename(os.path.normpath(folder))
    feature_path = os.path.join(folder, name + ".md")
    if not os.path.isfile(feature_path):
        report.error(folder, "no feature file %s.md named after its folder" % name)
        return
    text = read(feature_path)
    match = FEATURE_ID.search(text)
    if not match:
        report.error(feature_path, "no '- **Feature ID**: `<ID>`' line")
        return
    feature_id = match.group(1)
    check_status(text, feature_path, report)
    check_order(text, FEATURE_SECTIONS, feature_path, report)
    invariants = re.findall(r"^### (.+)$", section_body(text, "Invariants"), flags=re.M)
    check_numbering(invariants, feature_id + "-INVARIANT", feature_path, report)

    listed = {}
    for identifier, target in TABLE_LINK.findall(section_body(text, "Use cases")):
        listed[target] = identifier
    seen = {feature_id: feature_path}
    for invariant in invariants:
        seen[invariant.split(" ", 1)[0]] = feature_path

    files = sorted(n for n in os.listdir(folder) if n.endswith(".md") and n != name + ".md")
    for file_name in files:
        path = os.path.join(folder, file_name)
        use_case_id = check_use_case(path, feature_id, report, seen)
        if file_name not in listed:
            report.error(feature_path, "the use case file %s is not listed in the Use cases table" % file_name)
        elif use_case_id and listed[file_name] != use_case_id:
            report.error(feature_path, "the table lists %s as %s, the file says %s" % (file_name, listed[file_name], use_case_id))
    for target in sorted(set(listed) - set(files)):
        report.error(feature_path, "the Use cases table links to %s, which does not exist" % target)


def main(argv):
    if len(argv) != 2 or not os.path.isdir(argv[1]):
        print("usage: python check_specification.py <feature folder or specification folder>")
        return 2
    root = argv[1]
    name = os.path.basename(os.path.normpath(root))
    if os.path.isfile(os.path.join(root, name + ".md")):
        folders = [root]
    else:
        folders = sorted(os.path.join(root, n) for n in os.listdir(root) if os.path.isdir(os.path.join(root, n)))
    report = Report()
    for folder in folders:
        check_feature(folder, report)
    for path, message in report.errors:
        print("ERROR %s: %s" % (path, message))
    print("\nspecification check - %d feature(s), %d error(s)" % (len(folders), len(report.errors)))
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
