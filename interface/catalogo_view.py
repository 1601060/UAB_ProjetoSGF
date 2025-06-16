import tkinter as tk

class CatalogoView(tk.Toplevel):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.title("Catálogo de Ações")
        self.usuario = usuario
        self.geometry("800x500")
        label = tk.Label(self, text="Catálogo de Ações Disponíveis", font=("Arial", 14))
        label.pack(pady=20)
        # aqui implementar-se-á a listagem das ações (Treeview, Canvas…) - Futura funcionalidade
