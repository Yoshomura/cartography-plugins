"""Check the c4 plugin's generators.

    python -m unittest discover -s tests/c4 -v

Standard library only. The Mermaid rendering (Node.js and Playwright) is not exercised: the draw.io
generation, the model checks and the model -> Mermaid -> model round trip are.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SKILLS = os.path.join(REPO, "plugins", "c4", "skills")
VIEW = os.path.join(SKILLS, "c4-subdomain-view", "scripts", "subdomain_view.py")
FROM_MERMAID = os.path.join(SKILLS, "c4-subdomain-view", "scripts", "from_mermaid.py")
EXAMPLE = os.path.join(SKILLS, "c4-subdomain-view", "examples", "ordering.json")
LEVEL1 = os.path.join(SKILLS, "c4-diagrams", "examples", "context_level1.py")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def save(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle)


def run(args, **env):
    return subprocess.run([sys.executable, "-X", "utf8"] + args, capture_output=True, text=True,
                          encoding="utf-8", env={**os.environ, **env})


class Level1Example(unittest.TestCase):
    def test_no_card_crossing(self):
        with tempfile.TemporaryDirectory() as out:
            r = run([LEVEL1], C4_OUT=out)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("card-crossings 0", r.stdout)
            ET.parse(os.path.join(out, "Context.drawio"))
            self.assertTrue(os.path.exists(os.path.join(out, "Context.html")))


class SubdomainDrawio(unittest.TestCase):
    def test_example_routes_every_link(self):
        with tempfile.TemporaryDirectory() as out:
            r = run([VIEW, "drawio", EXAMPLE, "--drawio-dir", out])
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("unrouted 0", r.stdout)
            root = ET.parse(os.path.join(out, "c4-ordering.drawio")).getroot()
            edges = [c for c in root.iter("mxCell") if c.get("edge") == "1" and c.get("source")]
            self.assertGreaterEqual(len(edges), 18)
            names = {o.get("C4Name") for o in root.iter("object")}
            self.assertTrue({"ordering-api", "Orders DB", "orders data sink", "Payment"} <= names)

    def test_redis_key_is_refused_as_a_message(self):
        model = load(EXAMPLE)
        model["messages"].append({"from": "orderingapi", "to": "redis",
                                  "groups": [{"kind": "Redis key", "names": ["cart:{id}"]}]})
        with tempfile.TemporaryDirectory() as out:
            path = os.path.join(out, "bad.json")
            save(path, model)
            r = run([VIEW, "drawio", path, "--drawio-dir", out])
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("is a cache access, not a message", r.stdout + r.stderr)

    def test_unknown_end_is_refused(self):
        model = load(EXAMPLE)
        model["links"].append({"from": "orderingapi", "to": "nowhere", "label": "Call", "protocol": "HTTP"})
        with tempfile.TemporaryDirectory() as out:
            path = os.path.join(out, "bad.json")
            save(path, model)
            r = run([VIEW, "drawio", path, "--drawio-dir", out])
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("nowhere", r.stdout + r.stderr)


class MermaidRoundTrip(unittest.TestCase):
    def test_model_to_mermaid_to_model(self):
        sys.path.insert(0, os.path.dirname(VIEW))
        import subdomain_view
        model = subdomain_view.Model(EXAMPLE)
        code = subdomain_view.mermaid_code(model)
        with tempfile.TemporaryDirectory() as out:
            md = os.path.join(out, "view.md")
            with open(md, "w", encoding="utf-8") as handle:
                handle.write(subdomain_view.view_md(model, code))
            r = run([FROM_MERMAID, md])
            self.assertEqual(r.returncode, 0, r.stderr)
            back = json.loads(r.stdout)
        source = load(EXAMPLE)
        self.assertEqual(back["system"], source["system"])
        self.assertEqual(back["focus"], source["focus"])
        self.assertEqual({c["id"] for c in back["containers"]}, {c["id"] for c in source["containers"]})
        self.assertEqual({e["id"] for e in back["externals"]}, {e["id"] for e in source["externals"]})
        self.assertEqual({s["id"] for s in back["subdomains"]}, {s["id"] for s in source["subdomains"]})
        self.assertEqual(len(back["links"]), len(source["links"]))


if __name__ == "__main__":
    unittest.main()
