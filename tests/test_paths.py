import sys
from pathlib import Path
from utils.paths import get_ffmpeg_dir, get_asset_path


def test_get_ffmpeg_dir_from_pyinstaller_bundle(tmp_path, monkeypatch):
    exe_name = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
    fake_ffmpeg = tmp_path / exe_name
    fake_ffmpeg.write_text("binary", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    assert get_ffmpeg_dir() == str(tmp_path)


def test_get_ffmpeg_dir_fallback_to_system_path(monkeypatch):
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    # Simula pasta bin local inexistente e FFmpeg instalado no PATH do sistema
    monkeypatch.setattr("utils.paths.Path.exists", lambda self: False)
    monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/ffmpeg")

    assert get_ffmpeg_dir() == str(Path("/usr/bin"))


def test_get_asset_path_dev_mode(monkeypatch):
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    path = get_asset_path("mascote.png")
    assert path.name == "mascote.png"
    assert "assets" in path.parts