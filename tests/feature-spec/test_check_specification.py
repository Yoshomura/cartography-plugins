"""Run the specification checker against every fixture.

    python -m unittest discover -s tests/feature-spec -v

A fixture folder named `pass-*` must exit 0, one named `fail-*` must exit 1 and print the
errors listed for it below. Standard library only.
"""

import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CHECKER = os.path.join(REPO, "plugins", "feature-spec", "skills", "workflow-feature-spec", "scripts",
                       "check_specification.py")
FIXTURES = os.path.join(HERE, "fixtures")

# Each failing fixture, with a fragment of every error it must report.
EXPECTED_ERRORS = {
    "fail-sign-in": [
        "the status must be draft or ready, found 'later'",
        "SIGNIN-INVARIANT identifiers are numbered [2]",
        "the use case ID LOGIN-EMAIL does not start with the feature ID SIGNIN-",
        "the use case file sign-in-with-email-code.md is not listed in the Use cases table",
        "the heading 'SIGNIN-PASSKEY-RULE-1' does not start with SIGNIN-PASSKEY-BUSINESS-RULE-<n>",
        "write BUSINESS-RULE, never RULE alone",
        "SIGNIN-PASSKEY-SCENARIO identifiers are numbered [1, 3]",
        "SIGNIN-PASSKEY-SCENARIO-1: the sentence is 139 characters, 120 at most",
        "found ['Given', 'Then']",
        "SIGNIN-PASSKEY-SCENARIO-3 has no sentence before its Given / When / Then",
        "the Use cases table links to sign-in-with-google.md, which does not exist",
    ],
}


def run(fixture):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, CHECKER, os.path.join(FIXTURES, fixture)],
        capture_output=True,
        encoding="utf-8",
        env=env,
    )
    return result.returncode, result.stdout


class CheckerFixtures(unittest.TestCase):
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
                    self.assertIn(" %d error(s)" % len(EXPECTED_ERRORS[name]), out)


if __name__ == "__main__":
    unittest.main()
