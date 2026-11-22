import os
from typing import Callable, Optional
import yt_dlp
from utils.paths import get_ffmpeg_dir

class DownloadError(Exception):
    """Exceção customizada para erros amigáveis ao usuário."""
    pass

class MediaDownloader:
    def __init__(
        self,
        on_progress: Optional[Callable[[float, str], None]] = None,
        on_status: Optional[Callable[[str], None]] = None,
    ):
        self.on_progress = on_progress
        self.on_status = on_status
        self.ffmpeg_dir = get_ffmpeg_dir()

    def _progress_hook(self, d: dict) -> None:
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            percent = (downloaded / total * 100) if total > 0 else 0.0
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()

            if self.on_progress:
                self.on_progress(percent, f"{percent:.1f}% • {speed} • ETA {eta}")

        elif status == "finished":
            if self.on_progress:
                self.on_progress(100.0, "Convertendo mídia com FFmpeg...")
            if self.on_status:
                self.on_status("Processando áudio/vídeo...")

    def download(
        self,
        url: str,
        output_dir: str,
        media_format: str = "mp3",
        quality: str = "192",
        allow_playlist: bool = False,
    ) -> None:
        if not self.ffmpeg_dir:
            raise DownloadError(
                "FFmpeg não encontrado! Coloque o ffmpeg.exe na pasta 'bin/' ou instale-o no sistema."
            )

        if not os.path.isdir(output_dir):
            raise DownloadError("A pasta de destino selecionada não existe.")

        ydl_opts = {
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "noplaylist": not allow_playlist,
            "ffmpeg_location": self.ffmpeg_dir,
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
        }

        if media_format == "mp3":
            # quality recebe "128", "192" ou "320"
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": quality,
                }],
            })
        elif media_format == "wav":
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                }],
            })
        elif media_format == "mp4":
            # quality recebe "1080", "720", "480" ou "best"
            if quality == "best":
                fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            else:
                fmt = f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best"

            ydl_opts.update({
                "format": fmt,
                "merge_output_format": "mp4",
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except yt_dlp.utils.DownloadError as e:
            raise DownloadError(f"Falha ao baixar o vídeo. Verifique o link ou sua conexão.\nDetalhe: {e}")
        except Exception as e:
            raise DownloadError(f"Erro inesperado: {e}")