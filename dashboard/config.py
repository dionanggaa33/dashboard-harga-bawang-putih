"""Konfigurasi dashboard dan kontrol visibilitas halaman."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "dashboard_config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "default_year": 2025,
    "default_wilayah": [],
    "visibility": {
        "kpi": True,
        "peta": True,
        "tren": True,
        "perbandingan": True,
        "kmeans": True,
        "insight": True,
        "jisdor": True,
    },
}


def load_config() -> dict[str, Any]:
    """Membaca konfigurasi JSON dengan fallback konfigurasi bawaan."""

    try:
        with CONFIG_PATH.open(encoding="utf-8") as file:
            loaded = json.load(file)
    except (OSError, json.JSONDecodeError):
        loaded = {}
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    config.update({key: value for key, value in loaded.items() if key != "visibility"})
    config["visibility"].update(loaded.get("visibility", {}))
    return config


def save_config(config: dict[str, Any]) -> None:
    """Menyimpan konfigurasi dashboard ke file JSON."""

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=2)
