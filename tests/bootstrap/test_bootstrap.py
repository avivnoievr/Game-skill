"""Executable discovery contracts and preservation of an existing project install."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
FINDER = ROOT / "plugins/game-studio/skills/game-studio/scripts/find_blender.sh"


class BootstrapTests(unittest.TestCase):
    def probe(self, path):
        return subprocess.run(["bash", str(FINDER)], env={**os.environ, "BLENDER": str(path)},
                              capture_output=True, text=True)

    def fake_blender(self, folder, version):
        path = Path(folder) / "Blender with spaces"
        path.write_text("#!/bin/sh\nprintf 'GS_BLENDER_PROBE\\t" + version + "\\n'\n")
        path.chmod(0o755)
        return path

    def test_explicit_existing_executable_with_spaces(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.fake_blender(folder, "4.3.2")
            result = self.probe(path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), str(path) + "\t4.3.2")

    def test_old_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.probe(self.fake_blender(folder, "4.1.9"))
            self.assertEqual(result.returncode, 2)

    def test_bad_override_does_not_silently_use_system_blender(self):
        result = self.probe("/missing/game-studio-blender")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_upgrade_preserves_user_changes_and_unrelated_agents(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            old = target / ".claude/skills/game-studio"
            agents = target / ".claude/agents"
            old.mkdir(parents=True)
            agents.mkdir(parents=True)
            (old / "personal.txt").write_text("custom source")
            (agents / "asset-builder.md").write_text("custom builder")
            (agents / "unrelated.md").write_text("leave intact")
            result = subprocess.run(["bash", str(ROOT / "install.sh"), folder],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            backups = list((target / ".claude/game-studio-backups").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual((backups[0] / "skills/game-studio/personal.txt").read_text(), "custom source")
            self.assertEqual((backups[0] / "agents/asset-builder.md").read_text(), "custom builder")
            self.assertEqual((agents / "unrelated.md").read_text(), "leave intact")
            self.assertTrue((old / "SKILL.md").is_file())
            self.assertTrue((old / "THIRD_PARTY_NOTICES.md").is_file())
            self.assertIn("../THIRD_PARTY_NOTICES.md", (old / "references/design-loading.md").read_text())


if __name__ == "__main__":
    unittest.main()
