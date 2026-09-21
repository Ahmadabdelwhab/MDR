"""Load and validate runtime settings from JSON."""

from __future__ import annotations

import json
import os
import sys

DEFAULT_CONFIG = {
    "fps": 24,
    "idle_min": 1.2,
    "idle_max": 2.5,
    "image": None,
}


def load_config(path: str | None = None) -> dict:
    if path:
        config_path = path
    else:
        bundle_dir = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
        config_path = os.path.join(bundle_dir, "config.json")
    settings = dict(DEFAULT_CONFIG)

    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            values = json.load(config_file)
    except FileNotFoundError:
        return settings
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {config_path}: {exc}") from exc

    if not isinstance(values, dict):
        raise TypeError("Configuration must contain a JSON object")
    settings.update(values)

    if not isinstance(settings["fps"], int) or settings["fps"] <= 0:
        raise ValueError("config.fps must be a positive integer")
    if not isinstance(settings["idle_min"], (int, float)) or settings["idle_min"] < 0:
        raise ValueError("config.idle_min must be a non-negative number")
    if not isinstance(settings["idle_max"], (int, float)) or settings["idle_max"] < settings["idle_min"]:
        raise ValueError("config.idle_max must be >= config.idle_min")
    if settings["image"] is not None and not isinstance(settings["image"], str):
        raise ValueError("config.image must be a path string or null")

    return settings
