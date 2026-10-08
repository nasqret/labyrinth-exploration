"""Validate the Codex interface using a YAML parser, without model calls."""
import unittest
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO = Path(__file__).resolve().parents[1]


@unittest.skipUnless(yaml, "Codex metadata validation needs PyYAML")
class CodexMetadata(unittest.TestCase):
    def test_interface_and_invocation(self):
        metadata = yaml.safe_load((REPO / "agents" / "openai.yaml").read_text(encoding="utf-8"))
        self.assertIsInstance(metadata, dict)
        interface = metadata["interface"]
        self.assertIsInstance(interface["display_name"], str)
        self.assertTrue(interface["display_name"].strip())
        self.assertIsInstance(interface["short_description"], str)
        self.assertTrue(25 <= len(interface["short_description"]) <= 64)
        self.assertIsInstance(interface["default_prompt"], str)
        self.assertIn("$labyrinth-exploration", interface["default_prompt"])
        self.assertIs(metadata.get("policy", {}).get("allow_implicit_invocation", True), True)
        self.assertFalse(metadata.get("dependencies", {}).get("tools"),
                         "The research method needs no mandatory external tool connection")


if __name__ == "__main__":
    unittest.main()
