"""Versionamento dinâmico do ACC Manager.

Responsável por:
- detectar a branch atual do git
- identificar arquivos modificados ou não rastreados
- calcular a próxima versão com base na branch e no tipo de mudança
- gerar um manifesto de versionamento que a interface pode usar na aba de configurações
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

APP_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = APP_ROOT / "version.json"
DEFAULT_VERSION = "4.0.0"


class AppVersionManager:
    """Gerencia o versionamento do app em tempo real."""

    def __init__(self, repo_root: str | Path | None = None, version_file: str | Path | None = None):
        self.repo_root = Path(repo_root) if repo_root else APP_ROOT
        self.version_file = Path(version_file) if version_file else VERSION_FILE

    @staticmethod
    def _run_git(args: List[str], cwd: Path) -> str:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return ""
            return (result.stdout or "").strip()
        except Exception:
            return ""

    def is_git_repo(self) -> bool:
        return bool(self._run_git(["rev-parse", "--show-toplevel"], self.repo_root))

    def get_branch(self) -> str:
        branch = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"], self.repo_root)
        return branch or "unknown"

    def get_commit_hash(self) -> str:
        return self._run_git(["rev-parse", "--short", "HEAD"], self.repo_root) or "unknown"

    def get_current_version(self) -> str:
        if not self.version_file.exists():
            return DEFAULT_VERSION
        try:
            data = json.loads(self.version_file.read_text(encoding="utf-8"))
            version = data.get("current_version") or data.get("version")
            if version:
                return str(version)
        except Exception:
            pass
        return DEFAULT_VERSION

    def get_changed_files(self) -> List[str]:
        if not self.is_git_repo():
            return []

        status = self._run_git(["status", "--porcelain"], self.repo_root)
        if not status:
            return []

        files: List[str] = []
        for line in status.splitlines():
            if len(line) < 4:
                continue
            files.append(line[3:].strip())
        return files

    def get_untracked_files(self) -> List[str]:
        if not self.is_git_repo():
            return []
        data = self._run_git(["ls-files", "--others", "--exclude-standard"], self.repo_root)
        return [line.strip() for line in data.splitlines() if line.strip()]

    def _normalize_branch(self, branch: str) -> str:
        return branch.lower().replace("\\", "/").strip("/")

    def _bump_version(self, current_version: str, branch: str, changed_files: List[str], new_files: List[str]) -> str:
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$", current_version)
        if not match:
            return DEFAULT_VERSION

        major, minor, patch = (int(part) for part in match.groups())
        branch_name = self._normalize_branch(branch)

        if branch_name in {"main", "master"}:
            if changed_files or new_files:
                patch += 1
            return f"{major}.{minor}.{patch}"

        if branch_name.startswith("hotfix/"):
            patch += 1
            return f"{major}.{minor}.{patch}-hotfix"

        if branch_name.startswith("release/"):
            minor += 1
            patch = 0
            return f"{major}.{minor}.{patch}-rc"

        if branch_name.startswith("feature/"):
            minor += 1
            patch = 0
            return f"{major}.{minor}.{patch}-beta"

        if changed_files or new_files:
            patch += 1
        return f"{major}.{minor}.{patch}-dev"

    def _detect_channel(self, branch: str) -> str:
        branch_name = self._normalize_branch(branch)
        if branch_name in {"main", "master"}:
            return "stable"
        if branch_name.startswith("hotfix/"):
            return "hotfix"
        if branch_name.startswith("release/"):
            return "release"
        if branch_name.startswith("feature/"):
            return "feature"
        return "development"

    def validate_update(self) -> Dict[str, Any]:
        """Valida a situação atual para decidir se há atualização pendente."""
        branch = self.get_branch()
        changed_files = self.get_changed_files()
        new_files = self.get_untracked_files()
        current_version = self.get_current_version()
        next_version = self._bump_version(current_version, branch, changed_files, new_files)

        relevant_changes = [
            item for item in changed_files + new_files
            if item.startswith("core/") or item.startswith("ui/") or item in {"main.py", "config.py"}
        ]

        manifest = {
            "app_name": "ACC Manager",
            "branch": branch,
            "channel": self._detect_channel(branch),
            "current_version": current_version,
            "next_version": next_version,
            "commit": self.get_commit_hash(),
            "changed_files": changed_files,
            "new_files": new_files,
            "relevant_changes": relevant_changes,
            "needs_update": bool(relevant_changes),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.write_manifest(manifest)
        return manifest

    def write_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        self.version_file.parent.mkdir(parents=True, exist_ok=True)
        self.version_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest


if __name__ == "__main__":
    manager = AppVersionManager()
    print(json.dumps(manager.validate_update(), ensure_ascii=False, indent=2))
