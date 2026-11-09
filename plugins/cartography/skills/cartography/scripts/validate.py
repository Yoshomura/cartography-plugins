"""Validate the shape of the cartography artifacts. Format version 2.2.0.

Checks form, never content. That a file has valid frontmatter, its sections in order and no
banned word says nothing about whether the map is right: what it says is inferred and stays
outside any gate. The shape is not inferred, so a failing shape can block.

    python validate.py docs

Exit code 0 when every file passes, 1 otherwise. Warnings never fail the run.

Cartography is reverse engineering, whatever the technology, and it has two sources, declared
by the optional `source` frontmatter key (`code` when the key is absent):

- `code`: existing code, in any language. The implementation is a file path in that codebase.
- `functionality`: a functionality observed or described, with no code to read (a product
  studied from the outside, a user interface, a specification, documentation). The
  implementation is a plain name, unique in the set, never a path: a path to a file that does
  not exist would be an invention.

The specification the artifacts are compared with is organized by feature and use case: a
detail entry is named after a use case identifier, and its observed business rules point at the identifier of a
scenario, a business rule or an invariant of that specification.
"""

import io
import os
import re
import sys

FORMAT_VERSION = "2.2.0"

CODE = "code"
FUNCTIONALITY = "functionality"
SOURCES = (CODE, FUNCTIONALITY)

# Blockquotes are copied character for character from the templates. Comparing them exactly
# is what stops the boilerplate from drifting, and it is why the banned-vocabulary check can
# skip them: the canonical text itself contains "should". One exact set per source.
MAP_BLOCKQUOTE = (
    "> **Not normative, and inferred.** Where things are, never what they should be. `?` marks an\n"
    "> uncertain link, and nothing here is ever a blocking CI gate."
)
BLOCKQUOTE = {
    CODE: {
        "map": MAP_BLOCKQUOTE,
        "detail-entry": (
            "> **Observation, not specification.** The use case says what should happen; this file says\n"
            "> what the code does. Divergences are listed at the end, and settled in the specification,\n"
            "> not here."
        ),
        "refusal-surface": (
            "> **Observation, not specification.** The refusal is specified in the use case; its mechanism\n"
            "> is decided in the code and only observed here. Divergences are listed at the end."
        ),
    },
    FUNCTIONALITY: {
        "map": MAP_BLOCKQUOTE,
        "detail-entry": (
            "> **Observation, not specification.** The use case says what should happen; this file says\n"
            "> what the functionality does, as observed or described. Divergences are listed at the end,\n"
            "> and settled in the specification, not here."
        ),
        "refusal-surface": (
            "> **Observation, not specification.** The refusal is specified in the use case; what the\n"
            "> functionality shows when it refuses is only observed here. Divergences are listed at the end."
        ),
    },
}

SOURCE_LINES = {
    CODE: [
        "> Source: the use case. Compressed, not inferred.",
        "> Source: the code. Observed, not interpreted.",
    ],
    FUNCTIONALITY: [
        "> Source: the use case. Compressed, not inferred.",
        "> Source: the functionality. Observed, not interpreted.",
    ],
}

REQUIRED_KEYS = {
    "map": ["kind", "normative", "generator", "repository", "base"],
    "detail-entry": ["kind", "normative", "generator", "use-case", "implementation", "base"],
    "refusal-surface": ["kind", "normative", "generator", "repository", "base"],
}

# Allowed in every kind. An absent `source` reads `code`, so every artifact written before the
# key existed stays valid.
OPTIONAL_KEYS = ["source"]

SECTIONS = {
    "map": ["Use cases", "Inbound", "Outbound", "Anchors", "Unattached"],
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
FOREIGN_SPECIFICATION_PATH = re.compile(r"docs/specifications/")

# A file path in any language: a file name with an extension, optionally under folders. The
# language is not checked, and neither is the existence of the file.
FILE_PATH = re.compile(r"^(?:[^/\\]+[/\\])*[^/\\.][^/\\]*\.[A-Za-z0-9]+$")
FILE_EXTENSION = re.compile(r"\.[A-Za-z0-9]+$")
# An anchor with no tree to hash: the date the functionality was last observed.
OBSERVED_ANCHOR = re.compile(r"^" + EM_DASH + r" observed \d{4}-\d{2}-\d{2}$")


class Report(object):
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, path, message):
        self.errors.append((path, message))

    def warn(self, path, message):
        self.warnings.append((path, message))


def source_of(keys):
    return keys.get("source") or CODE


def implementation_key(value):
    """The identity of an implementation name: backticks and spaces trimmed, case ignored."""
    return value.strip().strip("`").strip().casefold()


def report_duplicates(names, path, where, report):
    """Report every implementation name met more than once. `names` is a list of raw values."""
    seen = {}
    for name in names:
        seen.setdefault(implementation_key(name), []).append(name.strip().strip("`").strip())
    for key in sorted(seen):
        if key and len(seen[key]) > 1:
            report.error(
                path,
                "the implementation name %r appears %d times %s: with source functionality an implementation name is unique"
                % (seen[key][0], len(seen[key]), where),
            )


def implementation_problem(value, source):
    """Return why an implementation value does not fit its source, or None when it fits.

    Code: a file path with an extension, any language. Functionality: a plain implementation name, and
    anything that looks like a path is refused, since there is no file for it to name.
    """
    value = value.strip().strip("`").strip()
    if source == FUNCTIONALITY:
        if not value:
            return "with source functionality the implementation is a name, and it is empty"
        if "/" in value or "\\" in value or FILE_EXTENSION.search(value):
            return "with source functionality the implementation is a plain name, never a file path"
        return None
    if "://" in value or not FILE_PATH.match(value):
        return "with source code the implementation must be a file path with an extension"
    return None


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
        if key not in REQUIRED_KEYS[kind] and key not in OPTIONAL_KEYS:
            report.error(path, "frontmatter carries the unexpected key %r" % key)

    if "source" in keys and keys["source"] not in SOURCES:
        report.error(path, "source must be one of %s, found %r" % (list(SOURCES), keys["source"]))
        return None
    source = source_of(keys)

    if keys.get("normative") != "false":
        report.error(path, "normative must be exactly 'false', found %r" % keys.get("normative"))
    if keys.get("generator") != "cartographer":
        report.error(path, "generator must be 'cartographer', found %r" % keys.get("generator"))

    if kind == "detail-entry":
        implementation = keys.get("implementation", "")
        # An empty implementation path stays tolerated with source code, as it always was. An
        # implementation name is always known with source functionality: it is part of the
        # specification.
        if implementation or source == FUNCTIONALITY:
            problem = implementation_problem(implementation, source)
            if problem:
                report.error(path, "%s, found %r" % (problem, implementation))
        if not keys.get("use-case"):
            report.warn(path, "use-case is empty: this implementation answers none, expected in the map too")

    # Nothing locating another repository belongs in the frontmatter.
    for key, value in keys.items():
        if key == "base":
            continue
        if FOREIGN_SPECIFICATION_PATH.search(value):
            report.error(path, "key %r carries a path into the documentation repository" % key)
        if key != "implementation" and SHA.fullmatch(value or ""):
            report.error(path, "key %r carries a bare commit SHA of a foreign repository" % key)

    return kind


def check_blockquote(body, kind, source, path, report):
    expected = BLOCKQUOTE[source][kind]
    if expected not in body:
        report.error(
            path,
            "the header blockquote does not match the source-%s template character for character" % source,
        )
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


def check_map(body, source, path, report, linked):
    rows = table_rows(body, "Use cases")
    if source == FUNCTIONALITY:
        report_duplicates([c[2] for c in rows if len(c) == 4], path, "in the Use cases table", report)
    if not rows:
        report.warn(path, "the Use cases table holds no row")
    for cells in rows:
        if len(cells) != 4:
            report.error(path, "a Use cases row has %d columns, expected 4" % len(cells))
            continue
        use_case, counter, implementation, summary = cells
        if not COUNTER.match(counter):
            report.error(path, "Scenarios must read declared/covered/tested, found %r" % counter)
        problem = implementation_problem(implementation, source)
        if problem:
            report.error(path, "the Implementation column: %s, found %r" % (problem, implementation))
        if len(summary) > 120:
            report.error(path, "the summary is %d characters, 120 at most: %r" % (len(summary), summary[:60]))
        link = re.search(r"\]\((details/[^)]+\.md)\)", use_case)
        if link:
            linked.add(link.group(1))
        else:
            report.error(path, "the Use case column must link to its detail entry, found %r" % use_case)

    if source == FUNCTIONALITY:
        # No tree to hash for an observed functionality: the anchor is the observation date.
        # A coordinate this repository holds may still carry its tree SHA.
        for cells in table_rows(body, "Anchors"):
            if len(cells) != 2:
                report.error(path, "an Anchors row has %d columns, expected 2" % len(cells))
                continue
            anchor = cells[1].strip("`")
            if not (SHA.fullmatch(anchor) or OBSERVED_ANCHOR.match(anchor)):
                report.error(
                    path,
                    "an anchor reads %r, expected a tree SHA or '%s observed YYYY-MM-DD'" % (cells[1], EM_DASH),
                )


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
            # deployable on the wire, and a returned outcome can carry one. An em dash is
            # accepted in both cells whatever the mechanism: an exception or a code that cannot
            # be observed is not recorded.
            report.error(path, "mechanism %r carries an exception %r" % (mechanism, exception))


def check_detail(body, source, path, report):
    for line in SOURCE_LINES[source]:
        if line not in body:
            report.error(path, "missing the source-%s line %r" % (source, line))
    for cells in table_rows(body, "The rules it applies"):
        if len(cells) != 3:
            report.error(path, "a rules row has %d columns, expected 3" % len(cells))


def validate_file(path, report, linked):
    """Validate one file and return (source, frontmatter), or (None, None) when its header
    cannot be read."""
    text = io.open(path, encoding="utf-8").read()
    keys, body = split_frontmatter(text, path, report)
    if keys is None:
        return None, None
    kind = check_frontmatter(keys, path, report)
    if kind is None:
        return None, None
    source = source_of(keys)
    if not keys.get("base"):
        if "`base` is empty" not in body:
            report.warn(path, "base is empty and the body does not say why")
    body = check_blockquote(body, kind, source, path, report)
    check_sections(body, kind, path, report)
    check_banned(body, path, report)
    if kind == "map":
        check_map(body, source, path, report, linked)
    elif kind == "refusal-surface":
        check_refusals(body, path, report)
    else:
        check_detail(body, source, path, report)
    return source, keys


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

    sources = {}
    frontmatters = {}
    for path in targets:
        sources[path], frontmatters[path] = validate_file(path, report, linked)

    # One set, one source: the map declares it and every other file follows.
    set_source = sources.get(os.path.join(root, "map.md"))
    if set_source:
        for path in targets:
            if sources[path] and sources[path] != set_source:
                report.error(path, "source is %r while the map declares %r" % (sources[path], set_source))

    # With source functionality the implementation name is the implementation's only identity:
    # two detail entries naming the same implementation are two descriptions of one thing.
    if set_source == FUNCTIONALITY:
        names = [
            frontmatters[p].get("implementation", "")
            for p in details
            if frontmatters.get(p) and frontmatters[p].get("kind") == "detail-entry"
        ]
        report_duplicates(names, details_dir, "across the detail entries' implementation keys", report)

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
        "\ncartography format %s - source %s - %d file(s), %d error(s), %d warning(s)"
        % (FORMAT_VERSION, set_source or "unknown", len(targets), len(report.errors), len(report.warnings))
    )
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
