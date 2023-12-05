import customtkinter as ctk
import tkinter as tk


class MessageBox(ctk.CTkToplevel):
    def __init__(self, type: str, msg: str, *args, fg_color: str | tuple[str, str] | None = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)
        self.title(type)
        ctk.CTkLabel(self, text=msg,font=("Arial", 24)).pack(side=tk.TOP, anchor=tk.CENTER, pady= 60, padx=60)
        
