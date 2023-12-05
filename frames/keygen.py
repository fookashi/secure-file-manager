import json

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

from utils.messagebox import MessageBox
from utils.messagebox import MessageBox
from elgamal import *


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

        if not len(self.path):
            return
        
        with open(f"{self.path}.okey", 'w') as okey, open(f"{self.path}.pkey", 'w') as pkey:
            okey.write(json.dumps({'g': self.public_key.g, 'p': self.public_key.p, 'y': self.public_key.y}))
            pkey.write(json.dumps({'g': self.private_key.g, 'p': self.private_key.p, 'x': self.private_key.x}))
