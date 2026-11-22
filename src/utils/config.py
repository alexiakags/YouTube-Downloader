import json
from pathlib import Path
from utils.paths import get_app_data_dir

class ConfigManager:
    def __init__(self):
        self.config_path = get_app_data_dir() / "config.json"
        self.data = self._load()

    def _load(self) -> dict:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def save(self) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    @property
    def download_dir(self) -> str:
        default_dir = str(Path.home() / "Downloads")
        return self.data.get("pasta_destino", default_dir)

    @download_dir.setter
    def download_dir(self, path: str) -> None:
        self.data["pasta_destino"] = path
        self.save()

    @property
    def theme(self) -> str:
        return self.data.get("tema", "light")

    @theme.setter
    def theme(self, mode: str) -> None:
        self.data["tema"] = mode
        self.save()