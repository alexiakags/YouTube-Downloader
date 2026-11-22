# 🎵 YT Downloader

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-F48FB1?style=for-the-badge)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Integrated-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)

Uma aplicação desktop multiplataforma com estética **retrô/pixel** para download e conversão de vídeos e playlists do YouTube em **MP3**, **WAV** e **MP4**, construída com arquitetura modular em Python, **FFmpeg integrado** e suíte de testes automatizados.

---

## ⬇️ Download Direto (Usuários Finais — Windows)

Não é necessário instalar Python, bibliotecas ou configurar o FFmpeg manualmente. O executável portátil já inclui todas as dependências embutidas:

1. Acesse a página de [**Releases do Repositório**](../../releases/latest).
2. Na seção **Assets**, baixe o arquivo **`YTDownloader.exe`**.
3. Dê um duplo clique para executar.

---

## ✨ Funcionalidades

* **Múltiplos Formatos e Qualidades:**
  * **Áudio MP3:** Conversão com seleção de bitrate (`320 kbps`, `192 kbps`, `128 kbps`).
  * **Áudio WAV:** Extração descomprimida sem perdas (`PCM`).
  * **Vídeo MP4:** Download e mesclagem automática de faixas de vídeo e áudio (`1080p`, `720p`, `480p` ou qualidade máxima).
* **Suporte a Playlists:** Opção para baixar vídeos individuais ou playlists completas.
* **Interface Não-Bloqueante:** Execução assíncrona via *multithreading*, mantendo a interface responsiva com barra de progresso em tempo real, velocidade de download e tempo estimado (ETA).
* **FFmpeg Portátil:** Resolução automática de binários tanto em ambiente empacotado (`sys._MEIPASS`) quanto no `PATH` do sistema operacional.

---

## 🎨 Estética & Temas

A interface segue uma linha retrô inspirada em terminais clássicos e consoles antigos (bordas retas, tipografia monoespaçada `Consolas` e alternância em tempo real persistida em configuração):

* **Modo Claro (Padrão):** Fundo em rosa bebê (`#FDF2F5`) e rosa pastel (`#F8E1E7`), bordas e textos em marrom café (`#6D4C41` / `#3E2723`) e destaques em rosa chiclete pastel (`#F48FB1`).
* **Modo Escuro:** Fundo em vinho/rosa escuro profundo (`#170B11` / `#26121C`), textos em branco rosado (`#FCE4EC`), destaques em rosa magenta (`#C71A54`) e barra de progresso em dourado retrô (`#F6BD60`).

---

## 🏗️ Arquitetura do Projeto

O projeto foi estruturado seguindo o princípio de **Separação de Responsabilidades (SoC)**, isolando a interface gráfica da lógica de extração e conversão de mídia — o que viabiliza testes unitários rápidos e sem acoplamento visual:

```text
ytdownloader/
├── .gitignore
├── pytest.ini              # Configuração de paths do Pytest
├── requirements.txt        # Dependências fixadas do projeto
├── README.md
├── assets/                 # Ícones e recursos visuais da interface
│   ├── icon.ico
│   └── mascote.png
├── bin/                    # Binários locais do FFmpeg (ignorados no Git)
├── src/
│   ├── main.py             # Ponto de entrada (Entrypoint) da aplicação
│   ├── core/
│   │   └── downloader.py   # Motor de download (yt-dlp + FFmpeg) desacoplado da UI
│   ├── ui/
│   │   └── app_window.py   # Interface gráfica CustomTkinter e controle de threads
│   └── utils/
│       ├── config.py       # Persistência de configurações no AppData / ~/.config
│       └── paths.py        # Resolução de caminhos (Dev, PyInstaller e PATH do SO)
└── tests/                  # Suíte de testes unitários automatizados
    ├── __init__.py
    ├── test_config.py
    ├── test_downloader.py
    └── test_paths.py
```

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.11+**
* **CustomTkinter & Pillow** (Interface gráfica moderna/customizada e manipulação de imagens)
* **yt-dlp** (Extração de streams e metadados)
* **FFmpeg** (Conversão de áudio e mesclagem de vídeo/áudio)
* **Pytest & unittest.mock** (Testes unitários automatizados)
* **PyInstaller** (Empacotamento em executável portátil)

---

## 💻 Como Rodar em Ambiente de Desenvolvimento

### Pré-requisitos

* **Python 3.11** ou superior.
* **FFmpeg:**
  * **Windows:** Baixe o `ffmpeg.exe` e coloque-o dentro da pasta `bin/` na raiz do projeto.
  * **Linux / macOS:** Instale via gerenciador de pacotes (`sudo apt install ffmpeg` ou `brew install ffmpeg`).

### Passo a passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/alexiakags/YouTube-Downloader.git
   cd ytdownloader
   ```

2. **Crie e ative um ambiente virtual (`.venv`):**
   * **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   * **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação:**
   ```bash
   python src/main.py
   ```

---

## 🧪 Executando os Testes

O projeto conta com testes unitários automatizados utilizando `pytest` e `unittest.mock` para validar a camada de negócios (`core`), persistência de configurações (`config`) e resolução de caminhos (`paths`):

```bash
pytest -v
```

---

## 📦 Gerando o Executável Portátil (Build)

Para empacotar a aplicação em um único arquivo `.exe` no Windows com o FFmpeg e os assets embutidos via **PyInstaller**:

```powershell
pyinstaller --noconfirm --onefile --windowed --name "YTDownloader" --icon "assets/icon.ico" --paths src --collect-all customtkinter --exclude-module unittest --exclude-module pydoc --add-binary "bin/ffmpeg.exe;." --add-data "assets;assets" src/main.py
```

O executável final será gerado em `dist/YTDownloader.exe`.

---

## ⚠️ Aviso Legal

Este projeto foi desenvolvido exclusivamente para fins educacionais e de portfólio. Respeite os Termos de Serviço da plataforma e os direitos autorais dos criadores de conteúdo ao utilizar a ferramenta.
