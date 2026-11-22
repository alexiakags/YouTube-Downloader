from utils.config import ConfigManager


def test_config_default_values(tmp_path, monkeypatch):
    # Redireciona o diretório de dados para uma pasta temporária do teste
    monkeypatch.setattr("utils.config.get_app_data_dir", lambda: tmp_path)

    cfg = ConfigManager()

    assert cfg.theme == "light"
    assert "Downloads" in cfg.download_dir


def test_config_persistence(tmp_path, monkeypatch):
    monkeypatch.setattr("utils.config.get_app_data_dir", lambda: tmp_path)

    cfg = ConfigManager()
    cfg.theme = "dark"
    cfg.download_dir = str(tmp_path / "Musicas")

    # Cria uma nova instância simulando reabrir o programa
    reloaded_cfg = ConfigManager()
    assert reloaded_cfg.theme == "dark"
    assert reloaded_cfg.download_dir == str(tmp_path / "Musicas")


def test_config_handles_corrupted_json(tmp_path, monkeypatch):
    monkeypatch.setattr("utils.config.get_app_data_dir", lambda: tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_text("{json_invalido_quebrado", encoding="utf-8")

    # Não deve quebrar o app; deve voltar aos padrões
    cfg = ConfigManager()
    assert cfg.theme == "light"