"""Release-boundary checks: committed input, exact approval and preservation."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "tools/prepare_distribution.py"


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.run_git("init", "-b", "main")
        files = {
            "plugins/game-studio/.claude-plugin/plugin.json": json.dumps({"version": "1.1.1", "repository": "old"}).encode(),
            "plugins/game-studio/skills/game-studio/SKILL.md": b"committed instructions\n",
            "plugins/game-studio/skills/game-studio/vendor/LICENSE": b"preserve source license\n",
            "plugins/game-studio/skills/game-studio/vendor/image.jpg": b"\xff\xd8binary reference\xff\xd9",
            "tests/fixture.txt": b"regression fixture\n",
            "tests/distribution/development-only.txt": b"preparer tests stay with preparer\n",
            "install.sh": b"#!/bin/sh\nexit 0\n",
            "distribution/README.template.md": b"{{VERSION}} {{SOURCE_SHA}} {{STATUS}}\n",
            "distribution/config.json": json.dumps({
                "source_repository": "owner/development", "publication_repository": "owner/publication",
                "include": ["plugins", "tests", "install.sh"],
                "exclude": ["tests/distribution"],
                "templates": {"distribution/README.template.md": "README.md"},
            }).encode(),
        }
        for path, data in files.items():
            dest = self.source / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        (self.source / "install.sh").chmod(0o755)
        self.run_git("add", ".")
        self.run_git("-c", "user.name=Release test fixture", "-c", "user.email=fixture@example.invalid",
                     "commit", "-m", "Synthetic release test input")
        self.sha = self.run_git("rev-parse", "HEAD").stdout.strip()

    def run_git(self, *args):
        return subprocess.run(["git", "-C", str(self.source), *args], capture_output=True, text=True, check=True)

    def prepare(self, target="candidate", extra=(), ref=None, version="1.1.1"):
        return subprocess.run([sys.executable, str(SCRIPT), "--source", str(self.source),
                               "--ref", ref or self.sha, "--version", version,
                               "--output", str(self.root / target), *extra], capture_output=True, text=True)

    def approval(self, **overrides):
        value = {"approved": True, "approved_by": "SYNTHETIC TEST ONLY", "approved_at": "2000-01-01",
                 "source_commit": self.sha, "version": "1.1.1", "checks": ["synthetic fixture"],
                 "observed_result": "test fixture, not a human approval", "limitations": ["not a real release"]}
        value.update(overrides)
        path = self.root / "fixture-approval.json"
        path.write_text(json.dumps(value))
        return ("--approval-record", str(path))

    def test_committed_snapshot_ignores_later_edits_and_preserves_binary_and_modes(self):
        skill = self.source / "plugins/game-studio/skills/game-studio/SKILL.md"
        skill.write_text("uncommitted later change\n")
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        out = self.root / "candidate"
        self.assertEqual((out / skill.relative_to(self.source)).read_bytes(), b"committed instructions\n")
        binary = "plugins/game-studio/skills/game-studio/vendor/image.jpg"
        self.assertEqual((out / binary).read_bytes(), (self.source / binary).read_bytes())
        self.assertEqual((out / "install.sh").stat().st_mode & 0o777, 0o755)
        manifest = json.loads((out / "RELEASE.json").read_text())
        self.assertEqual(manifest["status"], "candidate")
        self.assertIsNone(manifest["approval"])
        for entry in manifest["files"]:
            self.assertEqual(entry["sha256"], hashlib.sha256((out / entry["path"]).read_bytes()).hexdigest())
        self.assertTrue((out / "tests/fixture.txt").exists())
        self.assertFalse((out / "tests/distribution").exists())
        self.assertTrue((out / "plugins/game-studio/skills/game-studio/vendor/LICENSE").exists())

    def test_existing_output_is_preserved(self):
        self.assertEqual(self.prepare().returncode, 0)
        marker = self.root / "candidate/personal-note.txt"
        marker.write_text("keep this")
        self.assertEqual(self.prepare().returncode, 2)
        self.assertEqual(marker.read_text(), "keep this")

    def test_moving_branch_and_wrong_version_cannot_be_exported(self):
        self.assertEqual(self.prepare(ref="main").returncode, 2)
        self.assertEqual(self.prepare(version="9.9.9").returncode, 2)
        self.assertFalse((self.root / "candidate").exists())

    def test_approval_does_not_transfer_to_another_commit_or_version(self):
        self.assertEqual(self.prepare(extra=self.approval(source_commit="0" * 40)).returncode, 2)
        self.assertEqual(self.prepare(extra=self.approval(version="1.1.2")).returncode, 2)
        self.assertEqual(self.prepare(extra=self.approval(approved=False)).returncode, 2)
        self.assertFalse((self.root / "candidate").exists())

    def test_explicit_matching_record_is_preserved_without_publishing(self):
        result = self.prepare(extra=self.approval())
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads((self.root / "candidate/RELEASE.json").read_text())
        self.assertEqual(record["status"], "approved")
        self.assertEqual(record["approval"]["approved_by"], "SYNTHETIC TEST ONLY")
        self.assertFalse((self.root / "candidate/.git").exists())

    def test_export_inside_source_is_rejected(self):
        result = self.prepare(target="source/new-output")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.source / "new-output").exists())


if __name__ == "__main__":
    unittest.main()
