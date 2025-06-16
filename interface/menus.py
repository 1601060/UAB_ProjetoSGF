import tkinter as tk
from tkinter import messagebox


def setup_menus(menu_bar: tk.Menu, user_role: str, callbacks: dict):
    """
    Configura o menu principal de acordo com o perfil do utilizador.

    Parâmetros:
    - menu_bar: instância de tk.Menu associada à janela principal.
    - user_role: perfil do utilizador ("Gestor", "Formador" ou "Formando").
    - callbacks: dicionário com callbacks para cada ação de menu.
      Exemplo de chaves:
        {
            'gestao': func,
            'mostrar_ecran_acoes': func,
            'mostrar_ecran_formandos': func,
            'acao_padrao': func,
            ...
        }
    """
    # Limpa menus existentes
    menu_bar.delete(0, tk.END)

    # Menu de perfis
    menu_perfis = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Os Meus Perfis", menu=menu_perfis)

    if user_role == "Gestor":
        menu_perfis.add_command(label="Gestão", command=callbacks.get('gestao', callbacks.get('acao_padrao')))

        # Percursos e Cursos (placeholders)
        menu_percursos = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Percursos", menu=menu_percursos)

        menu_cursos = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Cursos", menu=menu_cursos)

        # Ações
        menu_acoes = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Ações", menu=menu_acoes)
        menu_acoes.add_command(label="Todas as Ações", command=callbacks.get('mostrar_ecran_acoes', callbacks.get('acao_padrao')))
        menu_acoes.add_command(label="Ações Geridas por Mim", command=callbacks.get('acao_padrao'))
        menu_acoes.add_command(label="Gerir Delegações", command=callbacks.get('acao_padrao'))
        menu_acoes.add_command(label="Pedidos", command=callbacks.get('acao_padrao'))
        menu_acoes.add_command(label="Eventos", command=callbacks.get('acao_padrao'))

        # Utilizadores
        menu_utilizadores = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Utilizadores", menu=menu_utilizadores)
        menu_utilizadores.add_command(label="Formandos", command=callbacks.get('mostrar_ecran_formandos', callbacks.get('acao_padrao')))

        # Configurações, Relatórios e Ajuda
        menu_config = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Configurações", menu=menu_config)

        menu_relatorios = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Relatórios", menu=menu_relatorios)

        menu_ajuda = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Ajuda", menu=menu_ajuda)

    elif user_role == "Formador":
        menu_perfis.add_command(label="Formador", command=callbacks.get('acao_padrao'))


    elif user_role == "Formando":

        # 1) submenu de perfil

        menu_perfis.add_command(label="Formando", command=callbacks.get('acao_padrao'))

        # 2) Histórico

        menu_historico = tk.Menu(menu_bar, tearoff=0)

        menu_bar.add_cascade(label="O meu Histórico", menu=menu_historico)

        menu_historico.add_command(

            label="Ver Histórico",

            command=callbacks.get('mostrar_ecran_historico', callbacks.get('acao_padrao'))

        )

        # 3) Catálogo

        menu_catalogo = tk.Menu(menu_bar, tearoff=0)

        menu_bar.add_cascade(label="Catálogo", menu=menu_catalogo)

        menu_catalogo.add_command(

            label="Ver Catálogo",

            command=callbacks.get('mostrar_ecran_catalogo', callbacks.get('acao_padrao'))

        )

        # 4) Pedidos

        menu_pedidos = tk.Menu(menu_bar, tearoff=0)

        menu_bar.add_cascade(label="Pedidos", menu=menu_pedidos)

        menu_pedidos.add_command(

            label="Os Meus Pedidos",

            command=callbacks.get('mostrar_ecran_pedidos', callbacks.get('acao_padrao'))

        )

        # 5) Ajuda (menu suspenso)

        menu_ajuda = tk.Menu(menu_bar, tearoff=0)

        menu_bar.add_cascade(label="Ajuda", menu=menu_ajuda)

        menu_ajuda.add_command(

            label="Manual de Utilização",

            command=callbacks.get('abrir_manual', callbacks.get('acao_padrao'))

        )

        menu_ajuda.add_command(

            label="Contactar Suporte",

            command=callbacks.get('contactar_suporte', callbacks.get('acao_padrao'))

        )