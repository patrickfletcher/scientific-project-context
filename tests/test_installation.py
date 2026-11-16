from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scientific_project_context import installation  # noqa: E402


class FakeDistribution:
    def __init__(self, files: dict[str, str]) -> None:
        self.files = files

    def read_text(self, name: str) -> str | None:
        return self.files.get(name)


class InstallationTests(unittest.TestCase):
    """Agents could not find or upgrade `spctx`; trial instruction files carried user names."""

    def describe(self, files: dict[str, str], *, layout: str = "home") -> dict[str, object]:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home" / "someone"
            project = home / "work" / "study"
            env = project / ".venv"
            (env / "bin").mkdir(parents=True)
            executable = env / "bin" / "python"
            if layout == "outside":
                executable = Path(tmp) / "opt" / "env" / "bin" / "python"
            with mock.patch.object(installation.metadata, "distribution", return_value=FakeDistribution(files)), \
                mock.patch.object(installation.sys, "executable", str(executable)), \
                mock.patch.object(installation.sys, "prefix", str(executable.parent.parent)), \
                mock.patch.object(installation.Path, "home", return_value=home):
                described = installation.describe_installation(project)
        assert described is not None
        return described

    def test_git_install_by_pip_gives_a_pip_upgrade_from_the_same_repository(self) -> None:
        described = self.describe(
            {
                "INSTALLER": "pip\n",
                "direct_url.json": json.dumps(
                    {"url": "https://token@github.com/org/spctx.git", "vcs_info": {"vcs": "git", "commit_id": "abc"}}
                ),
            }
        )
        self.assertEqual("git", described["source_kind"])
        self.assertEqual(
            ".venv/bin/python -m pip install --upgrade git+https://github.com/org/spctx.git",
            described["upgrade_command"],
        )
        self.assertNotIn("token", str(described["context_tools_line"]))
        self.assertNotIn("someone", str(described["context_tools_line"]))
        self.assertFalse(described["machine_specific"])

    def test_local_checkout_by_uv_reinstalls_from_its_relative_path(self) -> None:
        with tempfile.TemporaryDirectory():
            described = self.describe(
                {"INSTALLER": "uv", "direct_url.json": json.dumps({"url": "file:///nowhere/spctx", "dir_info": {}})}
            )
        self.assertEqual("local_directory", described["source_kind"])
        self.assertIn("--reinstall-package scientific-project-context", str(described["upgrade_command"]))
        self.assertTrue(str(described["upgrade_command"]).startswith("uv pip install --python .venv/bin/python"))
        # A source outside the project and home is specific to this machine.
        self.assertTrue(described["machine_specific"])

    def test_unrecorded_source_never_suggests_installing_by_name(self) -> None:
        described = self.describe({"INSTALLER": "pip"})
        self.assertIsNone(described["upgrade_command"])
        self.assertIn("never install it by name", str(described["context_tools_line"]))

    def test_an_environment_outside_project_and_home_is_flagged(self) -> None:
        described = self.describe({"INSTALLER": "pip"}, layout="outside")
        self.assertTrue(described["machine_specific"])

    def test_running_from_source_reports_nothing(self) -> None:
        error = installation.metadata.PackageNotFoundError
        with mock.patch.object(installation.metadata, "distribution", side_effect=error):
            self.assertIsNone(installation.describe_installation(Path(".")))


if __name__ == "__main__":
    unittest.main()
