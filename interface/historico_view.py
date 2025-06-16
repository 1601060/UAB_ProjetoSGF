import tkinter as tk

class HistoricoView(tk.Toplevel):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.title("O meu Histórico")
        self.usuario = usuario
        self.geometry("600x400")

        # Se receberes um objecto com atributo .nome, usa-o; senão assume que 'usuario' é string
        nome = getattr(usuario, 'nome', usuario)
        label = tk.Label(self, text=f"Histórico de {nome}", font=("Arial", 14))
        label.pack(pady=20)

        # adiciona aqui o Treeview ou outro widget para mostrar o histórico
