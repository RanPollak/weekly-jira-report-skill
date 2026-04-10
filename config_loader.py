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
    if explicit_path:
        file_cfg = _load_json_if_exists(os.path.expanduser(explicit_path))
    elif os.path.exists(repo_local_path):
        file_cfg = _load_json_if_exists(repo_local_path)
    elif os.path.exists(home_local_path):
        file_cfg = _load_json_if_exists(home_local_path)

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
