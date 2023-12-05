import customtkinter as ctk
import tkinter as tk


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
