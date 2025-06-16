import tkinter as tk

class PedidosView(tk.Toplevel):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.title("Os Meus Pedidos")
        self.usuario = usuario
        self.geometry("600x400")

        nome = getattr(usuario, 'nome', usuario)
        label = tk.Label(self, text=f"Pedidos de {nome}", font=("Arial", 14))
        label.pack(pady=20)

        # mostrar pedidos pendentes/histórico de pedidos
