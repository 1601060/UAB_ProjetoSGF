import tkinter as tk
from tkinter import messagebox

class AjudaView:
    def __init__(self, master):
        self.master = master

    def open_manual(self):
        messagebox.showinfo("Manual de Utilização",
                            "Aqui vai o manual de utilização do SGF 2.0…")

    def contactar_suporte(self):
        messagebox.showinfo("Contactar Suporte",
                            "Envie email para suporte@exemplo.com ou ligue 800 000 000.")
