import os
import yt_dlp
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import json

# Caminho do arquivo de configuração
config_file = "config.json"

def carregar_config():
    """Carrega a configuração de um arquivo JSON."""
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as file:
                return json.load(file)
        except Exception:
            return {}
    return {}

def salvar_config(config):
    """Salva a configuração em um arquivo JSON."""
    with open(config_file, "w") as file:
        json.dump(config, file)

def selecionar_pasta():
    """Permite ao usuário selecionar uma nova pasta de download."""
    pasta_destino = filedialog.askdirectory(title="Selecione a pasta para salvar os arquivos")
    if pasta_destino:
        config["pasta_destino"] = pasta_destino
        salvar_config(config)
        label_pasta.config(text=f"Pasta atual: {pasta_destino}")
    else:
        messagebox.showerror("Erro", "Nenhuma pasta foi selecionada!")

def baixar_audio():
    """Baixa o áudio do YouTube e salva na pasta configurada."""
    url = entry_url.get().strip()
    if not url:
        messagebox.showerror("Erro", "Por favor, insira um link válido!")
        return

    pasta_destino = config.get("pasta_destino")
    if not pasta_destino or not os.path.exists(pasta_destino):
        messagebox.showerror("Erro", "Pasta de destino não configurada ou inexistente!")
        selecionar_pasta()
        return

    # Configurações do yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
        'ffmpeg_location': r'C:\ffmpeg-7.1-full_build\ffmpeg-7.1-full_build\bin',  # Caminho para o FFmpeg
    }

    try:
        label_status.config(text="Baixando e convertendo... Aguarde!", fg="blue")
        root.update()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        label_status.config(text="Download concluído! 🎉", fg="green")
        messagebox.showinfo("Sucesso", "Download concluído com sucesso!")
    except Exception as e:
        label_status.config(text="Erro durante o download.", fg="red")
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

def centralizar_janela(root, largura, altura):
    """Centraliza a janela na tela."""
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    pos_x = (largura_tela - largura) // 2
    pos_y = (altura_tela - altura) // 2
    root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

# Carrega a configuração inicial
config = carregar_config()

# Configuração da janela principal
root = tk.Tk()
root.title("Baixador de Áudio - YouTube")

# Dimensões da janela
largura_janela = 400
altura_janela = 250
centralizar_janela(root, largura_janela, altura_janela)
root.resizable(False, False)

# Rótulo
label_instrucoes = tk.Label(root, text="Cole o link do vídeo do YouTube:", font=("Arial", 12))
label_instrucoes.pack(pady=10)

# Entrada de texto
entry_url = tk.Entry(root, width=50, font=("Arial", 10))
entry_url.pack(pady=5)

# Botão para iniciar o download
btn_baixar = tk.Button(root, text="Baixar MP3", command=baixar_audio, font=("Arial", 10), bg="green", fg="white")
btn_baixar.pack(pady=10)

# Exibe a pasta atual de download
pasta_atual = config.get("pasta_destino", "Nenhuma pasta configurada")
label_pasta = tk.Label(root, text=f"Pasta atual: {pasta_atual}", font=("Arial", 10), fg="blue")
label_pasta.pack(pady=5)

# Botão para alterar a pasta de download
btn_alterar_pasta = tk.Button(root, text="Alterar Pasta de Download", command=selecionar_pasta, font=("Arial", 10), bg="orange", fg="black")
btn_alterar_pasta.pack(pady=10)

# Status
label_status = tk.Label(root, text="", font=("Arial", 10))
label_status.pack(pady=10)

# Executa a janela
root.mainloop()
