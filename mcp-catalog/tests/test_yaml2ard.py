"""Tests for yaml2ard.py. Run from mcp-catalog/:  python3 -m unittest discover tests"""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(ROOT, "yaml2ard.py")
CATALOG = os.path.join(ROOT, "bio-nih-mcp.yaml")
FIXTURE = os.path.join(HERE, "fixtures", "mixed-kinds.example.yaml")
CONFORMANCE = os.path.join(ROOT, "vendor", "ard-spec", "conformance", "bin", "conformance-test")


def run(*args):
    p = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def entries_of(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["entries"]


class Yaml2Ard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def out(self, name):
        return os.path.join(self.tmp.name, name)

    def write_yaml(self, doc):
        path = self.out("in.yaml")
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(doc, f, sort_keys=False)
        return path

    def test_catalog_output_matches_committed_files(self):
        """Default output for the real catalog is unchanged (backward compatible)."""
        for extra, committed in (([], "ard.json"), (["--strip-curation"], "ard.pure.json")):
            code, log = run(CATALOG, "-o", self.out(committed), *extra)
            self.assertEqual(code, 0, log)
            self.assertIn("0 errors", log)
            self.assertEqual(entries_of(self.out(committed)), entries_of(os.path.join(ROOT, committed)))

    def test_fixture_is_clean(self):
        code, log = run(FIXTURE, "--check")
        self.assertEqual(code, 0, log)
        self.assertIn("3 entries | JSON Schema: passed | 0 errors, 1 warnings", log)  # placeholder IRI only

    def test_kind_filter(self):
        for kinds, ids in ((["skill"], ["demo-skill"]), (["mcp", "plugin"], ["demo-mcp", "demo-plugin"])):
            code, log = run(FIXTURE, "-o", self.out("k.json"), "--kind", *kinds)
            self.assertEqual(code, 0, log)
            self.assertEqual([e["identifier"].rsplit(":", 1)[1] for e in entries_of(self.out("k.json"))], ids)

    def test_kind_aware_curation_warnings(self):
        with open(FIXTURE, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        doc = copy.deepcopy(doc)
        skill = doc["entries"][1]
        skill["cat:transport"] = ["stdio"]          # MCP-only term on a skill
        del skill["cat:agents"]                      # expected on skills
        skill["cat:requires"] = ["urn:air:example.org:test-catalog:missing"]
        skill["cat:urlKind"] = "mcp-endpoint"
        skill["cat:rol"] = "optional"                # typo
        code, log = run(self.write_yaml(doc), "--check")
        self.assertEqual(code, 0, log)               # warnings never change the exit code
        self.assertIn("cat:transport belongs to mcp entries; unexpected on a skill entry", log)
        self.assertIn("skill entry has no cat:agents", log)
        self.assertIn("not an identifier in this catalog", log)
        self.assertIn("cat:urlKind 'mcp-endpoint' is not one of", log)
        self.assertIn("cat:rol is not a documented curation term", log)

    def test_errors_still_exit_1(self):
        with open(FIXTURE, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        doc["entries"][1]["url"] = "not-a-url"
        code, log = run(self.write_yaml(doc), "--check")
        self.assertEqual(code, 1, log)

    def test_split(self):
        index = self.out("ard.json")
        code, log = run(FIXTURE, "-o", index, "--split", "--base-url", "https://example.org/cat/")
        self.assertEqual(code, 0, log)
        idx = entries_of(index)
        self.assertEqual([e["type"] for e in idx], ["application/ai-catalog+json"] * 3)
        self.assertEqual([e["url"] for e in idx], [f"https://example.org/cat/ard.{k}.json"
                                                   for k in ("mcp", "skill", "plugin")])
        self.assertEqual(idx[1]["identifier"], "urn:air:example.org:test-catalog:catalog-skill")
        for k in ("mcp", "skill", "plugin"):
            self.assertEqual(len(entries_of(self.out(f"ard.{k}.json"))), 1)
        if os.path.exists(CONFORMANCE):
            for name in ("ard.json", "ard.mcp.json", "ard.skill.json", "ard.plugin.json"):
                p = subprocess.run([sys.executable, CONFORMANCE, "manifest", self.out(name)],
                                   capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_split_needs_base_url(self):
        code, log = run(FIXTURE, "-o", self.out("ard.json"), "--split")
        self.assertEqual(code, 2, log)


if __name__ == "__main__":
    unittest.main()
