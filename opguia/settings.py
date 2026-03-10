"""Persistent settings — saved connections, favorites, preferences.

Settings are stored as JSON in an OS-appropriate config directory:
  macOS:   ~/Library/Application Support/opguia/settings.json
  Linux:   ~/.config/opguia/settings.json
  Windows: %APPDATA%/opguia/settings.json
"""

import json
import sys
from pathlib import Path

_APP_NAME = "opguia"


def _config_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / _APP_NAME
    elif sys.platform == "win32":
        base = Path.home() / "AppData" / "Roaming"
        return base / _APP_NAME
    else:
        return Path.home() / ".config" / _APP_NAME


_DEFAULTS = {
    "allow_writes": False,
    "connections": [],   # list of saved endpoint URL strings
    "favorites": [],     # list of {"name": str, "node_id": str}
}


class Settings:
    """Read/write persistent JSON settings."""

    def __init__(self):
        self._path = _config_dir() / "settings.json"
        self._data: dict = {}
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text())
            except (json.JSONDecodeError, OSError):
                self._data = {}
        for key, default in _DEFAULTS.items():
            self._data.setdefault(key, default if not isinstance(default, list) else list(default))

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2))

    # ── Generic access ──

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value
        self._save()

    # ── Connections ──

    @property
    def connections(self) -> list[str]:
        return self._data.get("connections", [])

    def add_connection(self, url: str):
        conns = self._data.setdefault("connections", [])
        if url not in conns:
            conns.append(url)
            self._save()

    def remove_connection(self, url: str):
        conns = self._data.get("connections", [])
        if url in conns:
            conns.remove(url)
            self._save()

    # ── Favorites (saved variable bookmarks) ──

    @property
    def favorites(self) -> list[dict]:
        return self._data.get("favorites", [])

    def add_favorite(self, name: str, node_id: str):
        favs = self._data.setdefault("favorites", [])
        if not any(f["node_id"] == node_id for f in favs):
            favs.append({"name": name, "node_id": node_id})
            self._save()

    def remove_favorite(self, node_id: str):
        favs = self._data.get("favorites", [])
        self._data["favorites"] = [f for f in favs if f["node_id"] != node_id]
        self._save()

    def is_favorite(self, node_id: str) -> bool:
        return any(f["node_id"] == node_id for f in self.favorites)

    # ── Preferences ──

    @property
    def allow_writes(self) -> bool:
        return self._data.get("allow_writes", False)

    @allow_writes.setter
    def allow_writes(self, value: bool):
        self.set("allow_writes", value)
