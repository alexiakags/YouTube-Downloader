from dataclasses import dataclass, field
import queue
import threading
import uuid
from typing import Callable, List, Optional
from core.downloader import MediaDownloader, DownloadError


@dataclass
class QueueItem:
    url: str
    output_dir: str
    media_format: str = "mp3"
    quality: str = "192"
    allow_playlist: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    status: str = "Aguardando"  # "Aguardando" | "Baixando" | "Concluído" | "Erro"
    error_message: str = ""


class DownloadQueueManager:
    def __init__(
        self,
        downloader_factory: Callable[..., MediaDownloader] = MediaDownloader,
        on_queue_updated: Optional[Callable[[List[QueueItem]], None]] = None,
        on_item_progress: Optional[Callable[[str, float, str], None]] = None,
        on_queue_finished: Optional[Callable[[], None]] = None,
    ):
        self.downloader_factory = downloader_factory
        self.on_queue_updated = on_queue_updated
        self.on_item_progress = on_item_progress
        self.on_queue_finished = on_queue_finished

        self._queue: queue.Queue[QueueItem] = queue.Queue()
        self._items: List[QueueItem] = []
        self._lock = threading.Lock()
        self._is_running = False
        self._worker_thread: Optional[threading.Thread] = None

    @property
    def items(self) -> List[QueueItem]:
        with self._lock:
            return list(self._items)

    @property
    def is_running(self) -> bool:
        return self._is_running

    def add_item(
        self,
        url: str,
        output_dir: str,
        media_format: str = "mp3",
        quality: str = "192",
        allow_playlist: bool = False,
    ) -> QueueItem:
        item = QueueItem(
            url=url,
            output_dir=output_dir,
            media_format=media_format,
            quality=quality,
            allow_playlist=allow_playlist,
        )
        with self._lock:
            self._items.append(item)
        self._queue.put(item)
        self._notify_updated()

        if not self._is_running:
            self._start_worker()

        return item

    def remove_item(self, item_id: str) -> bool:
        """Remove um item da lista visual (apenas se não estiver baixando no momento)."""
        with self._lock:
            for idx, item in enumerate(self._items):
                if item.id == item_id and item.status != "Baixando":
                    self._items.pop(idx)
                    self._notify_updated()
                    return True
        return False

    def clear_completed(self) -> None:
        """Limpa itens já concluídos ou com erro da lista."""
        with self._lock:
            self._items = [i for i in self._items if i.status in ("Aguardando", "Baixando")]
        self._notify_updated()

    def _notify_updated(self):
        if self.on_queue_updated:
            self.on_queue_updated(self.items)

    def _start_worker(self):
        self._is_running = True
        self._worker_thread = threading.Thread(target=self._process_loop, daemon=True)
        self._worker_thread.start()

    def _process_loop(self):
        while True:
            try:
                item = self._queue.get_nowait()
            except queue.Empty:
                self._is_running = False
                if self.on_queue_finished:
                    self.on_queue_finished()
                break

            # Se o item foi removido da lista antes de chegar a vez dele, pula
            with self._lock:
                if item not in self._items:
                    self._queue.task_done()
                    continue
                item.status = "Baixando"
            self._notify_updated()

            downloader = self.downloader_factory(
                on_progress=lambda pct, txt, current_id=item.id: (
                    self.on_item_progress(current_id, pct, txt) if self.on_item_progress else None
                )
            )

            try:
                downloader.download(
                    url=item.url,
                    output_dir=item.output_dir,
                    media_format=item.media_format,
                    quality=item.quality,
                    allow_playlist=item.allow_playlist,
                )
                with self._lock:
                    item.status = "Concluído"
            except DownloadError as e:
                with self._lock:
                    item.status = "Erro"
                    item.error_message = str(e)
            finally:
                self._queue.task_done()
                self._notify_updated()