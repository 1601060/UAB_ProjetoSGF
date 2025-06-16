import os
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from data.acoes import carregar_acoes
from data.inscricoes import carregar_inscricoes

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'Acoes.csv')

class AcoesView:
    """
    Exibe e gere o ecran de Ações:
    - Filtros de pesquisa
    - Paginação
    - "CRUD" (se for Gestor)
    - Acesso às Inscrições das ações
    """
    def __init__(self, container, user_role, callbacks):
        self.container = container
        self.user_role = user_role
        self.callbacks = callbacks

        # DataFrames e paginação
        self.acoes_data = None
        self.filtered_data = None
        self.current_page = 0
        self.page_size = 10
        self.order = {}

        # Variáveis de filtro
        self.filtro_area = tk.StringVar()
        self.filtro_modalidade = tk.StringVar()
        self.filtro_inicio = tk.StringVar()
        self.filtro_fim = tk.StringVar()
        self.filtro_estado = tk.StringVar()
        self.filtro_codigo = tk.StringVar()
        self.filtro_nome = tk.StringVar()

        # Treeview e botão Inscrições
        self.tree = None
        self.btn_inscricoes = None

    def build(self):
        # Limpa container
        for widget in self.container.winfo_children():
            widget.destroy()

        # Carrega dados
        df = carregar_acoes()
        if df is None or df.empty:
            messagebox.showerror("Erro", "Não foi possível carregar Ações.csv.")
            return
        self.acoes_data = df.copy()
        self.filtered_data = df.copy()
        self.current_page = 0
        self.order = {}

        # Filtros
        frame_filtros = ttk.LabelFrame(self.container, text="Filtros de Pesquisa (Ações)")
        frame_filtros.pack(fill=tk.X, padx=10, pady=5)
        labels = ["Área:", "Modalidade:", "Início:", "Fim:", "Estado:", "Código:", "Nome:"]
        vars_ = [self.filtro_area, self.filtro_modalidade, self.filtro_inicio,
                 self.filtro_fim, self.filtro_estado, self.filtro_codigo, self.filtro_nome]
        cols = 4
        for i, (lbl, var) in enumerate(zip(labels, vars_)):
            row = i // cols
            col = (i % cols) * 2
            ttk.Label(frame_filtros, text=lbl).grid(row=row, column=col, padx=5, pady=5, sticky="e")
            ttk.Entry(frame_filtros, textvariable=var).grid(row=row, column=col+1, padx=5, pady=5)
        ttk.Button(frame_filtros, text="Pesquisar", command=self.aplicar_filtros).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(frame_filtros, text="Limpar", command=self.limpar_filtros).grid(row=2, column=1, padx=5, pady=5)

        # Treeview
        frame_tree = ttk.Frame(self.container)
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        vsb = ttk.Scrollbar(frame_tree, orient="vertical")
        hsb = ttk.Scrollbar(frame_tree, orient="horizontal")
        self.tree = ttk.Treeview(frame_tree, show='headings', yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        cols_tree = list(df.columns)
        self.tree['columns'] = cols_tree
        for col in cols_tree:
            self.tree.heading(col, text=col, command=lambda c=col: self.ordenar(c))
            self.tree.column(col, width=100)

        # Navegação
        nav = ttk.Frame(self.container)
        nav.pack(pady=5)
        ttk.Button(nav, text="Anterior", command=self.pagina_anterior).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav, text="Próxima", command=self.pagina_proxima).pack(side=tk.LEFT, padx=5)

        # CRUD e Inscrições
        actions = ttk.Frame(self.container)
        actions.pack(pady=5)
        state = tk.NORMAL if self.user_role == 'Gestor' else tk.DISABLED
        ttk.Button(actions, text="Novo", command=self.novo_registro, state=state).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="Editar", command=self.editar_registro, state=state).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="Remover", command=self.remover_registro, state=state).pack(side=tk.LEFT, padx=5)
        self.btn_inscricoes = ttk.Button(actions, text="Inscrições", command=self.on_inscricoes)
        self.btn_inscricoes.pack(side=tk.LEFT, padx=5)
        self.btn_inscricoes.pack_forget()
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

        # Atualiza inicial
        self.atualizar()

    def _on_select(self, event):
        if self.tree.selection():
            self.btn_inscricoes.pack(side=tk.LEFT, padx=5)
        else:
            self.btn_inscricoes.pack_forget()

    def aplicar_filtros(self):
        df = self.acoes_data.copy()
        for attr, col in [(self.filtro_area, 'area'),
                          (self.filtro_modalidade, 'modalidade'),
                          (self.filtro_inicio, 'data_inicio'),
                          (self.filtro_fim, 'data_fim'),
                          (self.filtro_estado, 'estado'),
                          (self.filtro_codigo, 'codigo_accao'),
                          (self.filtro_nome, 'nome_accao')]:
            val = attr.get().strip()
            if val:
                df = df[df[col].astype(str).str.contains(val, case=False, na=False)]
        self.filtered_data = df
        self.current_page = 0
        self.atualizar()

    def limpar_filtros(self):
        for var in [self.filtro_area, self.filtro_modalidade, self.filtro_inicio,
                    self.filtro_fim, self.filtro_estado, self.filtro_codigo, self.filtro_nome]:
            var.set("")
        self.filtered_data = self.acoes_data.copy()
        self.current_page = 0
        self.atualizar()

    def ordenar(self, col):
        asc = self.order.get(col, True)
        self.filtered_data = self.filtered_data.sort_values(by=col, ascending=asc)
        self.order[col] = not asc
        self.current_page = 0
        self.atualizar()

    def atualizar(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if self.filtered_data is None or self.filtered_data.empty:
            return
        start = self.current_page * self.page_size
        end = start + self.page_size
        for idx, row in self.filtered_data.iloc[start:end].iterrows():
            self.tree.insert('', tk.END, iid=idx, values=list(row))

    def pagina_anterior(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.atualizar()

    def pagina_proxima(self):
        max_page = (len(self.filtered_data) - 1) // self.page_size
        if self.current_page < max_page:
            self.current_page += 1
            self.atualizar()

    def novo_registro(self):
        if self.user_role != "Gestor":
            messagebox.showwarning("Permissão", "Não tem permissão para criar novas Ações.")
            return
        root = self.container.winfo_toplevel()
        janela_novo = tk.Toplevel(root)
        janela_novo.title("Nova Ação")
        ttk.Label(janela_novo, text="Nome da Ação:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_nome = ttk.Entry(janela_novo)
        entry_nome.grid(row=0, column=1, padx=5, pady=5)
        def gravar_novo():
            nome = entry_nome.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Preencha o nome da ação.")
                return
            novo = pd.DataFrame([{"nome_accao": nome}])
            self.acoes_data = pd.concat([self.acoes_data, novo], ignore_index=True)
            self.acoes_data.to_csv(CSV_PATH, index=False, sep=';', encoding='utf-16')
            self.filtered_data = self.acoes_data.copy()
            self.current_page = 0
            self.atualizar()
            janela_novo.destroy()
        ttk.Button(janela_novo, text="Gravar", command=gravar_novo).grid(row=1, column=0, columnspan=2, pady=10)

    def editar_registro(self):
        if self.user_role != "Gestor":
            messagebox.showwarning("Permissão", "Não tem permissão para editar Ações.")
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma Ação para editar.")
            return
        idx = int(sel[0])
        root = self.container.winfo_toplevel()
        janela_edit = tk.Toplevel(root)
        janela_edit.title("Editar Ação")
        ttk.Label(janela_edit, text="Nome da Ação:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_nome = ttk.Entry(janela_edit)
        entry_nome.grid(row=0, column=1, padx=5, pady=5)
        entry_nome.insert(0, str(self.acoes_data.at[idx, "nome_accao"]))
        def gravar_edicao():
            novo_nome = entry_nome.get().strip()
            self.acoes_data.at[idx, "nome_accao"] = novo_nome
            self.acoes_data.to_csv(CSV_PATH, index=False, sep=';', encoding='utf-16')
            self.filtered_data = self.acoes_data.copy()
            self.atualizar()
            janela_edit.destroy()
        ttk.Button(janela_edit, text="Gravar", command=gravar_edicao).grid(row=1, column=0, columnspan=2, pady=10)

    def remover_registro(self):
        if self.user_role != "Gestor":
            messagebox.showwarning("Permissão", "Não tem permissão para remover Ações.")
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma Ação para remover.")
            return
        idx = int(sel[0])
        if not messagebox.askyesno("Confirmar", "Deseja remover a Ação selecionada?"):
            return
        self.acoes_data.drop(index=idx, inplace=True)
        self.acoes_data.reset_index(drop=True, inplace=True)
        self.acoes_data.to_csv(CSV_PATH, index=False, sep=';', encoding='utf-16')
        self.filtered_data = self.acoes_data.copy()
        self.current_page = 0
        self.atualizar()

    def on_inscricoes(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Inscrições", "Nenhuma ação selecionada.")
            return
        idx = int(sel[0])
        record = self.acoes_data.iloc[idx]
        self.callbacks.get('abrir_inscricoes')(record)
