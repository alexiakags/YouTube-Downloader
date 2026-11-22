import os
import subprocess
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from utils.config import ConfigManager
from utils.paths import get_asset_path
from core.downloader import MediaDownloader, DownloadError

# Paletas Duplas: (Modo Claro: Rosa Pastel & Marrom | Modo Escuro: Rosa Escuro & Creme/Dourado)
BG_MAIN = ("#FDF2F5", "#170B11")          # Fundo geral (Rosa bebê | Vinho/Rosa bem escuro)
PANEL_BG = ("#F8E1E7", "#26121C")         # Cards/caixas (Rosa pastel | Rosa escuro profundo)
BORDER_COLOR = ("#6D4C41", "#F48FB1")     # Bordas pixeladas (Marrom café | Rosa chiclete iluminado)
TEXT_PRIMARY = ("#3E2723", "#FCE4EC")     # Texto principal (Marrom escuro | Branco rosado suave)
TEXT_MUTED = ("#8D6E63", "#D89BB0")       # Texto secundário (Marrom médio | Rosa antigo)

ACCENT_PRIMARY = ("#F48FB1", "#C71A54")   # Destaque principal (Rosa pastel | Rosa magenta vibrante)
ACCENT_HOVER = ("#EC407A", "#C2185B")     # Hover principal (Rosa intenso | Rosa escuro profundo)
BTN_START_TEXT = ("#3E2723", "#FFF8FA")   # Texto do botão Iniciar (Marrom escuro | Branco rosado)

ACCENT_SECONDARY = ("#8D6E63", "#F6BD60") # Destaque secundário / Barra (Marrom | Dourado retrô)
ACCENT_SEC_HOVER = ("#5D4037", "#E0A84B") # Hover secundário
ERROR_RED = ("#C62828", "#FF6E6E")        # Alerta de erro

FONT_TITLE = ("Consolas", 18, "bold")
FONT_LABEL = ("Consolas", 16, "bold")
FONT_BODY = ("Consolas", 14)
FONT_BTN = ("Consolas", 14, "bold")


class DownloaderApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.config = ConfigManager()
        self.is_downloading = False

        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        ctk.set_appearance_mode(self.config.theme)
        self.root.title("Youtube Downloader")
        self.root.configure(fg_color=BG_MAIN)
        self._set_window_icon()

        largura, altura = 640, 660
        x = (self.root.winfo_screenwidth() - largura) // 2
        y = (self.root.winfo_screenheight() - altura) // 2
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")
        self.root.resizable(False, False)

    def _set_window_icon(self):
        icon_path = get_asset_path("mascote.png")
        if icon_path.exists():
            try:
                pil_icon = Image.open(icon_path)
                self._window_icon = ImageTk.PhotoImage(pil_icon)
                self.root.after(200, lambda: self.root.iconphoto(False, self._window_icon))
            except Exception:
                pass

    def _build_ui(self):
        # Moldura externa estilo tela retrô
        main_frame = ctk.CTkFrame(
            self.root,
            fg_color=BG_MAIN,
            border_width=2,
            border_color=BORDER_COLOR,
            corner_radius=0,
        )
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Cabeçalho Retrô com Botão de Alternar Tema
        header = ctk.CTkFrame(
            main_frame,
            fg_color=PANEL_BG,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
        )
        header.pack(fill="x", padx=14, pady=(14, 12))

        ctk.CTkLabel(
            header,
            text=">> YT_DOWNLOADER.EXE",
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY,
        ).pack(side="left", padx=12, pady=8)

        theme_label = "[ ☀ LIGHT ]" if self.config.theme == "dark" else "[ ☾ DARK ]"
        self.btn_theme = ctk.CTkButton(
            header,
            text=theme_label,
            font=("Consolas", 13, "bold"),
            width=110,
            height=30,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
            fg_color=BG_MAIN,
            hover_color=ACCENT_PRIMARY,
            text_color=TEXT_PRIMARY,
            command=self._toggle_theme,
        )
        self.btn_theme.pack(side="right", padx=10, pady=8)

        # Seção: Input de URL + Botão Colar
        ctk.CTkLabel(
            main_frame,
            text="> INSIRA A URL DO VÍDEO OU PLAYLIST:",
            font=FONT_LABEL,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=16)

        url_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        url_frame.pack(fill="x", padx=16, pady=(4, 14))

        self.entry_url = ctk.CTkEntry(
            url_frame,
            font=FONT_BODY,
            fg_color=PANEL_BG,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            border_color=BORDER_COLOR,
            border_width=2,
            corner_radius=0,
            height=36,
            placeholder_text="https://youtube.com/watch?v=...",
        )
        self.entry_url.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            url_frame,
            text="COLAR",
            font=FONT_BTN,
            width=82,
            height=36,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
            fg_color=PANEL_BG,
            hover_color=ACCENT_PRIMARY,
            text_color=TEXT_PRIMARY,
            command=self._paste_url,
        ).pack(side="right")

        # Seção: Opções (Formato, Qualidade e Playlist)
        options_box = ctk.CTkFrame(
            main_frame,
            fg_color=PANEL_BG,
            border_width=2,
            border_color=BORDER_COLOR,
            corner_radius=0,
        )
        options_box.pack(fill="x", padx=16, pady=(0, 14))

        # Linha 1: Formatos + Playlist
        row1 = ctk.CTkFrame(options_box, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=(10, 8))

        self.format_var = ctk.StringVar(value="mp3")

        ctk.CTkLabel(row1, text="FORMATO:", font=FONT_LABEL, text_color=TEXT_MUTED).pack(side="left", padx=(0, 8))

        for texto, valor in [("MP3", "mp3"), ("WAV", "wav"), ("MP4", "mp4")]:
            ctk.CTkRadioButton(
                row1,
                text=texto,
                variable=self.format_var,
                value=valor,
                font=FONT_BODY,
                text_color=TEXT_PRIMARY,
                fg_color=ACCENT_PRIMARY,
                hover_color=ACCENT_HOVER,
                border_color=BORDER_COLOR,
                command=self._on_format_change,
            ).pack(side="left", padx=(0, 12))

        self.playlist_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            row1,
            text="PLAYLIST",
            variable=self.playlist_var,
            font=FONT_BODY,
            text_color=TEXT_PRIMARY,
            fg_color=ACCENT_SECONDARY,
            hover_color=ACCENT_SEC_HOVER,
            border_color=BORDER_COLOR,
            corner_radius=0,
        ).pack(side="right")

        # Linha 2: Seletor de Qualidade
        row2 = ctk.CTkFrame(options_box, fg_color="transparent")
        row2.pack(fill="x", padx=12, pady=(0, 10))

        ctk.CTkLabel(row2, text="QUALIDADE:", font=FONT_LABEL, text_color=TEXT_MUTED).pack(side="left", padx=(0, 8))

        self.quality_var = ctk.StringVar(value="192 kbps")
        self.quality_menu = ctk.CTkOptionMenu(
            row2,
            variable=self.quality_var,
            values=["320 kbps", "192 kbps", "128 kbps"],
            font=FONT_BODY,
            dropdown_font=FONT_BODY,
            corner_radius=0,
            fg_color=BG_MAIN,
            button_color=ACCENT_PRIMARY,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=PANEL_BG,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_hover_color=ACCENT_PRIMARY,
            width=210,
            height=30,
        )
        self.quality_menu.pack(side="left")

        # Seção: Pasta de Destino
        folder_box = ctk.CTkFrame(main_frame, fg_color="transparent")
        folder_box.pack(fill="x", padx=16, pady=(0, 16))

        self.label_pasta = ctk.CTkLabel(
            folder_box,
            text=f"DIR: {self._format_path(self.config.download_dir)}",
            font=FONT_BODY,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.label_pasta.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            folder_box,
            text="ABRIR",
            font=("Consolas", 13, "bold"),
            width=75,
            height=30,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
            fg_color=PANEL_BG,
            hover_color=ACCENT_PRIMARY,
            text_color=TEXT_PRIMARY,
            command=self._open_folder,
        ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(
            folder_box,
            text="ALTERAR",
            font=("Consolas", 13, "bold"),
            width=90,
            height=30,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
            fg_color=PANEL_BG,
            hover_color=ACCENT_PRIMARY,
            text_color=TEXT_PRIMARY,
            command=self._select_folder,
        ).pack(side="right")

        # Botão Principal Estilo Arcade Start
        self.btn_download = ctk.CTkButton(
            main_frame,
            text="[ INICIAR DOWNLOAD ]",
            font=("Consolas", 16, "bold"),
            height=46,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            text_color=BTN_START_TEXT,
            command=self._start_download,
        )
        self.btn_download.pack(fill="x", padx=16)

        # Barra de Progresso Retrô
        self.progress = ctk.CTkProgressBar(
            main_frame,
            height=18,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
            fg_color=PANEL_BG,
            progress_color=ACCENT_SECONDARY,
        )
        self.progress.set(0)
        self.progress.pack(fill="x", padx=16, pady=(16, 6))

        self.label_status = ctk.CTkLabel(
            main_frame,
            text="STATUS: AGUARDANDO COMANDO...",
            font=FONT_BODY,
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        self.label_status.pack(fill="x", padx=16)

        # Imagem decorativa no rodapé (476x535 -> 178x200 proporcional)
        asset_path = get_asset_path("mascote.png")
        if asset_path.exists():
            pil_image = Image.open(asset_path)
            retro_img = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=(178, 200),
            )
            ctk.CTkLabel(main_frame, text="", image=retro_img).pack(pady=(12, 8))

    def _on_format_change(self):
        fmt = self.format_var.get()
        if fmt == "mp3":
            self.quality_menu.configure(state="normal", values=["320 kbps", "192 kbps", "128 kbps"])
            self.quality_var.set("192 kbps")
        elif fmt == "wav":
            self.quality_menu.configure(state="disabled", values=["Sem perdas (PCM)"])
            self.quality_var.set("Sem perdas (PCM)")
        elif fmt == "mp4":
            self.quality_menu.configure(state="normal", values=["1080p", "720p", "480p", "Máxima"])
            self.quality_var.set("1080p")

    def _toggle_theme(self):
        novo_tema = "light" if self.config.theme == "dark" else "dark"
        self.config.theme = novo_tema
        ctk.set_appearance_mode(novo_tema)
        self.btn_theme.configure(text="[ ☀ LIGHT ]" if novo_tema == "dark" else "[ ☾ DARK ]")

    def _format_path(self, path: str, max_len: int = 30) -> str:
        return path if len(path) <= max_len else f"...{path[-(max_len - 3):]}"

    def _paste_url(self):
        try:
            texto = self.root.clipboard_get().strip()
            if texto.startswith(("http://", "https://")):
                self.entry_url.delete(0, "end")
                self.entry_url.insert(0, texto)
            else:
                messagebox.showwarning("AVISO", "A área de transferência não contém um link válido.")
        except Exception:
            pass

    def _select_folder(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta de destino")
        if pasta:
            self.config.download_dir = pasta
            self.label_pasta.configure(text=f"DIR: {self._format_path(pasta)}")

    def _open_folder(self):
        pasta = self.config.download_dir
        if os.path.exists(pasta):
            if sys.platform == "win32":
                os.startfile(pasta)
            elif sys.platform == "darwin":
                subprocess.run(["open", pasta])
            else:
                subprocess.run(["xdg-open", pasta])

    def _update_progress_safe(self, percent: float, text: str):
        normalized = max(0.0, min(1.0, percent / 100.0))
        self.root.after(0, lambda: self.progress.set(normalized))
        self.root.after(0, lambda: self.label_status.configure(text=f"STATUS: {text}", text_color=TEXT_PRIMARY))

    def _start_download(self):
        if self.is_downloading:
            return

        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("AVISO", "Insira um link válido antes de iniciar!")
            return

        self.is_downloading = True
        self.btn_download.configure(state="disabled", text="[ PROCESSANDO... ]")
        self.progress.set(0)
        self.label_status.configure(text="STATUS: CONECTANDO AO SERVIDOR...", text_color=TEXT_MUTED)

        thread = threading.Thread(target=self._download_worker, args=(url,), daemon=True)
        thread.start()

    def _download_worker(self, url: str):
        downloader = MediaDownloader(
            on_progress=self._update_progress_safe,
            on_status=lambda msg: self.root.after(
                0, lambda: self.label_status.configure(text=f"STATUS: {msg.upper()}", text_color=TEXT_MUTED)
            ),
        )

        raw_quality = self.quality_var.get()
        clean_quality = "best" if raw_quality == "Máxima" else raw_quality.replace(" kbps", "").replace("p", "")

        try:
            downloader.download(
                url=url,
                output_dir=self.config.download_dir,
                media_format=self.format_var.get(),
                quality=clean_quality,
                allow_playlist=self.playlist_var.get(),
            )
            self.root.after(0, self._on_download_success)
        except DownloadError as e:
            self.root.after(0, lambda: self._on_download_error(str(e)))
        finally:
            self.is_downloading = False
            self.root.after(0, lambda: self.btn_download.configure(state="normal", text="[ INICIAR DOWNLOAD ]"))

    def _on_download_success(self):
        self.progress.set(1.0)
        self.label_status.configure(text="STATUS: DOWNLOAD CONCLUÍDO! [OK]", text_color=TEXT_PRIMARY)
        self.entry_url.delete(0, "end")
        messagebox.showinfo("SUCESSO", "Mídia salva com sucesso na pasta de destino!")

    def _on_download_error(self, error_msg: str):
        self.progress.set(0)
        self.label_status.configure(text="STATUS: FALHA NA OPERAÇÃO [ERRO]", text_color=ERROR_RED)
        messagebox.showerror("ERRO", error_msg)