"""Validate the shape of the cartography artifacts. Format version 1.0.0.

Checks form, never content. That a file has valid frontmatter, its sections in order and no
banned word says nothing about whether the map is right: what it says is inferred and stays
outside any gate. The shape is not inferred, so a failing shape can block.

    python .claude/skills/cartography/scripts/validate.py docs

Exit code 0 when every file passes, 1 otherwise. Warnings never fail the run.
"""

import io
import os
import re
import sys

FORMAT_VERSION = "1.0.0"

# Blockquotes are copied character for character from the templates. Comparing them exactly
# is what stops the boilerplate from drifting, and it is why the banned-vocabulary check can
# skip them: the canonical text itself contains "should".
BLOCKQUOTE = {
    "map": (
        "> **Not normative, and inferred.** Where things are, never what they should be. `?` marks an\n"
        "> uncertain link, and nothing here is ever a blocking CI gate."
    ),
    "detail-entry": (
        "> **Observation, not specification.** The scenario says what should happen; this file says\n"
        "> what the code does. Divergences are listed at the end, and settled in the specification,\n"
        "> not here."
    ),
    "refusal-surface": (
        "> **Observation, not specification.** The refusal is specified in the scenario; its mechanism\n"
        "> is decided in the code and only observed here. Divergences are listed at the end."
    ),
}

SOURCE_LINES = [
    "> Source: the scenario. Compressed, not inferred.",
    "> Source: the code. Observed, not interpreted.",
]

REQUIRED_KEYS = {
    "map": ["kind", "normative", "generator", "repository", "base"],
    "detail-entry": ["kind", "normative", "generator", "scenario", "usecase", "base"],
    "refusal-surface": ["kind", "normative", "generator", "repository", "base"],
}

SECTIONS = {
    "map": ["Usecases", "Inbound", "Outbound", "Anchors", "Unattached"],
    "detail-entry": [
        "What it answers",
        "What it does",
        "The rules it applies",
        "What it needs",
        "What it produces",
        "Observed divergences",
    ],
    "refusal-surface": [
        "Mechanisms",
        "Business refusals",
        "Adapter refusals",
        "Translation",
        "Divergences",
    ],
}

MECHANISMS = {"Business exception", "Returned outcome", "Silent no-op", "Adapter"}
EM_DASH = "—"

BANNED = [
    ("in order to", "purpose"),
    ("so that", "purpose"),
    ("because", "cause"),
    ("to prevent", "purpose"),
    ("correctly", "judgment"),
    ("properly", "judgment"),
    ("should", "judgment"),
    ("redundant", "judgment"),
    ("unnecessary", "judgment"),
    ("presumably", "completion"),
    ("seems intended", "completion"),
    ("likely", "completion"),
    ("probably", "completion"),
]

FRONTMATTER_LINE = re.compile(r"^[a-z][a-z-]*:( .+)?$")
COUNTER = re.compile(r"^\d+/\d+/\d+$")
SHA = re.compile(r"\b[0-9a-f]{7,40}\b")
FOREIGN_SCENARIO_PATH = re.compile(r"docs/[a-z0-9-]+/scenarios/")


class Report(object):
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, path, message):
        self.errors.append((path, message))

    def warn(self, path, message):
        self.warnings.append((path, message))


def split_frontmatter(text, path, report):
    if not text.startswith("---\n"):
        report.error(path, "no YAML frontmatter: the file must open on a --- line")
        return None, text
    end = text.find("\n---\n", 3)
    if end == -1:
        report.error(path, "frontmatter is never closed by a --- line")
        return None, text
    block = text[4:end]
    body = text[end + 5 :]

    keys = {}
    for line in block.split("\n"):
        if not FRONTMATTER_LINE.match(line):
            report.error(path, "frontmatter line is not a plain 'key: value': %r" % line)
            continue
        key, _, value = line.partition(":")
        keys[key.strip()] = value.strip()
    return keys, body


def check_frontmatter(keys, path, report):
    kind = keys.get("kind")
    if kind not in REQUIRED_KEYS:
        report.error(path, "unknown kind %r, expected one of %s" % (kind, sorted(REQUIRED_KEYS)))
        return None

    for key in REQUIRED_KEYS[kind]:
        if key not in keys:
            report.error(path, "frontmatter is missing the key %r" % key)

    for key in keys:
        if key not in REQUIRED_KEYS[kind]:
            report.error(path, "frontmatter carries the unexpected key %r" % key)

    if keys.get("normative") != "false":
        report.error(path, "normative must be exactly 'false', found %r" % keys.get("normative"))
    if keys.get("generator") != "cartographer":
        report.error(path, "generator must be 'cartographer', found %r" % keys.get("generator"))

    if kind == "detail-entry":
        usecase = keys.get("usecase", "")
        if usecase and not usecase.endswith(".cs"):
            report.error(path, "usecase must be a file path, found %r" % usecase)
        if not keys.get("scenario"):
            report.warn(path, "scenario is empty: this usecase answers none, expected in the map too")

    # Nothing locating another repository belongs in the frontmatter.
    for key, value in keys.items():
        if key == "base":
            continue
        if FOREIGN_SCENARIO_PATH.search(value):
            report.error(path, "key %r carries a path into the documentation repository" % key)
        if key != "usecase" and SHA.fullmatch(value or ""):
            report.error(path, "key %r carries a bare commit SHA of a foreign repository" % key)

    return kind


def check_blockquote(body, kind, path, report):
    expected = BLOCKQUOTE[kind]
    if expected not in body:
        report.error(path, "the header blockquote does not match the template character for character")
        return body
    return body.replace(expected, "")


def check_sections(body, kind, path, report):
    found = re.findall(r"^## (.+)$", body, flags=re.MULTILINE)
    expected = SECTIONS[kind]
    if found != expected:
        report.error(path, "sections are %s, expected exactly %s in that order" % (found, expected))


def check_banned(body, path, report):
    for line_number, line in enumerate(body.split("\n"), 1):
        lowered = line.lower()
        for word, family in BANNED:
            if word in lowered:
                report.error(path, "line %d: banned %s vocabulary %r" % (line_number, family, word))


def table_rows(body, heading):
    match = re.search(r"^## " + re.escape(heading) + r"$", body, flags=re.MULTILINE)
    if not match:
        return []
    rest = body[match.end() :]
    nxt = re.search(r"^## ", rest, flags=re.MULTILINE)
    if nxt:
        rest = rest[: nxt.start()]
    rows = []
    for line in rest.split("\n"):
        line = line.strip()
        if not line.startswith("|") or set(line) <= set("|- "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows[1:] if rows else []


def check_map(body, path, report, linked):
    rows = table_rows(body, "Usecases")
    if not rows:
        report.warn(path, "the Usecases table holds no row")
    for cells in rows:
        if len(cells) != 4:
            report.error(path, "a Usecases row has %d columns, expected 4" % len(cells))
            continue
        scenario, counter, usecase, summary = cells
        if not COUNTER.match(counter):
            report.error(path, "Cases must read declared/covered/tested, found %r" % counter)
        if not usecase.strip("`").endswith(".cs"):
            report.error(path, "the Usecase column must be a file path, found %r" % usecase)
        if len(summary) > 120:
            report.error(path, "the summary is %d characters, 120 at most: %r" % (len(summary), summary[:60]))
        link = re.search(r"\]\((details/[^)]+\.md)\)", scenario)
        if link:
            linked.add(link.group(1))
        else:
            report.error(path, "the Scenario column must link to its detail entry, found %r" % scenario)


def check_refusals(body, path, report):
    for cells in table_rows(body, "Business refusals"):
        if len(cells) != 8:
            report.error(path, "a Business refusals row has %d columns, expected 8" % len(cells))
            continue
        mechanism, exception = cells[1], cells[2]
        if mechanism.strip("`") not in MECHANISMS:
            report.error(path, "unknown mechanism %r, expected one of %s" % (mechanism, sorted(MECHANISMS)))
        elif mechanism.strip("`") != "Business exception" and exception != EM_DASH:
            # Only the exception is tied to the mechanism. A code is what leaves the
            # deployable on the wire, and a returned outcome can carry one.
            report.error(path, "mechanism %r carries an exception %r" % (mechanism, exception))


def check_detail(body, path, report):
    for line in SOURCE_LINES:
        if line not in body:
            report.error(path, "missing the source line %r" % line)
    for cells in table_rows(body, "The rules it applies"):
        if len(cells) != 3:
            report.error(path, "a rules row has %d columns, expected 3" % len(cells))


def validate_file(path, report, linked):
    text = io.open(path, encoding="utf-8").read()
    keys, body = split_frontmatter(text, path, report)
    if keys is None:
        return None
    kind = check_frontmatter(keys, path, report)
    if kind is None:
        return None
    if not keys.get("base"):
        if "`base` is empty" not in body:
            report.warn(path, "base is empty and the body does not say why")
    body = check_blockquote(body, kind, path, report)
    check_sections(body, kind, path, report)
    check_banned(body, path, report)
    if kind == "map":
        check_map(body, path, report, linked)
    elif kind == "refusal-surface":
        check_refusals(body, path, report)
    else:
        check_detail(body, path, report)
    return kind


def main(argv):
    root = argv[1] if len(argv) > 1 else "docs"
    report = Report()
    linked = set()

    targets = []
    for name in ("map.md", "refusals.md"):
        candidate = os.path.join(root, name)
        if os.path.exists(candidate):
            targets.append(candidate)
        else:
            report.error(root, "%s is absent" % name)

    details_dir = os.path.join(root, "details")
    details = []
    if os.path.isdir(details_dir):
        details = sorted(
            os.path.join(details_dir, n) for n in os.listdir(details_dir) if n.endswith(".md")
        )
        targets.extend(details)
    else:
        report.error(root, "the details/ directory is absent")

    for path in targets:
        validate_file(path, report, linked)

    # Every detail entry is reachable from the map, and every link resolves.
    on_disk = set(os.path.relpath(p, root).replace(os.sep, "/") for p in details)
    for target in sorted(linked - on_disk):
        report.error(os.path.join(root, "map.md"), "links to %s, which does not exist" % target)
    for orphan in sorted(on_disk - linked):
        report.error(os.path.join(root, orphan), "is linked from no row of the map")

    for path, message in report.warnings:
        print("warn  %s: %s" % (path, message))
    for path, message in report.errors:
        print("ERROR %s: %s" % (path, message))

    print(
        "\ncartography format %s - %d file(s), %d error(s), %d warning(s)"
        % (FORMAT_VERSION, len(targets), len(report.errors), len(report.warnings))
    )
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
