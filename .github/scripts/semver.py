"""Semantic Versioning 2.0.0 for the release workflow: validate versions, compare two of them.

    python3 .github/scripts/semver.py valid <version>...     exit 1 naming each invalid one
    python3 .github/scripts/semver.py compare <a> <b>        prints -1, 0 or 1 (a against b)
    python3 .github/scripts/semver.py bump <version> <level> prints the next version, level major|minor|patch

Every version this repository publishes is checked here: the repository version, each plugin
version, and therefore every tag. `sort -V` is not used for ordering because it ranks
1.0.0-rc.1 after 1.0.0, which semver forbids. Build metadata (`+...`) is ignored in ordering,
as section 10 of the specification requires.
"""

import re
import sys

# The regular expression published with the specification (semver.org, FAQ), unchanged.
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def parse(version):
    match = SEMVER.match(version)
    if not match:
        raise ValueError(version)
    core = tuple(int(part) for part in match.group(1, 2, 3))
    pre = match.group(4)
    return core, (pre.split(".") if pre else [])


def compare_pre(a, b):
    # A version without prerelease ranks above one with it (spec, section 11.3).
    if not a or not b:
        return (len(a) == 0) - (len(b) == 0)
    for x, y in zip(a, b):
        if x == y:
            continue
        x_num, y_num = x.isdigit(), y.isdigit()
        if x_num and y_num:
            return (int(x) > int(y)) - (int(x) < int(y))
        if x_num != y_num:
            return -1 if x_num else 1  # numeric identifiers rank below alphanumeric ones
        return (x > y) - (x < y)
    return (len(a) > len(b)) - (len(a) < len(b))


def compare(a, b):
    (core_a, pre_a), (core_b, pre_b) = parse(a), parse(b)
    if core_a != core_b:
        return (core_a > core_b) - (core_a < core_b)
    return compare_pre(pre_a, pre_b)


LEVELS = ("major", "minor", "patch")


def bump(version, level):
    # A prerelease is promoted to its own version (1.1.0-rc.1 -> 1.1.0) whatever the level:
    # the prerelease already announced the version it leads to. Build metadata is dropped.
    (major, minor, patch), pre = parse(version)
    if level not in LEVELS:
        raise ValueError(level)
    if pre:
        return "%d.%d.%d" % (major, minor, patch)
    if level == "major":
        return "%d.0.0" % (major + 1)
    if level == "minor":
        return "%d.%d.0" % (major, minor + 1)
    return "%d.%d.%d" % (major, minor, patch + 1)


def main(argv):
    if len(argv) == 4 and argv[1] == "bump":
        try:
            print(bump(argv[2], argv[3]))
        except ValueError as error:
            print("not a semantic version or a level (major|minor|patch): %r" % str(error))
            return 2
        return 0
    if len(argv) >= 3 and argv[1] == "valid":
        bad = [v for v in argv[2:] if not SEMVER.match(v)]
        for v in bad:
            print("not a semantic version (MAJOR.MINOR.PATCH[-prerelease][+build], no 'v'): %r" % v)
        return 1 if bad else 0
    if len(argv) == 4 and argv[1] == "compare":
        try:
            print(compare(argv[2], argv[3]))
        except ValueError as error:
            print("not a semantic version: %r" % str(error))
            return 2
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
