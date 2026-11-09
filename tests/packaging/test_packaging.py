"""Packaging of every plugin: license, icon, and the provenance line of what it generates.

    python -m unittest discover -s tests/packaging

The provenance line, `Generated with <plugin> <version> (<repository>)`, is written by hand in a
template or a script. It carries the plugin version, so a version raised in `plugin.json` alone
would leave it wrong: these tests fail until both move together.
"""

import io
import json
import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLUGINS = os.path.join(REPO, "plugins")
URL = "https://github.com/Yoshomura/cartography-plugins"

# Every file that carries the provenance line, per plugin.
PROVENANCE = {
    "cartography": [
        "skills/cartography/references/map.code.template.md",
        "skills/cartography/references/map.functionality.template.md",
    ],
    "feature-spec": ["skills/workflow-feature-spec/references/feature.template.md"],
    "c4": [
        "skills/c4-diagrams/scripts/c4lib.py",
        "skills/c4-diagrams/examples/context_level1.mmd",
    ],
}


def read(*parts):
    with io.open(os.path.join(*parts), encoding="utf-8") as handle:
        return handle.read()


def manifest(plugin):
    return json.loads(read(PLUGINS, plugin, ".claude-plugin", "plugin.json"))


class Packaging(unittest.TestCase):
    def test_every_plugin_is_covered(self):
        self.assertEqual(sorted(PROVENANCE), sorted(os.listdir(PLUGINS)))

    def test_license_travels_with_the_plugin(self):
        root = read(REPO, "LICENSE")
        self.assertIn("Copyright (c) 2026 Nicolas Jouet (Yoshomura)", root)
        for plugin in PROVENANCE:
            with self.subTest(plugin=plugin):
                self.assertEqual(manifest(plugin)["license"], "MIT")
                self.assertEqual(read(PLUGINS, plugin, "LICENSE"), root)

    def test_icon_is_a_file_inside_the_plugin(self):
        for plugin in PROVENANCE:
            with self.subTest(plugin=plugin):
                icon = manifest(plugin)["icon"]
                self.assertTrue(icon.startswith("./"), icon)
                self.assertTrue(os.path.isfile(os.path.join(PLUGINS, plugin, icon)), icon)

    def test_provenance_line_carries_the_plugin_version(self):
        for plugin, paths in PROVENANCE.items():
            line = "Generated with %s %s (%s)" % (plugin, manifest(plugin)["version"], URL)
            for path in paths:
                with self.subTest(plugin=plugin, path=path):
                    self.assertIn(line, read(PLUGINS, plugin, path))


if __name__ == "__main__":
    unittest.main()
