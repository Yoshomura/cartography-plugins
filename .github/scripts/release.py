"""The release of this marketplace: two levels of semantic versions, both published at the merge.

    python3 .github/scripts/release.py check-pr <base-ref> <body-file> <labels-json>
        exit 1 naming every problem with the pull request
    python3 .github/scripts/release.py next <labels-json>
        prints the repository version the merge publishes, nothing under release:none
    python3 .github/scripts/release.py plugin-tags
        prints the `<plugin>--v<version>` tag of every plugin whose current version is not tagged
    python3 .github/scripts/release.py notes <body-file>
        prints the `## Release notes` section of a pull request body

Two versions, both Semantic Versioning 2.0.0 strings with no `v` prefix:

- **The repository version** is what a consumer pins with `ref`: a `ref` checks out the whole
  marketplace at one commit. It lives in no file. A pull request declares the level of its
  change with exactly one label, release:major, release:minor, release:patch or release:none,
  and the merge publishes the highest semantic version tag raised by that level as tag `X.Y.Z`,
  or the floor 1.0.0 when no release exists yet.
- **A plugin version** says what a user of that plugin risks. It is the `version` of the
  plugin's `plugin.json`, never of the marketplace entry. Every pull request that changes a
  plugin raises its version, and the merge tags it `<plugin>--v<version>`, the convention
  Claude Code resolves dependency version ranges against.

The repository level is at least the highest plugin level of the pull request: a plugin raised
to a new major, or removed from the catalog, makes the repository release a major. Nothing is
ever committed to master by the workflow: it writes tags and a release only.
"""

import json
import re
import subprocess
import sys

import semver

LEVELS = ("major", "minor", "patch", "none")
RANK = {"none": 0, "patch": 1, "minor": 2, "major": 3}
PREFIX = "release:"
FLOOR = "1.0.0"
RELEASED = ("plugins/", ".claude-plugin/")
MARKETPLACE = ".claude-plugin/marketplace.json"
PLUGIN_TAG = "%s--v%s"
NOTES = re.compile(r"^## Release notes[ \t]*\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)


def git(*args, check=True):
    result = subprocess.run(["git", *args], check=check, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else None


def level_of(labels):
    """The level the labels declare, or the list of problems with them."""
    declared = [label for label in labels if label.startswith(PREFIX)]
    if len(declared) != 1:
        found = ", ".join(declared) or "none"
        return None, ["exactly one release label is required (%s), found: %s"
                      % ("|".join(PREFIX + level for level in LEVELS), found)]
    level = declared[0][len(PREFIX):]
    if level not in LEVELS:
        return None, ["unknown release label %s" % declared[0]]
    return level, []


def notes_of(body):
    # The section runs to the next `## ` heading. When it is the last one, the body's signature
    # (a trailing Co-authored-by line) follows it and is not part of the notes.
    match = NOTES.search(body.replace("\r\n", "\n"))
    if not match:
        return ""
    lines = match.group(1).rstrip().split("\n")
    while lines and (not lines[-1].strip() or lines[-1].lower().startswith("co-authored-by:")):
        lines.pop()
    return "\n".join(lines).strip()


def latest():
    """The highest semantic version among the repository tags, None when no release exists."""
    tags = [tag for tag in git("tag", "--list").split() if semver.SEMVER.match(tag)]
    best = None
    for tag in tags:
        if best is None or semver.compare(tag, best) > 0:
            best = tag
    return best


def next_version(level):
    if level == "none":
        return None
    current = latest()
    return FLOOR if current is None else semver.bump(current, level)


def plugin_versions(ref=None):
    """{plugin directory name: version or None}, read at `ref`, or in the working tree."""
    listing = git("ls-tree", "-r", "--name-only", ref, "plugins/") if ref else git(
        "ls-files", "plugins/")
    if listing is None:
        return {}
    versions = {}
    for path in listing.split():
        parts = path.split("/")
        if len(parts) == 4 and parts[2] == ".claude-plugin" and parts[3] == "plugin.json":
            text = git("show", "%s:%s" % (ref, path)) if ref else open(path, encoding="utf-8").read()
            versions[parts[1]] = json.loads(text).get("version")
    return versions


def level_between(old, new):
    """The semver level that leads from `old` to `new`, None when `new` is not higher."""
    if semver.compare(new, old) <= 0:
        return None
    (old_core, _), (new_core, _) = semver.parse(old), semver.parse(new)
    if new_core[0] != old_core[0]:
        return "major"
    if new_core[1] != old_core[1]:
        return "minor"
    return "patch"


def check_pr(base, body_file, labels_json):
    problems = []
    level, label_problems = level_of(json.loads(labels_json))
    problems += label_problems

    changed = git("diff", "--name-only", "%s...HEAD" % base).split()
    released = [path for path in changed if path.startswith(RELEASED)]
    if level == "none" and released:
        problems.append("release:none, but released content changed: %s" % ", ".join(released))

    with open(body_file, encoding="utf-8") as handle:
        body = handle.read()
    if level not in (None, "none") and not notes_of(body):
        problems.append("release:%s needs a non-empty '## Release notes' section in the body" % level)

    with open(MARKETPLACE, encoding="utf-8") as handle:
        for entry in json.load(handle).get("plugins", []):
            if "version" in entry:
                problems.append("the marketplace entry %s carries a version; it belongs in its plugin.json"
                                % entry.get("name"))

    # Every plugin carries a valid version; every changed plugin raises it.
    before, after = plugin_versions(base), plugin_versions()
    highest = "none"
    for name, version in sorted(after.items()):
        if not version or not semver.SEMVER.match(version):
            problems.append("plugins/%s/.claude-plugin/plugin.json needs a semantic version, found %r"
                            % (name, version))
            continue
        touched = any(path.startswith("plugins/%s/" % name) for path in changed)
        old = before.get(name)
        if not touched:
            continue
        if not old:
            print("%s starts at %s." % (name, version))
            continue
        step = level_between(old, version)
        if step is None:
            problems.append("plugins/%s/ changed, but its version stays at %s; raise it" % (name, version))
            continue
        print("%s: %s -> %s, a %s." % (name, old, version, step))
        highest = max(highest, step, key=RANK.get)
    for name in sorted(set(before) - set(after)):
        print("%s is removed from the catalog, a major." % name)
        highest = "major"
    if level in RANK and RANK[level] < RANK[highest]:
        problems.append("the plugins move by a %s, the label release:%s is lower; use release:%s"
                        % (highest, level, highest))

    for problem in problems:
        print("::error::%s" % problem)
    if problems:
        return 1
    print("release:%s, merging publishes %s." % (level, next_version(level) or "no repository version"))
    return 0


def plugin_tags():
    existing = set(git("tag", "--list").split())
    for name, version in sorted(plugin_versions().items()):
        if version and semver.SEMVER.match(version):
            tag = PLUGIN_TAG % (name, version)
            if tag not in existing:
                print(tag)
    return 0


def main(argv):
    if len(argv) == 5 and argv[1] == "check-pr":
        return check_pr(argv[2], argv[3], argv[4])
    if len(argv) == 3 and argv[1] == "next":
        level, problems = level_of(json.loads(argv[2]))
        if problems:
            for problem in problems:
                print("::error::%s" % problem, file=sys.stderr)
            return 1
        print(next_version(level) or "")
        return 0
    if len(argv) == 2 and argv[1] == "plugin-tags":
        return plugin_tags()
    if len(argv) == 3 and argv[1] == "notes":
        with open(argv[2], encoding="utf-8") as handle:
            print(notes_of(handle.read()))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
