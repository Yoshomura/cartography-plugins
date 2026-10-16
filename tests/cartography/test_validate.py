"""Run the cartography validator against every fixture set.

    python -m unittest discover -s tests/cartography -v

A fixture folder named `pass-*` must exit 0, one named `fail-*` must exit 1 and print the
errors listed for it below. Standard library only.
"""

import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
VALIDATOR = os.path.join(REPO, "plugins", "cartography", "skills", "cartography", "scripts", "validate.py")
FIXTURES = os.path.join(HERE, "fixtures")

# Each failing fixture, with a fragment of every error it must report.
EXPECTED_ERRORS = {
    "fail-functionality-with-paths": [
        "with source functionality the implementation is a plain name, never a file path, found '`src/account/SignIn.cs`'",
        "with source functionality the implementation is a plain name, never a file path, found 'SignIn.ts'",
        "an anchor reads '2026-10-15'",
        "missing the source-functionality line",
    ],
    "fail-functionality-duplicate-name": [
        "the implementation name 'Sign in' appears 2 times in the Use cases table",
        "the implementation name 'Sign in' appears 2 times across the detail entries' implementation keys",
    ],
    "fail-pre-2-vocabulary": [
        "sections are ['Usecases', 'Inbound', 'Outbound', 'Anchors', 'Unattached']",
        "frontmatter is missing the key 'use-case'",
        "frontmatter is missing the key 'implementation'",
        "frontmatter carries the unexpected key 'scenario'",
        "frontmatter carries the unexpected key 'usecase'",
        "with source functionality the implementation is a name, and it is empty",
        "details/ACC-01.md: is linked from no row of the map",
        "details/ACC-02.md: is linked from no row of the map",
    ],
    "fail-code-malformed": [
        "with source code the implementation must be a file path with an extension, found 'Sign in'",
        "source is 'functionality' while the map declares 'code'",
    ],
}


def run(fixture):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, VALIDATOR, os.path.join(FIXTURES, fixture)],
        capture_output=True,
        encoding="utf-8",
        env=env,
    )
    return result.returncode, result.stdout


class ValidatorFixtures(unittest.TestCase):
    def test_every_fixture(self):
        names = sorted(os.listdir(FIXTURES))
        self.assertTrue(names, "no fixture found")
        for name in names:
            with self.subTest(fixture=name):
                code, out = run(name)
                if name.startswith("pass-"):
                    self.assertEqual(code, 0, out)
                    self.assertIn(" 0 error(s)", out)
                else:
                    self.assertTrue(name.startswith("fail-"), "unexpected fixture name %r" % name)
                    self.assertEqual(code, 1, out)
                    for fragment in EXPECTED_ERRORS[name]:
                        self.assertIn(fragment, out)
                    expected_count = " %d error(s)" % len(EXPECTED_ERRORS[name])
                    self.assertIn(expected_count, out)


if __name__ == "__main__":
    unittest.main()
