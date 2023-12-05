import multiprocessing as mp
import json
from enum import IntEnum
import os

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

from utils.messagebox import MessageBox
from twofish import encrypt_file, generate_context, generate_key
from utils.messagebox import MessageBox
from elgamal import *
import requests


class UploadFrame(ctk.CTkFrame):
        
    class modes(IntEnum):
        ECB = 0,
        CBC = 1,
        CFB = 2,
        OFB = 3
    
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.fg_color = "#2E8B57"
        self.corner_radius = 10
        self.task = None
        self.path = None
        self.progress_val = mp.Value('f')
        self.key_len = tk.IntVar(value=None)
        self.mode = tk.StringVar(value=None)
        self.pack(side=tk.TOP, expand=True)
        self.create_upload_form()
        
    
        

    def create_upload_form(self):
        main_label = ctk.CTkLabel(self,text="Загрузить файл", font=("Arial", 40))
        main_label.pack(side=tk.TOP,pady=50)
        file_upload_form = ctk.CTkFrame(self, fg_color="transparent")
        file_upload_form.pack(side=tk.TOP,anchor=tk.W,padx=50, pady=25)
        self.file_path_label = ctk.CTkLabel(file_upload_form, text="Выберите файл:", font=("Arial", 24))
        self.file_path_label.pack(side=tk.LEFT)
        self.browse_button = ctk.CTkButton(file_upload_form, text="Обзор", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT, padx=10)
        self.file_path_entry = ctk.CTkLabel(file_upload_form, text="", width=60)
        self.file_path_entry.pack(side=tk.LEFT)
        
        public_key_form = ctk.CTkFrame(self, fg_color="transparent")
        public_key_form.pack(side=tk.TOP, anchor=tk.W, padx=50, pady=25)

        self.public_key_label = ctk.CTkLabel(public_key_form, text="Выберите файл с открытым ключом(.okey):", font=("Arial", 24))
        self.public_key_label.pack(side=tk.LEFT)
        self.browse_public_key_button = ctk.CTkButton(public_key_form, text="Обзор", command=self.browse_public_key)
        self.browse_public_key_button.pack(side=tk.LEFT, padx=10)
        self.public_key_path_entry = ctk.CTkLabel(public_key_form, text="", width=60)
        self.public_key_path_entry.pack(side=tk.LEFT)

        key_form = ctk.CTkFrame(self, fg_color="transparent")
        key_form.pack(side=tk.TOP, anchor=tk.W, padx=50, pady=25)
        self.key_label = ctk.CTkLabel(key_form, text="Введите ключ:", font=("Arial", 24))
        self.key_label.pack(side=tk.LEFT)
  
        self.key_entry = ctk.CTkEntry(key_form, show="x", width=200)  
        self.key_entry.pack(side=tk.LEFT, padx=25)
        key_size_form = ctk.CTkFrame(self, fg_color="transparent")
        key_size_form.pack(side=tk.TOP,anchor=tk.W, padx=50)
        self.key_length_label = ctk.CTkLabel(key_size_form, text="Выберите длину ключа:",font=("Arial", 24))
        self.key_length_label.pack(side=tk.LEFT)

        self.key_length_16_checkbox = ctk.CTkRadioButton(key_size_form, value=16,text="16 знаков", variable=self.key_len)
        self.key_length_16_checkbox.pack(side=tk.LEFT,padx=10)

        self.key_length_24_checkbox = ctk.CTkRadioButton(key_size_form, value=24,text="24 знака", variable=self.key_len)
        self.key_length_24_checkbox.pack(side=tk.LEFT)

        self.key_length_32_checkbox = ctk.CTkRadioButton(key_size_form, value=32,text="32 знака", variable=self.key_len)
        self.key_length_32_checkbox.pack(side=tk.LEFT)
        
        
 
        mode_form = ctk.CTkFrame(self, fg_color="transparent")
        mode_form.pack(side=tk.TOP, anchor=tk.W, padx=50,pady=25)
        self.encryption_mode_label = ctk.CTkLabel(mode_form, text="Выберите режим шифрования:",font=("Arial", 24))
        self.encryption_mode_label.pack(side=tk.LEFT)

        self.ecb_checkbox = ctk.CTkRadioButton(mode_form, text="ECB", value=self.modes.ECB, variable=self.mode)
        self.ecb_checkbox.pack(side=tk.LEFT)

        self.cbc_checkbox = ctk.CTkRadioButton(mode_form, text="CBC", value=self.modes.CBC, variable=self.mode)
        self.cbc_checkbox.pack(side=tk.LEFT)
        
        self.ofb_checkbox = ctk.CTkRadioButton(mode_form, text="OFB", value=self.modes.OFB, variable=self.mode)
        self.ofb_checkbox.pack(side=tk.LEFT)

        self.cfb_checkbox = ctk.CTkRadioButton(mode_form, text="CFB", value=self.modes.CFB, variable=self.mode)
        self.cfb_checkbox.pack(side=tk.LEFT)
        
       
        upload_send_form = ctk.CTkFrame(self, fg_color="transparent")
        upload_send_form.pack(side=tk.TOP, anchor=tk.N,pady=20)
        self.upload_button = ctk.CTkButton(upload_send_form, text="Загрузить файл", command=self.start_uploading)
        self.upload_button.pack(side=tk.TOP, anchor=tk.N)
        self.progress_var = tk.DoubleVar(value=0)
        
    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.path = file_path
        if len(file_path) > 60:
            file_path = f"{file_path[:27]}..."
        self.file_path_entry.configure(text=file_path)
        
    def browse_public_key(self):
        public_key_path = filedialog.askopenfilename(filetypes=[('Open key', '*.okey')])
        self.public_key_path = public_key_path
        if len(public_key_path) > 60:
            public_key_path = f"{public_key_path[:27]}..."
        self.public_key_path_entry.configure(text=public_key_path)

    def start_uploading(self):
        if self.task and self.task.is_alive():
            MessageBox("Ошибка", "Дождитесь или отмените текущую загрузку!", self)
            return
        self.progress_window = ctk.CTkToplevel(self)
        self.progress_window.title("Прогресс загрузки")
        self.progress_window.geometry("400x150")
        self.progress_window.resizable(False, False)
        self.progress_window.protocol("WM_DELETE_WINDOW", self.cancel_upload)
        ctk.CTkLabel(self.progress_window, text="").pack(pady=5)
        self.progrss_info = ctk.CTkLabel(self.progress_window,text="Подготовка к шифрованию...")
        self.progrss_info.pack(anchor=tk.CENTER)
        self.progrss_bar = ctk.CTkProgressBar(self.progress_window, variable=self.progress_var)
        self.progrss_bar.pack(pady=10,anchor=tk.CENTER)

        self.cancel_button = ctk.CTkButton(self.progress_window, text="Отмена", command=self.cancel_upload)
        self.cancel_button.pack(anchor=tk.CENTER)
        
        self.progress_var.set(0)
        self.progress_window.wm_transient(self)
        self.queue = mp.Queue(1)
        self.task = mp.Process(target=self.upload_file, daemon=True)
        self.task.start()
        self.after(500, self.check_proc)
    
    def check_proc(self):
        self.update_progress_bar()
        if self.task and not self.task.is_alive():
            self.progress_window.destroy()
            res = self.queue.get()
            if isinstance(res, Exception):
                MessageBox("Ошибка", str(res), self)
                return
            else:
                self.show_result(res)

        else:
            self.after(500, self.check_proc)
                        
    def cancel_upload(self):
        if self.task.is_alive():
            self.task_canceled=True
            self.task.kill()
            self.progress_window.destroy()
            self.queue.put(Exception("Загрузка отменена"))


    def update_progress_bar(self):
        if not(self.task and self.task.is_alive()):
            return
        progress = self.progress_val.value
        if progress >= 1.0:
            self.progrss_info.configure(text=f"Файл загружается на сервер")
            return
        self.progrss_info.configure(text=f"Файл шифруется({round(progress * 100, 2)}%)")
        self.progress_var.set(progress)
        
    def upload_file(self):
        key = self.key_entry.get().encode()
        mode = self.mode.get()
        key_len = self.key_len.get()
        if len(key) < key_len:
            key = key + bytes(key_len-len(key) for _ in range(key_len-len(key)))
        if not(self.path and self.public_key_path and key and mode and key_len):
            self.queue.put(Exception("Пожалуйста, выберите файл, введите ключ, выберите режим шифрования и длину ключа."))
            return
        url = f"{self.master.url}/storage/upload" 
        xkey = generate_key(key, key_len)
        iv = os.urandom(16)
        context = generate_context(iv, int(mode), xkey)
        ciphered = encrypt_file(self.path, context, self.progress_val)
        
        _, filename = os.path.split(self.path)
        headers = {'name':filename,'Content-Type': 'application/octet-stream'}
        try:
            response = requests.post(url, data=ciphered.file, headers=headers)
        except requests.exceptions.ConnectionError:
            self.queue.put(Exception("Проблема подключения к серверу!"))
            return
        ciphered.close()
        
        if response.status_code != 200:
            self.queue.put(Exception(f"Не удалось загрузить файл. Код ошибки: {response.status_code}"))
            return

        info = json.loads(response.content)
        info['name'] = filename
        info['iv'] = iv.hex().upper()
        info['key'] = key.decode()
        info['key_len'] = key_len
        info['mode'] = int(mode)
        self.queue.put(json.dumps(info))
        
    def show_result(self, info: str):
        self.save_file_path = None
        def save_file():
            self.save_file_path = filedialog.asksaveasfilename(defaultextension=".cl", filetypes=[('CryptoLoad files','*.cl')])
            if not len(self.save_file_path):
                return
            with open(self.public_key_path, 'r') as pk:
                try:
                    js_key = json.loads(pk.read())
                    public_key = ElGamalPublicKey.from_json(js_key)
                except Exception as e:
                    MessageBox("Ошибка", str(e), result_window)
                    
                    return
            encrypted_key = ElGamalEncryptionService().encrypt(info.encode(), public_key)
            with open(self.save_file_path,"wb") as f:
                f.write(encrypted_key)
            result_window.destroy()

        result_window = ctk.CTkToplevel(self)
        ctk.CTkLabel(result_window, text="Файл был загружен, выберите путь для сохранения ключа для последующего скачивания файла.").pack(side=tk.TOP, anchor=tk.N, padx=50,pady=50)
        
        ctk.CTkButton(result_window, text="Сохранить", command=save_file).pack(side=tk.TOP,pady=25)
        result_window.wm_transient(self)