import tkinter as tk
from tkinter import ttk, messagebox

class LoginWindow:
    """
    Exibe uma janela de login (Toplevel) para o utilizador inserir
    credenciais e escolher o perfil (Gestor, Formador, Formando).
    """
    def __init__(self, parent):
        self.parent = parent  # Janela principal
        self.user_role = None

    def show(self):
        login_window = tk.Toplevel(self.parent)
        login_window.title("Login")
        login_window.geometry("300x150")

        # Widgets de entrada
        ttk.Label(login_window, text="Utilizador:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_utilizador = ttk.Entry(login_window)
        entry_utilizador.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(login_window, text="Senha:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        entry_senha = ttk.Entry(login_window, show="*")
        entry_senha.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(login_window, text="Perfil:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        cb_perfil = ttk.Combobox(login_window, values=["Gestor", "Formador", "Formando"], state="readonly")
        cb_perfil.grid(row=2, column=1, padx=5, pady=5)
        cb_perfil.current(0)

        def fazer_login():
            utilizador = entry_utilizador.get().strip()
            senha = entry_senha.get().strip()
            perfil = cb_perfil.get()

            if not utilizador or not senha:
                messagebox.showwarning("Login", "Por favor, preencha utilizador e senha.")
                return

            self.user_role = perfil
            messagebox.showinfo("Login", f"Bem-vindo, {utilizador}!\nPerfil: {perfil}")
            login_window.destroy()

        # Botão de Login
        btn_login = ttk.Button(login_window, text="Login", command=fazer_login)
        btn_login.grid(row=3, column=0, columnspan=2, pady=10)

        # Impede interações com a janela principal
        login_window.grab_set()
        self.parent.wait_window(login_window)

        return self.user_role
