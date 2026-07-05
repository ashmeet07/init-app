import json
import os
from pathlib import Path
from typing import Any, Dict


VALID_PATH_BEHAVIORS = {"documents", "current", "custom"}


class PathConfig:
    """Small user config for default project output behavior."""

    @staticmethod
    def config_path() -> Path:
        override = os.environ.get("INIT_APP_CONFIG_PATH")
        if override:
            return Path(override).expanduser().resolve()
        return (Path.home() / ".init-app" / "config.json").resolve()

    @classmethod
    def load(cls) -> Dict[str, Any]:
        path = cls.config_path()
        if not path.exists():
            return {}

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

        if not isinstance(data, dict):
            return {}

        behavior = data.get("path_behavior")
        if behavior and behavior not in VALID_PATH_BEHAVIORS:
            data.pop("path_behavior", None)

        return data

    @classmethod
    def save(cls, data: Dict[str, Any]) -> Path:
        clean: Dict[str, Any] = {}

        behavior = data.get("path_behavior")
        if behavior in VALID_PATH_BEHAVIORS:
            clean["path_behavior"] = behavior

        output_dir = data.get("output_dir")
        if output_dir:
            clean["output_dir"] = str(Path(str(output_dir)).expanduser().resolve())

        path = cls.config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(clean, indent=2) + "\n", encoding="utf-8")
        return path

    @classmethod
    def reset(cls) -> Path:
        path = cls.config_path()
        if path.exists():
            path.unlink()
        return path

    @classmethod
    def describe(cls) -> str:
        data = cls.load()
        behavior = data.get("path_behavior", "documents")
        output_dir = data.get("output_dir", "")
        lines = [
            f"config: {cls.config_path()}",
            f"path_behavior: {behavior}",
        ]
        if output_dir:
            lines.append(f"output_dir: {output_dir}")
        return "\n".join(lines)
