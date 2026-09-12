import json
from pathlib import Path

from core.version_manager import AppVersionManager


def make_manager(tmp_path: Path, branch: str = "feature/new-tab") -> AppVersionManager:
    version_file = tmp_path / "version.json"
    version_file.write_text(json.dumps({"current_version": "4.0.0"}), encoding="utf-8")
    manager = AppVersionManager(repo_root=tmp_path, version_file=version_file)
    manager.get_branch = lambda: branch
    return manager


def test_feature_branch_bumps_minor_to_beta(tmp_path):
    manager = make_manager(tmp_path)

    assert manager._bump_version("4.0.0", "feature/new-tab", ["ui/settings_dialog.py"], []) == "4.1.0-beta"


def test_hotfix_branch_bumps_patch_to_hotfix(tmp_path):
    manager = make_manager(tmp_path)

    assert manager._bump_version("4.0.0", "hotfix/parser", ["core/motec_parser.py"], []) == "4.0.1-hotfix"


def test_main_branch_without_relevant_changes_keeps_version(tmp_path):
    manager = make_manager(tmp_path)

    assert manager._bump_version("4.0.0", "main", [], []) == "4.0.0"


def test_validate_update_reports_tracked_and_new_relevant_files(tmp_path, monkeypatch):
    manager = make_manager(tmp_path)
    monkeypatch.setattr(manager, "is_git_repo", lambda: True)
    monkeypatch.setattr(manager, "get_changed_files", lambda: ["ui/settings_dialog.py", "README.md"])
    monkeypatch.setattr(manager, "get_untracked_files", lambda: ["core/version_manager.py"])
    monkeypatch.setattr(manager, "get_commit_hash", lambda: "abc1234")

    manifest = manager.validate_update()

    assert manifest["branch"] == "feature/new-tab"
    assert manifest["next_version"] == "4.1.0-beta"
    assert manifest["needs_update"] is True
    assert manifest["relevant_changes"] == ["ui/settings_dialog.py", "core/version_manager.py"]
