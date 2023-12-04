import os
import multiprocessing as mp
import json
from enum import IntEnum
from tempfile import NamedTemporaryFile

import requests
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

from elgamal import *
from twofish import encrypt_file, decrypt_file, generate_context, generate_key, CallbackFunc


ctk.set_default_color_theme('dark-blue') 

    
        
class MessageBox(ctk.CTkToplevel):
    def __init__(self, type: str, msg: str, *args, fg_color: str | tuple[str, str] | None = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)
        self.title(type)
        ctk.CTkLabel(self, text=msg,font=("Arial", 24)).pack(side=tk.TOP, anchor=tk.CENTER, pady= 60, padx=60)
        
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
        
        public_key_form = ctk.CTkFrame(self, fg_color="transparent")
        public_key_form.pack(side=tk.TOP, anchor=tk.W, padx=50, pady=25)

        self.public_key_label = ctk.CTkLabel(public_key_form, text="Выберите файл с открытым ключом(.okey):", font=("Arial", 24))
        self.public_key_label.pack(side=tk.LEFT)
        self.browse_public_key_button = ctk.CTkButton(public_key_form, text="Обзор", command=self.browse_public_key)
        self.browse_public_key_button.pack(side=tk.LEFT, padx=10)
        self.public_key_path_entry = ctk.CTkLabel(public_key_form, text="", width=60)
        self.public_key_path_entry.pack(side=tk.LEFT)
        
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
        self.progress_window.resizable = (0, 0)
        self.progress_window.protocol("WM_DELETE_WINDOW", self.cancel_upload)

        self.progrss_bar = ctk.CTkProgressBar(self.progress_window, variable=self.progress_var)
        self.progrss_bar.pack(pady=10,side=tk.TOP, anchor=tk.CENTER)
        self.cancel_button = ctk.CTkButton(self.progress_window, text="Отмена", command=self.cancel_upload)
        self.cancel_button.pack(pady=10,side=tk.TOP, anchor=tk.CENTER)
        
        self.progress_var.set(0)
        self.total_size = os.path.getsize(self.path)
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
            self.task.kill()
            self.progress_window.destroy()
            self.queue.put(Exception("Загрузка отменена"))


    def update_progress_bar(self):
        progress = self.progress_val.value
        if progress > 1.0:
            progress = 1.0
        self.progress_var.set(progress)
        
    def upload_file(self):
        self.progress_var.set(0.5)
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
        response = requests.post(url, data=ciphered.file, headers=headers)
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
            if self.save_file_path is None:
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
        self.progress_window.resizable = (0, 0)
        self.progress_window.protocol("WM_DELETE_WINDOW", self.cancel_download)

        self.progress_var = tk.DoubleVar(value=0)
        self.progrss_bar = ctk.CTkProgressBar(self.progress_window, variable=self.progress_var)
        self.progrss_bar.pack(pady=10, side=tk.TOP, anchor=tk.CENTER)
        self.cancel_button = ctk.CTkButton(self.progress_window, text="Отмена", command=self.cancel_download)
        self.cancel_button.pack(pady=10, side=tk.TOP, anchor=tk.CENTER)

        self.progress_window.wm_transient(self)
        self.queue = mp.Queue(1)
        self.task = mp.Process(target=self.download_file, daemon=True)
        self.task.start()
        self.after(500, self.check_proc)

    def update_progress_bar(self):
        progress = self.progress_val.value
        if progress > 1.0:
            progress = 1.0
        self.progress_var.set(progress)
        
    def check_proc(self):
        self.update_progress_bar()
        if not self.task.is_alive():
            self.progress_window.destroy()
            res = self.queue.get()
            if isinstance(res, Exception):
                MessageBox("Ошибка", str(res), self)
                if self.save_path is not None:
                    os.remove(self.save_path.name)
                return
        else:
            self.after(500, self.check_proc)

    def cancel_download(self):
        if self.task.is_alive():
            self.task.terminate()
            self.progress_window.destroy()
            self.queue.put(Exception("Загрузка отменена"))

    def download_file(self):

        with requests.get(f"{self.master.url}/storage/download/{self.info['file_id']}", stream=True) as r:
            if r.status_code != 200:
                self.queue.put(Exception(f"Ошибка сервера: {r.status_code}"))
                return
            xkey = generate_key(self.info['key'].encode(), int(self.info['key_len']))
            context = generate_context(bytes.fromhex(self.info['iv']), int(self.info['mode']), xkey)

            with NamedTemporaryFile("wb+") as tmp:
                for chunk in r.iter_content(chunk_size=8192):
                    tmp.write(chunk)
                decrypt_file(tmp.name,context, self.save_path.name, self.progress_val)
            self.queue.put(True)
        
        
        
class ElGamalKeyGenerationFrame(ctk.CTkFrame):
    
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.fg_color = "#3E8B97"
        self.corner_radius = 10
        self.create_key_generation_form()
        self.public_key, self.private_key = None, None
        self.path = None
        self.key_counter = 0
        self.test_dict = {"Miller-Rabin": MillerRabinTester, "Fermat": FermatTester, "Solovay-Strassen": SolovayStrassenTester}

    def create_key_generation_form(self):
        main_label = ctk.CTkLabel(self, text="Генерация ключей", font=("Arial", 40))
        main_label.pack(side=tk.TOP, pady=50)

        prime_test_label = ctk.CTkLabel(self, text="Выберите тест простоты:", font=("Arial", 24))
        prime_test_label.pack(side=tk.TOP, anchor=tk.W, padx=50)

        self.prime_test_combobox = ctk.CTkComboBox(self, values=["Miller-Rabin", "Fermat", "Solovay-Strassen"])
        self.prime_test_combobox.set("Miller-Rabin")
        self.prime_test_combobox.pack(side=tk.TOP, anchor=tk.W, padx=50, pady=10)

        key_length_label = ctk.CTkLabel(self, text="Выберите длину ключа:", font=("Arial", 24))
        key_length_label.pack(side=tk.TOP, anchor=tk.W, padx=50)

        self.key_length_combobox = ctk.CTkComboBox(self, values=["128", "256", "512", "1024", "2048"])
        self.key_length_combobox.set("1024")
        self.key_length_combobox.pack(side=tk.TOP, anchor=tk.W, padx=50, pady=10)



        save_form = ctk.CTkFrame(self, fg_color="transparent")
        save_form.pack(side=tk.TOP,pady=50)
        
        generate_button = ctk.CTkButton(save_form, text="Генерировать ключи", command=self.generate_keys)
        generate_button.pack(side=tk.LEFT,padx=20)

        save_button = ctk.CTkButton(save_form, text="Сохранить ключи", command=self.save_keys)
        save_button.pack(side=tk.RIGHT,padx=20)
        
        self.key_counter_msg = ctk.CTkLabel(self, text="")
        self.key_counter_msg.pack(side=tk.TOP,anchor=tk.CENTER)

    def generate_keys(self):
        prime_test = self.prime_test_combobox.get()
        key_length = int(self.key_length_combobox.get())
        self.public_key, self.private_key = ElGamalKeyGeneratorService(self.test_dict[prime_test](), NumberGenerator()).generate_keys(0.999, key_length)
        self.key_counter+=1
        self.key_counter_msg.configure(text=f"Ключи сгенерированы({self.key_counter})")

    def save_keys(self):
        if self.public_key is None or self.private_key is None:
            MessageBox("Ошибка", "Ключи еще не были сгенерированы!",self)
            return

        self.path = filedialog.asksaveasfilename()

        if self.path is None:
            return
        
        with open(f"{self.path}.okey", 'w') as okey, open(f"{self.path}.pkey", 'w') as pkey:
            okey.write(json.dumps({'g': self.public_key.g, 'p': self.public_key.p, 'y': self.public_key.y}))
            pkey.write(json.dumps({'g': self.private_key.g, 'p': self.private_key.p, 'x': self.private_key.x}))


class InfoFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.fg_color = "#3E8B97"
        self.corner_radius = 0
        self.create_info_form()

    def create_info_form(self):
        info_text = """
        Данное приложение является курсовой работой по предмету "Защита информации".
        В ней реализовано шифрование файлов алгоритмом Twofish,
        а также шифрование ключа алгоритмом ELGAMAL.

        Выполнена студентом группы МПМ-120, Косаревским Денисом.
        """

        info_label = ctk.CTkTextbox(self, wrap=tk.WORD, width=50, height=10, font=("Arial", 16))
        info_label.insert(tk.END, info_text)
        info_label.configure(state=tk.DISABLED)
        info_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True, anchor=tk.W, pady=50, padx=50)

        
        
class FileUploaderApp(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("CryptoLoad")
        self.geometry(f"800x600")
        self.resizable=(0,0)
        self.url = "http://0.0.0.0:8000"
        self.current_form = None
        
        menu = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        
        menu.pack(side=tk.TOP,fill=tk.X, pady=10)
        upload_button = ctk.CTkButton(menu, text="Загрузить", fg_color="transparent",command=self.show_upload_form)
        upload_button.pack(side=tk.LEFT)
        download_button = ctk.CTkButton(menu, text="Скачать", fg_color="transparent",command=self.show_download_form)
        download_button.pack(side=tk.LEFT)
        keygen_button = ctk.CTkButton(menu, text="Генерация ключей", fg_color="transparent", command=self.show_keygen_form)
        keygen_button.pack(side=tk.LEFT)
        download_button = ctk.CTkButton(menu, text="Информация", fg_color="transparent",command=self.show_info_form)
        download_button.pack(side=tk.LEFT)
        
        self.upload_form = UploadFrame(self)
        self.download_form = DownloadFrame(self)
        self.info_form = InfoFrame(self)
        self.keygen_form = ElGamalKeyGenerationFrame(self)
        
        self.show_upload_form()



    def show_upload_form(self):
        if self.current_form:
            self.current_form.pack_forget()
        self.upload_form.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.current_form = self.upload_form

    def show_download_form(self):
        if self.current_form:
            self.current_form.pack_forget()
        self.download_form.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.current_form = self.download_form

    def show_info_form(self):
        if self.current_form:
            self.current_form.pack_forget()
        self.info_form.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.current_form = self.info_form 

    def show_keygen_form(self):
        if self.current_form:
            self.current_form.pack_forget()
        self.keygen_form.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.current_form = self.keygen_form

if __name__ == "__main__":
    app = FileUploaderApp()
    app.mainloop()