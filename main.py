import tkinter as tk
from tkinter import ttk, messagebox

from interface import (
    LoginWindow,
    setup_menus,
    DashboardView,
    FormandosView,
    AcoesView,
    InscricoesView,
    HistoricoView,
    CatalogoView,
    PedidosView,
    AjudaView
)


def main():
    # Janela principal
    root = tk.Tk()
    root.title("Sistema de Gestão de Formação - Projeto UAB - UC Projeto Final")
    root.withdraw()

    # Tema e estilo
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Arial", 11, "bold"), foreground="#002060")

    # Login
    login = LoginWindow(root)
    user_role = login.show()
    if not user_role:
        messagebox.showwarning("Login", "Login não realizado. A encerrar aplicação.")
        root.destroy()
        return

    # Mostrar janela principal
    root.deiconify()
    try:
        root.state('zoomed')  # Windows maximized
    except Exception:
        root.attributes('-fullscreen', True)

    # Container para as views
    container = tk.Frame(root)
    container.pack(fill=tk.BOTH, expand=True)

    # Callbacks para as views
    def open_dashboard():
        DashboardView(container, callbacks).build()

    def open_formandos():
        FormandosView(container, user_role).build()

    def open_acoes():
        AcoesView(container, user_role, callbacks).build()

    def open_inscricoes(record=None):
        InscricoesView(root, container, record, user_role).show()

    def open_historico():
        HistoricoView(root, user_role)

    def open_catalogo():
        CatalogoView(root, user_role)

    def open_pedidos():
        PedidosView(root, user_role)

    def open_manual():
        AjudaView(root).open_manual()

    def contactar_suporte():
        AjudaView(root).contactar_suporte()

    def default_action():
        messagebox.showinfo("Funcionalidade", "Funcionalidade a implementar.")

    callbacks = {
        'gestao': open_dashboard,
        'mostrar_ecran_acoes': open_acoes,
        'mostrar_ecran_formandos': open_formandos,
        'abrir_inscricoes': open_inscricoes,
        'mostrar_ecran_historico': open_historico,
        'mostrar_ecran_catalogo': open_catalogo,
        'mostrar_ecran_pedidos': open_pedidos,
        'abrir_manual': open_manual,
        'contactar_suporte': contactar_suporte,
        'acao_padrao': default_action
    }

    # Configuração do menu
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    setup_menus(menu_bar, user_role, callbacks)

    # View inicial
    if user_role == "Gestor":
        open_dashboard()
    else:
        messagebox.showinfo("Perfil", f"Bem-vindo, perfil: {user_role}")

    root.mainloop()


if __name__ == "__main__":
    main()
