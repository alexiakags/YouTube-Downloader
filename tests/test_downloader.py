from unittest.mock import MagicMock
import pytest
from core.downloader import MediaDownloader, DownloadError


def test_download_raises_error_when_ffmpeg_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("core.downloader.get_ffmpeg_dir", lambda: None)
    downloader = MediaDownloader()

    with pytest.raises(DownloadError, match="FFmpeg não encontrado"):
        downloader.download("https://youtube.com/watch?v=123", str(tmp_path))


def test_download_raises_error_when_output_dir_invalid(monkeypatch):
    monkeypatch.setattr("core.downloader.get_ffmpeg_dir", lambda: "/fake/bin")
    downloader = MediaDownloader()

    with pytest.raises(DownloadError, match="pasta de destino"):
        downloader.download("https://youtube.com/watch?v=123", "/pasta/que/nao/existe")


def test_download_mp3_options(tmp_path, monkeypatch):
    monkeypatch.setattr("core.downloader.get_ffmpeg_dir", lambda: "/fake/bin")

    captured_opts = {}
    mock_ydl_instance = MagicMock()

    def fake_youtube_dl(opts):
        captured_opts.update(opts)
        context = MagicMock()
        context.__enter__.return_value = mock_ydl_instance
        return context

    monkeypatch.setattr("yt_dlp.YoutubeDL", fake_youtube_dl)

    downloader = MediaDownloader()
    downloader.download(
        url="https://youtube.com/watch?v=abc",
        output_dir=str(tmp_path),
        media_format="mp3",
        quality="320",
        allow_playlist=False,
    )

    mock_ydl_instance.download.assert_called_once_with(["https://youtube.com/watch?v=abc"])
    assert captured_opts["noplaylist"] is True
    assert captured_opts["postprocessors"][0]["preferredcodec"] == "mp3"
    assert captured_opts["postprocessors"][0]["preferredquality"] == "320"


def test_download_wav_and_mp4_options(tmp_path, monkeypatch):
    monkeypatch.setattr("core.downloader.get_ffmpeg_dir", lambda: "/fake/bin")

    captured_opts = {}

    def fake_youtube_dl(opts):
        captured_opts.clear()
        captured_opts.update(opts)
        return MagicMock()

    monkeypatch.setattr("yt_dlp.YoutubeDL", fake_youtube_dl)
    downloader = MediaDownloader()

    # Testa WAV
    downloader.download("https://youtube.com/watch?v=1", str(tmp_path), media_format="wav")
    assert captured_opts["postprocessors"][0]["preferredcodec"] == "wav"
    assert "preferredquality" not in captured_opts["postprocessors"][0]

    # Testa MP4 720p com Playlist habilitada
    downloader.download(
        "https://youtube.com/playlist?list=1",
        str(tmp_path),
        media_format="mp4",
        quality="720",
        allow_playlist=True,
    )
    assert captured_opts["noplaylist"] is False
    assert "height<=720" in captured_opts["format"]
    assert captured_opts["merge_output_format"] == "mp4"