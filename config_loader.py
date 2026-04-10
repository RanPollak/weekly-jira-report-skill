#!/usr/bin/env python3
"""
Shared config loader for weekly Jira report scripts.
"""
import json
import os
from typing import Dict, Any


DEFAULT_CONFIG: Dict[str, Any] = {
    "JIRA_URL": "https://your-company.atlassian.net",
    "EMAIL": "your-email@company.com",
    "API_TOKEN": "YOUR_JIRA_API_TOKEN_HERE",
    "START_ISSUE": "PROJECT-123",
    "TEAM_NAME": "Your Team Name",
    "OUTPUT_DIR": "~/weekly-reports",
    "DRIVE_FOLDER_PATH": "Your Folder/Path",
    "DRIVE_FOLDER_URL": "https://drive.google.com/drive/folders/YOUR-FOLDER-ID",
    "USE_SHARED_DRIVE": True,
}


def _is_placeholder(value: str) -> bool:
    if not isinstance(value, str):
        return False
    markers = (
        "YOUR_",
        "your-",
        "your ",
        "PROJECT-123",
        "Your Team Name",
        "Your Folder/Path",
    )
    return any(marker in value for marker in markers)


def _parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _validate_private_file_permissions(path: str):
    # Skip permission checks on non-POSIX systems.
    if os.name != "posix":
        return
    if _parse_bool(os.getenv("WEEKLY_REPORT_ALLOW_INSECURE_PERMS", "false")):
        return

    mode = os.stat(path).st_mode & 0o777
    # Require owner-only read/write/execute bits (e.g. 600, 640 is rejected).
    if mode & 0o077:
        raise PermissionError(
            f"Insecure permissions on config file: {path} (mode {oct(mode)}). "
            "Run: chmod 600 <config-file> "
            "or set WEEKLY_REPORT_ALLOW_INSECURE_PERMS=true to bypass."
        )


def _load_json_if_exists(path: str) -> Dict[str, Any]:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_config() -> Dict[str, Any]:
    cfg = dict(DEFAULT_CONFIG)

    explicit_path = os.getenv("WEEKLY_REPORT_CONFIG")
    repo_local_path = os.path.join(os.path.dirname(__file__), "weekly_report.local.json")
    home_local_path = os.path.expanduser("~/.weekly-report.local.json")

    file_cfg = {}
    config_source_path = None
    if explicit_path:
        config_source_path = os.path.expanduser(explicit_path)
        _validate_private_file_permissions(config_source_path)
        file_cfg = _load_json_if_exists(config_source_path)
    elif os.path.exists(repo_local_path):
        config_source_path = repo_local_path
        _validate_private_file_permissions(config_source_path)
        file_cfg = _load_json_if_exists(config_source_path)
    elif os.path.exists(home_local_path):
        config_source_path = home_local_path
        _validate_private_file_permissions(config_source_path)
        file_cfg = _load_json_if_exists(config_source_path)

    cfg.update(file_cfg)

    # Environment variable overrides
    env_keys = [
        "JIRA_URL",
        "EMAIL",
        "API_TOKEN",
        "START_ISSUE",
        "TEAM_NAME",
        "OUTPUT_DIR",
        "DRIVE_FOLDER_PATH",
        "DRIVE_FOLDER_URL",
        "USE_SHARED_DRIVE",
    ]
    for key in env_keys:
        if key in os.environ:
            cfg[key] = os.environ[key]

    if isinstance(cfg.get("USE_SHARED_DRIVE"), str):
        cfg["USE_SHARED_DRIVE"] = _parse_bool(cfg["USE_SHARED_DRIVE"])

    cfg["OUTPUT_DIR"] = os.path.expanduser(str(cfg.get("OUTPUT_DIR", "~/weekly-reports")))
    cfg["TEAM_NAME_SLUG"] = str(cfg.get("TEAM_NAME", "Team")).replace(" ", "_")
    cfg["CONFIG_SOURCE_PATH"] = config_source_path or "defaults/env-only"
    return cfg


def validate_required(cfg: Dict[str, Any], required_keys):
    missing = []
    for key in required_keys:
        value = cfg.get(key)
        if value is None:
            missing.append(key)
            continue
        if isinstance(value, str):
            if not value.strip() or _is_placeholder(value):
                missing.append(key)
    if missing:
        raise ValueError(
            "Missing/placeholder config values: "
            + ", ".join(missing)
            + ". Configure weekly_report.local.json or set environment variables."
        )


def mask_sensitive_text(text: Any, cfg: Dict[str, Any]) -> str:
    masked = str(text)
    for key in ("API_TOKEN", "EMAIL"):
        value = str(cfg.get(key, "")).strip()
        if value and not _is_placeholder(value):
            masked = masked.replace(value, "[REDACTED]")
    return masked
