import multiprocessing as mp
import json
import os
from tempfile import NamedTemporaryFile

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

from utils.messagebox import MessageBox
from twofish import decrypt_file, generate_context, generate_key
from utils.messagebox import MessageBox
from elgamal import *
import requests


class DownloadFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.fg_color = "#3E8B97"
        self.corner_radius = 10
        self.save_path = None
        self.path = None
        self.private_key_path = None
        self.saved_file = None
        self.task = None
        self.progress_val = mp.Value('f')
        self.create_download_form()

    def create_download_form(self):
        main_label = ctk.CTkLabel(self, text="Скачать файл", font=("Arial", 40))
        main_label.pack(side=tk.TOP, pady=50)

        browse_file_form = ctk.CTkFrame(self, fg_color="transparent")
        browse_file_form.pack(side=tk.TOP, anchor=tk.W, padx=50, pady=25)

        file_path_label = ctk.CTkLabel(browse_file_form, text="Выберите файл с расширением .cl:", font=("Arial", 20))
        file_path_label.pack(side=tk.LEFT, pady=10)

        browse_button = ctk.CTkButton(browse_file_form, text="Обзор", command=self.browse_key_file)
        browse_button.pack(side=tk.LEFT, pady=10, padx=10)

        private_key_form = ctk.CTkFrame(self, fg_color="transparent")
        private_key_form.pack(side=tk.TOP, anchor=tk.W, padx=50, pady=25)
        self.private_key_label = ctk.CTkLabel(private_key_form, text="Выберите файл с закрытым ключом(.pkey):",
                                              font=("Arial", 20))
        self.private_key_label.pack(side=tk.LEFT)
        self.browse_private_key_button = ctk.CTkButton(private_key_form, text="Обзор",
                                                       command=self.browse_private_key)
        self.browse_private_key_button.pack(side=tk.LEFT, padx=10)
        self.private_key_path_entry = ctk.CTkLabel(private_key_form, text="", width=60)
        self.private_key_path_entry.pack(side=tk.LEFT)

        download_button = ctk.CTkButton(self, text="Скачать", command=self.start_downloading)
        download_button.pack(pady=10)

    def browse_key_file(self):
        key_file_path = filedialog.askopenfilename(filetypes=[("CryptoLoad files", "*.cl")])
        self.path = key_file_path

    def browse_private_key(self):
        private_key_path = filedialog.askopenfilename(filetypes=[("Private key", "*.pkey")])
        self.private_key_path = private_key_path
        if len(private_key_path) > 60:
            private_key_path = f"{private_key_path[:27]}..."
        self.private_key_path_entry.configure(text=private_key_path)

    def start_downloading(self):
        if self.task and self.task.is_alive():
            MessageBox("Ошибка", "Дождитесь или отмените текущее скачивание!", self)
        if not(self.private_key_path and self.path):
            MessageBox("Ошибка", "Выберите cl-файл и файл с расширением .pkey!", self)
            return
        with open(self.private_key_path, 'r') as pk:
            try:
                js_key = json.loads(pk.read())
                private_key = ElGamalPrivateKey.from_json(js_key)
            except Exception as e:
                MessageBox("Ошибка",str(e),self)
                return
        with open(self.path, 'rb') as f:
            try:
                self.info = json.loads(ElGamalEncryptionService().decrypt(f.read(), private_key))
            except:
                MessageBox("Ошибка","Ошибка при обработке данных ключом, вы точно используете правильный ключ?",self)
                return
        name = self.info['name']
        self.save_path = filedialog.asksaveasfile(parent=self, initialdir=os.getcwd(), initialfile=name)
        if self.save_path is None:
            return
        self.progress_window = ctk.CTkToplevel(self)
        self.progress_window.title("Прогресс загрузки")
        self.progress_window.geometry("400x150")
        self.progress_window.resizable(False, False)
        self.progress_window.protocol("WM_DELETE_WINDOW", self.cancel_download)

        self.progress_var = tk.DoubleVar(value=0)
        ctk.CTkLabel(self.progress_window, text="").pack(pady=5, anchor=tk.CENTER)
        self.progrss_info = ctk.CTkLabel(self.progress_window, text="Скачивание файла...")
        self.progrss_info.pack(anchor=tk.CENTER)
        self.progrss_bar = ctk.CTkProgressBar(self.progress_window, variable=self.progress_var)
        self.progrss_bar.pack(anchor=tk.CENTER)
        self.cancel_button = ctk.CTkButton(self.progress_window, text="Отмена", command=self.cancel_download)
        self.cancel_button.pack(pady=10, anchor=tk.CENTER)

        self.progress_window.wm_transient(self)
        self.queue = mp.Queue(1)
        self.task = mp.Process(target=self.download_file, daemon=True)
        self.task.start()
        self.after(500, self.check_proc)

    def update_progress_bar(self):
        progress = self.progress_val.value
        if not(self.task and self.task.is_alive()) and not int(progress):
            return
        if progress > 1.0:
            self.progrss_info.configure(text=f"Завершение обработки файла")
            return
        self.progrss_info.configure(text=f"Файл расшифровывается({round(progress * 100, 2)}%)")
        self.progress_var.set(progress)
        
    def check_proc(self):
        self.update_progress_bar()
        if not self.task.is_alive():
            self.progress_window.destroy()
            res = self.queue.get()
            if isinstance(res, Exception):
                MessageBox("Ошибка", str(res), self)
                if self.save_path is not None:
                    try:
                        os.remove(self.tmp_name)
                        os.remove(self.save_path.name)
                    except:
                        pass
                return
        else:
            self.after(500, self.check_proc)

    def cancel_download(self):
        if self.task.is_alive():
            self.task.kill()
            self.progress_window.destroy()
            self.queue.put(Exception("Загрузка отменена"))

    def download_file(self):
        try: 
            r = requests.get(f"{self.master.url}/storage/download/{self.info['file_id']}", stream=True)
        except requests.exceptions.ConnectionError:
            self.queue.put(Exception("Проблема при подключении к серверу!"))
            return
        if r.status_code != 200:
            self.queue.put(Exception(f"Ошибка сервера: {r.status_code}"))
            return
        xkey = generate_key(self.info['key'].encode(), int(self.info['key_len']))
        context = generate_context(bytes.fromhex(self.info['iv']), int(self.info['mode']), xkey)

        with NamedTemporaryFile("wb+", delete=True) as tmp:
            self.tmp_name = tmp.name
            for chunk in r.iter_content(chunk_size=8192):
                try: 
                    tmp.write(chunk)
                except OSError:
                    self.queue.put(Exception("Нет места на диске!"))
                    return
            tmp.seek(0)
            decrypt_file(tmp.name,context, self.save_path.name, self.progress_val)
            self.queue.put(True)