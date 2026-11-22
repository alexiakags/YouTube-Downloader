import customtkinter as ctk
from ui.app_window import DownloaderApp

def main():
    root = ctk.CTk()
    DownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    