import threading
import time
from unittest.mock import MagicMock
from core.downloader import DownloadError
from core.queue_manager import DownloadQueueManager


def _wait_until_idle(manager: DownloadQueueManager, timeout: float = 2.0):
    deadline = time.time() + timeout
    while manager.is_running and time.time() < deadline:
        time.sleep(0.01)
    assert not manager.is_running, "A fila não finalizou dentro do tempo esperado."


def test_queue_processes_multiple_items_sequentially(tmp_path):
    processed_urls = []
    finished_event = threading.Event()

    def fake_factory(**kwargs):
        mock_dl = MagicMock()

        def fake_download(url, output_dir, media_format, quality, allow_playlist):
            processed_urls.append((url, media_format, quality))

        mock_dl.download.side_effect = fake_download
        return mock_dl

    manager = DownloadQueueManager(
        downloader_factory=fake_factory,
        on_queue_finished=finished_event.set,
    )

    manager.add_item("https://youtube.com/watch?v=1", str(tmp_path), "mp3", "320")
    manager.add_item("https://youtube.com/watch?v=2", str(tmp_path), "wav", "best")
    manager.add_item("https://youtube.com/watch?v=3", str(tmp_path), "mp4", "1080")

    assert finished_event.wait(timeout=2.0)
    _wait_until_idle(manager)

    assert processed_urls == [
        ("https://youtube.com/watch?v=1", "mp3", "320"),
        ("https://youtube.com/watch?v=2", "wav", "best"),
        ("https://youtube.com/watch?v=3", "mp4", "1080"),
    ]
    assert all(item.status == "Concluído" for item in manager.items)


def test_queue_continues_after_item_error(tmp_path):
    finished_event = threading.Event()

    def fake_factory(**kwargs):
        mock_dl = MagicMock()

        def fake_download(url, **kw):
            if "fail" in url:
                raise DownloadError("Vídeo indisponível")

        mock_dl.download.side_effect = fake_download
        return mock_dl

    manager = DownloadQueueManager(
        downloader_factory=fake_factory,
        on_queue_finished=finished_event.set,
    )

    item_err = manager.add_item("https://youtube.com/watch?v=fail", str(tmp_path))
    item_ok = manager.add_item("https://youtube.com/watch?v=ok", str(tmp_path))

    assert finished_event.wait(timeout=2.0)
    _wait_until_idle(manager)

    assert item_err.status == "Erro"
    assert "Vídeo indisponível" in item_err.error_message
    assert item_ok.status == "Concluído"


def test_remove_pending_item_and_clear_completed(tmp_path):
    block_first = threading.Event()
    first_started = threading.Event()
    finished_event = threading.Event()

    def fake_factory(**kwargs):
        mock_dl = MagicMock()

        def fake_download(url, **kw):
            if "first" in url:
                first_started.set()
                block_first.wait(timeout=2.0)

        mock_dl.download.side_effect = fake_download
        return mock_dl

    manager = DownloadQueueManager(
        downloader_factory=fake_factory,
        on_queue_finished=finished_event.set,
    )

    first = manager.add_item("https://youtube.com/watch?v=first", str(tmp_path))
    assert first_started.wait(timeout=2.0)

    second = manager.add_item("https://youtube.com/watch?v=second", str(tmp_path))
    third = manager.add_item("https://youtube.com/watch?v=third", str(tmp_path))

    # Não deve permitir remover o item que está baixando agora
    assert manager.remove_item(first.id) is False
    # Deve permitir remover o segundo enquanto ainda está aguardando
    assert manager.remove_item(second.id) is True

    block_first.set()
    assert finished_event.wait(timeout=2.0)
    _wait_until_idle(manager)

    assert [i.id for i in manager.items] == [first.id, third.id]

    manager.clear_completed()
    assert manager.items == []