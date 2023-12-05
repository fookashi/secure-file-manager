import tkinter as tk
import customtkinter as ctk
from frames import *

class FileUploaderApp(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("CryptoLoad")
        self.geometry("800x600")
        self.resizable(False, False)
        self.url = "http://0.0.0.0:8000"
        self.current_form = None

        # Create a container frame for the menu
        menu_bar = tk.Menu(self, background="lightgrey")
        self.config(menu=menu_bar)

        # Create menu items for navigation
        menu_items = [
            ("Загрузить", self.show_upload_form),
            ("Скачать", self.show_download_form),
            ("Генерация ключей", self.show_keygen_form),
            ("Информация", self.show_info_form),
            ("Выход", self.exit_application)
        ]

        for text, command in menu_items:
            menu_bar.add_command(label=text, command=command)

        # Create frames for different functionalities
        self.upload_form = UploadFrame(self)
        self.download_form = DownloadFrame(self)
        self.info_form = InfoFrame(self)
        self.keygen_form = ElGamalKeyGenerationFrame(self)

        # Show the upload form initially
        self.show_upload_form()

    def show_upload_form(self):
        self.show_form(self.upload_form)

    def show_download_form(self):
        self.show_form(self.download_form)

    def show_info_form(self):
        self.show_form(self.info_form)

    def show_keygen_form(self):
        self.show_form(self.keygen_form)

    def show_form(self, form):
        if self.current_form:
            self.current_form.pack_forget()
        form.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.current_form = form
        
    def exit_application(self):
        self.destroy()
        
if __name__ == "__main__":
    app = FileUploaderApp()
    app.mainloop()
