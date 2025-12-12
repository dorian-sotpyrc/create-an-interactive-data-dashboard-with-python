from __future__ import annotations

import os
from typing import Any, Dict

import yaml


class ConfigError(Exception):
    """Raised when the dashboard configuration is invalid."""


def load_dashboard_config(path: str) -> Dict[str, Any]:
    """Load and minimally validate the dashboard YAML config.

    Parameters
    ----------
    path: str
        Path to the YAML config file.
    """
    if not os.path.exists(path):
        raise ConfigError(f"Dashboard config not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    # Minimal validation
    if "data_source" not in raw:
        raise ConfigError("Config must define 'data_source'.")

    if "metrics" not in raw or not isinstance(raw["metrics"], list):
        raise ConfigError("Config must define a list of 'metrics'.")

    if "charts" not in raw or not isinstance(raw["charts"], list):
        raise ConfigError("Config must define a list of 'charts'.")

    # Provide sensible defaults
    raw.setdefault("filters", [])

    return raw
