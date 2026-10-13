#!/usr/bin/env python3
"""Tests for the Hermes hook wrapper (fail closed) and the memory templates."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HOOK = REPO / "hermes-home" / "agent-hooks" / "privacy-guard.py"
MEMORIES = REPO / "0 - System" / "memories"
ENTRY_DELIMITER = "\n§\n"  # Hermes' memory entry separator

# A stand-in policy: blocks any payload that mentions "secret", like the real guard
# blocks any payload naming the private folder.
STUB_POLICY = '''
import json
def run_hermes(stdin_text):
    blocked = "secret" in stdin_text
    print(json.dumps({"decision": "block", "reason": "stub"} if blocked else {}))
    return 0
'''


class HermesHookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write_policy(self, source):
        scripts = self.vault / "0 - System" / "scripts"
        scripts.mkdir(parents=True, exist_ok=True)
        (scripts / "privacy_guard.py").write_text(source, encoding="utf-8")

    def run_hook(self, payload, vault=True):
        env = {k: v for k, v in os.environ.items() if k != "HERMES_VAULT"}
        if vault:
            env["HERMES_VAULT"] = str(self.vault)
        r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                           capture_output=True, text=True, env=env, timeout=10)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def assertBlocked(self, decision):
        self.assertEqual(decision.get("decision"), "block")

    def test_blocks_when_vault_is_not_set(self):
        self.write_policy(STUB_POLICY)
        self.assertBlocked(self.run_hook({"tool_input": {}}, vault=False))

    def test_blocks_when_policy_is_missing(self):
        self.assertBlocked(self.run_hook({"tool_input": {}}))

    def test_blocks_when_policy_fails_to_load(self):
        self.write_policy("this is not python (")
        self.assertBlocked(self.run_hook({"tool_input": {}}))

    def test_blocks_when_policy_has_no_hermes_entry_point(self):
        self.write_policy("x = 1\n")
        self.assertBlocked(self.run_hook({"tool_input": {}}))

    def test_delegates_the_decision_to_the_policy(self):
        self.write_policy(STUB_POLICY)
        self.assertEqual(self.run_hook({"tool_input": {"command": "ls notes"}}), {})
        self.assertBlocked(self.run_hook({"tool_input": {"command": "cat secret"}}))


class MemoryTemplateTest(unittest.TestCase):
    def test_templates_parse_as_hermes_entries(self):
        for name in ("USER.md", "MEMORY.md"):
            text = (MEMORIES / name).read_text(encoding="utf-8")
            self.assertFalse(text.startswith("---"), f"{name}: no frontmatter in memory files")
            entries = [e.strip() for e in text.split(ENTRY_DELIMITER)]
            self.assertGreater(len(entries), 1, name)
            self.assertTrue(all(entries), f"{name}: empty entry")


if __name__ == "__main__":
    unittest.main()
