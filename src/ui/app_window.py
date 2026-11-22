import os
import subprocess
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from utils.config import ConfigManager
from utils.paths import get_asset_path
from core.queue_manager import DownloadQueueManager, QueueItem

# Paletas Duplas: (Modo Claro: Rosa Pastel & Marrom | Modo Escuro: Rosa Escuro & Creme/Dourado)
BG_MAIN = ("#FDF2F5", "#170B11")
PANEL_BG = ("#F8E1E7", "#26121C")
BORDER_COLOR = ("#6D4C41", "#F48FB1")
TEXT_PRIMARY = ("#3E2723", "#FCE4EC")
TEXT_MUTED = ("#8D6E63", "#D89BB0")

ACCENT_PRIMARY = ("#F48FB1", "#C71A54")
ACCENT_HOVER = ("#EC407A", "#C2185B")
BTN_START_TEXT = ("#3E2723", "#FFF8FA")

ACCENT_SECONDARY = ("#8D6E63", "#F6BD60")
ACCENT_SEC_HOVER = ("#5D4037", "#E0A84B")
SUCCESS_GREEN = ("#2E7D32", "#69F0AE")
ERROR_RED = ("#C62828", "#FF6E6E")

FONT_TITLE = ("Consolas", 18, "bold")
FONT_LABEL = ("Consolas", 15, "bold")
FONT_BODY = ("Consolas", 13)
FONT_SMALL = ("Consolas", 12)
FONT_BTN = ("Consolas", 13, "bold")


class DownloaderApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.config = ConfigManager()

        self.queue_manager = DownloadQueueManager(
            on_queue_updated=lambda items: self.root.after(0, lambda: self._render_queue(items)),
            on_item_progress=self._update_progress_safe,
            on_queue_finished=lambda: self.root.after(0, self._on_queue_finished),
        )

        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        ctk.set_appearance_mode(self.config.theme)
        self.root.title("Youtube Downloader")
        self.root.configure(fg_color=BG_MAIN)
        self._set_window_icon()

        largura, altura = 660, 860
        x = (self.root.winfo_screenwidth() - largura) // 2
        y = max(10, (self.root.winfo_screenheight() - altura) // 2)
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
        main_frame = ctk.CTkFrame(
            self.root,
            fg_color=BG_MAIN,
            border_width=2,
            border_color=BORDER_COLOR,
            corner_radius=0,
        )
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Cabeçalho
        header = ctk.CTkFrame(
            main_frame,
            fg_color=PANEL_BG,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
        )
        header.pack(fill="x", padx=14, pady=(12, 10))

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
            font=FONT_BTN,
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

        # Input URL
        ctk.CTkLabel(
            main_frame,
            text="> INSIRA A URL DO VÍDEO OU PLAYLIST:",
            font=FONT_LABEL,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=16)

        url_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        url_frame.pack(fill="x", padx=16, pady=(4, 10))

        self.entry_url = ctk.CTkEntry(
            url_frame,
            font=FONT_BODY,
            fg_color=PANEL_BG,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            border_color=BORDER_COLOR,
            border_width=2,
            corner_radius=0,
            height=34,
            placeholder_text="https://youtube.com/watch?v=...",
        )
        self.entry_url.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            url_frame,
            text="COLAR",
            font=FONT_BTN,
            width=80,
            height=34,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
            fg_color=PANEL_BG,
            hover_color=ACCENT_PRIMARY,
            text_color=TEXT_PRIMARY,
            command=self._paste_url,
        ).pack(side="right")

        # Opções (Formato, Qualidade e Playlist)
        options_box = ctk.CTkFrame(
            main_frame,
            fg_color=PANEL_BG,
            border_width=2,
            border_color=BORDER_COLOR,
            corner_radius=0,
        )
        options_box.pack(fill="x", padx=16, pady=(0, 10))

        row1 = ctk.CTkFrame(options_box, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=(8, 6))

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

        row2 = ctk.CTkFrame(options_box, fg_color="transparent")
        row2.pack(fill="x", padx=12, pady=(0, 8))

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
            width=200,
            height=28,
        )
        self.quality_menu.pack(side="left")

        # Pasta de Destino
        folder_box = ctk.CTkFrame(main_frame, fg_color="transparent")
        folder_box.pack(fill="x", padx=16, pady=(0, 10))

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
            font=FONT_BTN,
            width=72,
            height=28,
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
            font=FONT_BTN,
            width=88,
            height=28,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
            fg_color=PANEL_BG,
            hover_color=ACCENT_PRIMARY,
            text_color=TEXT_PRIMARY,
            command=self._select_folder,
        ).pack(side="right")

        # Botão Adicionar à Fila
        self.btn_download = ctk.CTkButton(
            main_frame,
            text="[ + ADICIONAR À FILA ]",
            font=("Consolas", 15, "bold"),
            height=42,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            text_color=BTN_START_TEXT,
            command=self._enqueue_download,
        )
        self.btn_download.pack(fill="x", padx=16)

        # Barra de Progresso do Item Atual
        self.progress = ctk.CTkProgressBar(
            main_frame,
            height=16,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
            fg_color=PANEL_BG,
            progress_color=ACCENT_SECONDARY,
        )
        self.progress.set(0)
        self.progress.pack(fill="x", padx=16, pady=(12, 4))

        self.label_status = ctk.CTkLabel(
            main_frame,
            text="STATUS: FILA VAZIA — AGUARDANDO COMANDO...",
            font=FONT_SMALL,
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        self.label_status.pack(fill="x", padx=16, pady=(0, 8))

        # Cabeçalho da Fila + Botão Limpar
        queue_header = ctk.CTkFrame(main_frame, fg_color="transparent")
        queue_header.pack(fill="x", padx=16, pady=(2, 4))

        self.label_queue_title = ctk.CTkLabel(
            queue_header,
            text="> FILA DE DOWNLOADS (0):",
            font=FONT_LABEL,
            text_color=TEXT_PRIMARY,
        )
        self.label_queue_title.pack(side="left")

        ctk.CTkButton(
            queue_header,
            text="LIMPAR CONCLUÍDOS",
            font=("Consolas", 11, "bold"),
            width=145,
            height=24,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_COLOR,
            fg_color=PANEL_BG,
            hover_color=ACCENT_PRIMARY,
            text_color=TEXT_PRIMARY,
            command=self.queue_manager.clear_completed,
        ).pack(side="right")

        # Lista Rolável da Fila
        self.queue_list_frame = ctk.CTkScrollableFrame(
            main_frame,
            height=135,
            fg_color=PANEL_BG,
            border_width=2,
            border_color=BORDER_COLOR,
            corner_radius=0,
        )
        self.queue_list_frame.pack(fill="x", padx=16, pady=(0, 10))

        # Mascote no rodapé (proporcional 142x160 para caber confortavelmente com a fila)
        asset_path = get_asset_path("mascote.png")
        if asset_path.exists():
            pil_image = Image.open(asset_path)
            retro_img = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=(142, 160),
            )
            ctk.CTkLabel(main_frame, text="", image=retro_img).pack(pady=(2, 4))

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

    def _enqueue_download(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("AVISO", "Insira um link válido antes de adicionar à fila!")
            return

        raw_quality = self.quality_var.get()
        clean_quality = "best" if raw_quality == "Máxima" else raw_quality.replace(" kbps", "").replace("p", "")

        self.queue_manager.add_item(
            url=url,
            output_dir=self.config.download_dir,
            media_format=self.format_var.get(),
            quality=clean_quality,
            allow_playlist=self.playlist_var.get(),
        )
        self.entry_url.delete(0, "end")

    def _update_progress_safe(self, item_id: str, percent: float, text: str):
        normalized = max(0.0, min(1.0, percent / 100.0))
        self.root.after(0, lambda: self.progress.set(normalized))
        self.root.after(
            0,
            lambda: self.label_status.configure(text=f"[{item_id}] {text}", text_color=TEXT_PRIMARY),
        )

    def _on_queue_finished(self):
        self.progress.set(1.0)
        self.label_status.configure(text="STATUS: TODOS OS ITENS DA FILA PROCESSADOS [OK]", text_color=SUCCESS_GREEN)

    def _render_queue(self, items: list[QueueItem]):
        self.label_queue_title.configure(text=f"> FILA DE DOWNLOADS ({len(items)}):")

        for widget in self.queue_list_frame.winfo_children():
            widget.destroy()

        status_colors = {
            "Aguardando": TEXT_MUTED,
            "Baixando": ACCENT_SECONDARY,
            "Concluído": SUCCESS_GREEN,
            "Erro": ERROR_RED,
        }

        for item in items:
            row = ctk.CTkFrame(
                self.queue_list_frame,
                fg_color=BG_MAIN,
                border_width=1,
                border_color=BORDER_COLOR,
                corner_radius=0,
            )
            row.pack(fill="x", pady=3, padx=2)

            short_url = item.url if len(item.url) <= 32 else f"{item.url[:29]}..."
            info_text = f"[{item.media_format.upper()}] {short_url}"

            ctk.CTkLabel(
                row,
                text=info_text,
                font=FONT_SMALL,
                text_color=TEXT_PRIMARY,
                anchor="w",
            ).pack(side="left", padx=8, pady=4, fill="x", expand=True)

            ctk.CTkLabel(
                row,
                text=item.status.upper(),
                font=("Consolas", 11, "bold"),
                text_color=status_colors.get(item.status, TEXT_PRIMARY),
            ).pack(side="left", padx=6)

            if item.status != "Baixando":
                ctk.CTkButton(
                    row,
                    text="X",
                    font=("Consolas", 11, "bold"),
                    width=26,
                    height=22,
                    corner_radius=0,
                    fg_color=PANEL_BG,
                    hover_color=ERROR_RED,
                    text_color=TEXT_PRIMARY,
                    command=lambda i_id=item.id: self.queue_manager.remove_item(i_id),
                ).pack(side="right", padx=4, pady=3)