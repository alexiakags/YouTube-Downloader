import os
import sys
import shutil
from pathlib import Path

APP_NAME = "YTDownloader"

def get_app_data_dir() -> Path:
    """Retorna o diretório persistente e gravável para configurações e logs."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".config"
    
    app_dir = base / APP_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

def get_ffmpeg_dir() -> str | None:
    exe_name = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"

    # 1. Ambiente PyInstaller (--onefile ou --onedir)
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundled_ffmpeg = Path(sys._MEIPASS) / exe_name
        if bundled_ffmpeg.exists():
            return str(sys._MEIPASS)

    # 2. Pasta local bin/ na raiz do projeto
    project_bin = Path(__file__).resolve().parents[2] / "bin"
    if (project_bin / exe_name).exists():
        return str(project_bin)

    # 3. PATH do sistema (Linux/macOS/Windows)
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return str(Path(system_ffmpeg).parent)

def get_asset_path(filename: str) -> Path:
    """Localiza arquivos da pasta assets/ tanto em dev quanto no PyInstaller."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "assets" / filename
    return Path(__file__).resolve().parents[2] / "assets" / filename

    return None