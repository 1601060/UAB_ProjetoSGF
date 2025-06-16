import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from data.formando import carregar_formandos
from tkcalendar import DateEntry



# Diretório base do projeto (um nível acima de 'interface')
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'Formandos.csv')

class FormandosView:
    """
    Exibe e gere o ecrã de Formandos:
    - Filtros de pesquisa
    - Paginação
    - CRUD (se for Gestor)
    - Exportar CSV
    - Gerar relatório PDF (stub)
    - Gerar gráfico (stub)
    """
    def __init__(self, container, user_role):
        self.container = container
        self.user_role = user_role

        # DataFrames e paginação
        self.formandos_data = None
        self.filtered_data = None
        self.current_page = 0
        self.page_size = 10
        self.order = {}

        # Variáveis de filtro
        self.filtro_distrito = tk.StringVar()
        self.filtro_servico = tk.StringVar()
        self.filtro_numero = tk.StringVar()
        self.filtro_nome = tk.StringVar()
        self.filtro_estado = tk.StringVar()
        self.filtro_activo = tk.StringVar()
        self.filtro_origem = tk.StringVar()

        # Treeview
        self.tree = None

    def build(self):
        # Limpa a área
        for widget in self.container.winfo_children():
            widget.destroy()

        # Carrega dados
        df = carregar_formandos()
        if df is None or df.empty:
            messagebox.showerror("Erro", "Não foi possível carregar Formandos.csv.")
            return
        self.formandos_data = df.copy()
        self.filtered_data = df.copy()
        self.current_page = 0
        self.order = {}

        # Filtros
        frame_filtros = ttk.LabelFrame(self.container, text="Filtros de Pesquisa (Formandos)")
        frame_filtros.pack(fill=tk.X, padx=10, pady=5)

        labels = ["Distrito:", "Serviço:", "Nº Funcionário:", "Nome:", "Estado:", "Activo:", "Origem:"]
        vars_ = [self.filtro_distrito, self.filtro_servico, self.filtro_numero,
                 self.filtro_nome, self.filtro_estado, self.filtro_activo, self.filtro_origem]
        cols = 4
        for i, (label, var) in enumerate(zip(labels, vars_)):
            ttk.Label(frame_filtros, text=label).grid(row=i//cols, column=(i%cols)*2,
                                                       padx=5, pady=5, sticky="e")
            if label in ["Activo:", "Origem:"]:
                cb = ttk.Combobox(frame_filtros, textvariable=var, state="readonly")
                cb['values'] = (["Ativo", "Inactivo"] if label == "Activo:" else ["Interno", "Externo"])
                cb.grid(row=i//cols, column=(i%cols)*2+1, padx=5, pady=5)
            else:
                ttk.Entry(frame_filtros, textvariable=var).grid(row=i//cols, column=(i%cols)*2+1,
                                                                 padx=5, pady=5)

        ttk.Button(frame_filtros, text="Pesquisar", command=self.aplicar_filtros)
        ttk.Button(frame_filtros, text="Pesquisar", command=self.aplicar_filtros).grid(row=2, column=0,
                                                                                         padx=5, pady=5)
        ttk.Button(frame_filtros, text="Limpar", command=self.limpar_filtros).grid(row=2, column=1,
                                                                                    padx=5, pady=5)

        # Treeview
        frame_tree = ttk.Frame(self.container)
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        vsb = ttk.Scrollbar(frame_tree, orient="vertical")
        hsb = ttk.Scrollbar(frame_tree, orient="horizontal")
        self.tree = ttk.Treeview(frame_tree, show='headings',
                                 yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        cols = list(df.columns)
        self.tree['columns'] = cols
        for col in cols:
            self.tree.heading(col, text=col, command=lambda c=col: self.ordenar(c))
            self.tree.column(col, width=100)

        # Navegação
        nav = ttk.Frame(self.container)
        nav.pack(pady=5)
        ttk.Button(nav, text="Anterior", command=self.pagina_anterior).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav, text="Próxima", command=self.pagina_proxima).pack(side=tk.LEFT, padx=5)

        # CRUD e export
        actions = ttk.Frame(self.container)
        actions.pack(pady=5)
        state = tk.NORMAL if self.user_role == 'Gestor' else tk.DISABLED
        ttk.Button(actions, text="Novo", command=self.novo_registro, state=state).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="Editar", command=self.editar_registro, state=state).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="Remover", command=self.remover_registro, state=state).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="Exportar CSV", command=self.exportar_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="Relatório PDF", command=self.gerar_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="Mostrar Gráfico", command=self.mostrar_grafico).pack(side=tk.LEFT, padx=5)

        self.atualizar()

    def aplicar_filtros(self):
        df = self.formandos_data.copy()
        if self.filtro_distrito.get(): df = df[df['distrito'].str.contains(self.filtro_distrito.get(), na=False, case=False)]
        if self.filtro_servico.get(): df = df[df['servico'].str.contains(self.filtro_servico.get(), na=False, case=False)]
        if self.filtro_numero.get(): df = df[df['numero'].astype(str).str.contains(self.filtro_numero.get(), na=False, case=False)]
        if self.filtro_nome.get(): df = df[df['nome'].str.contains(self.filtro_nome.get(), na=False, case=False)]
        if self.filtro_estado.get(): df = df[df['estado'].str.contains(self.filtro_estado.get(), na=False, case=False)]
        if self.filtro_activo.get(): df = df[df['activo'].str.contains(self.filtro_activo.get(), na=False, case=False)]
        if self.filtro_origem.get(): df = df[df['origem'].str.contains(self.filtro_origem.get(), na=False, case=False)]
        self.filtered_data = df
        self.current_page = 0
        self.atualizar()

    def limpar_filtros(self):
        for var in [self.filtro_distrito, self.filtro_servico, self.filtro_numero,
                    self.filtro_nome, self.filtro_estado, self.filtro_activo, self.filtro_origem]:
            var.set("")
        self.filtered_data = self.formandos_data.copy()
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
        page = self.filtered_data.iloc[start:end]
        for idx, row in page.iterrows():
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
        if self.user_role != 'Gestor':
            messagebox.showwarning("Permissão",
                                   "Não tem permissão para criar novos Formandos.")
            return

        root = self.container.winfo_toplevel()
        janela = tk.Toplevel(root)
        janela.title("Novo Registo de Formando")
        janela.geometry("600x400")  # ajusta conforme necessário

        # Cria o Notebook
        notebook = ttk.Notebook(janela)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Cria uma frame para cada separador
        frame_pessoais      = ttk.Frame(notebook)
        frame_profissionais = ttk.Frame(notebook)
        frame_contactos     = ttk.Frame(notebook)
        frame_educacao      = ttk.Frame(notebook)
        frame_acesso        = ttk.Frame(notebook)
        frame_eventos       = ttk.Frame(notebook)

        # Adiciona cada frame como um tab
        notebook.add(frame_pessoais,      text="Dados Pessoais")
        notebook.add(frame_profissionais, text="Dados Profissionais")
        notebook.add(frame_contactos,     text="Contactos")
        notebook.add(frame_educacao,      text="Educação")
        notebook.add(frame_acesso,        text="Acesso")
        notebook.add(frame_eventos,       text="Eventos Extra")

        # ——— Preenche o tab "Dados Pessoais" como exemplo ———
        # Aqui podes replicar os teus widgets de Nome, Distrito, Activo, etc.
        ttk.Label(frame_pessoais, text="Numero:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_numero = ttk.Entry(frame_pessoais)
        entry_numero.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_pessoais, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        entry_nome = ttk.Entry(frame_pessoais)
        entry_nome.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_pessoais, text="Distrito:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_dist = ttk.Entry(frame_pessoais)
        entry_dist.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_pessoais, text="Activo:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        var_activo = tk.StringVar(value="Ativo")
        combo_activo = ttk.Combobox(frame_pessoais, textvariable=var_activo, values=["Ativo", "Inactivo"], state="readonly")
        combo_activo.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_pessoais, text="N.º BI:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        entry_bi = ttk.Entry(frame_pessoais)
        entry_bi.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_pessoais, text="N.º Contribuinte:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        entry_contribuinte = ttk.Entry(frame_pessoais)
        entry_contribuinte.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_pessoais, text="Data Nascimento:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        dtnascimento = DateEntry(
            frame_pessoais,
            date_pattern='dd-MM-yyyy',
            showweeknumbers=False
        )
        dtnascimento.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_pessoais, text="Sexo:").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        var_sexo = tk.StringVar(value="F")
        combo_sexo = ttk.Combobox(frame_pessoais, textvariable=var_sexo, values=["F", "M"], state="readonly")
        combo_sexo.grid(row=7, column=1, padx=5, pady=5, sticky="w")




        # ——— Preenche o tab "Acesso" como exemplo ———

        ttk.Label(frame_acesso, text="perfil:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        var_perfil = tk.StringVar(value="Formando")
        combo_perfil = ttk.Combobox(frame_acesso, textvariable=var_perfil, values=["Formando", "Formador", "Gestor"], state="readonly")
        combo_perfil.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_acesso, text="origem:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        var_origem = tk.StringVar(value="Interno")
        combo_origem = ttk.Combobox(frame_acesso, textvariable=var_origem, values=["Interno", "Externo"], state="readonly")
        combo_origem.grid(row=2, column=1, padx=5, pady=5, sticky="w")


        # ——— Preenche o tab "Contactos" como exemplo ———

        ttk.Label(frame_contactos, text="Email:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_email = ttk.Entry(frame_contactos)
        entry_email.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # ——— Preenche o tab "Dados Profissionais" como exemplo ———

        ttk.Label(frame_profissionais, text="Serviço:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_servico = ttk.Entry(frame_profissionais)
        entry_servico.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_profissionais, text="Data Admissão:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        dtadmissao = DateEntry(
            frame_profissionais,
            date_pattern='dd-MM-yyyy',
            showweeknumbers=False
        )
        dtadmissao.grid(row=1, column=1, padx=5, pady=5, sticky="w")


        # ——— Botão de Gravar em baixo (fora do Notebook) ———
        btn_frame = ttk.Frame(janela)
        btn_frame.pack(fill="x", pady=(0,10))
        btn_gravar = ttk.Button(btn_frame, text="Gravar", command=lambda: self._gravar_novo( entry_numero, entry_nome, var_perfil, entry_servico, entry_dist, dtadmissao, dtnascimento, var_sexo, var_activo, var_origem, entry_bi, entry_contribuinte, entry_email, janela))

        btn_gravar.pack(side="right", padx=10)

    def _gravar_novo(self, entry_numero, entry_nome, var_perfil, entry_servico, entry_dist, dtadmissao, dtnascimento, var_sexo, var_activo, var_origem, entry_bi, entry_contribuinte, entry_email, janela):
        numero = entry_numero.get().strip()
        nome = entry_nome.get().strip()
        perfil = var_perfil.get().strip()
        servico = entry_servico.get().strip()
        dist = entry_dist.get().strip()
        dtadmissao = dtadmissao.get().strip()
        dtnascimento = dtnascimento.get().strip()
        sexo = var_sexo.get().strip()
        activo = var_activo.get().strip()
        origem = var_origem.get().strip()
        bi_num = entry_bi.get().strip()
        nif = entry_contribuinte.get().strip()
        email = entry_email.get().strip()


        if not nome or not dist or not activo or not perfil or not email:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return


        novo = pd.DataFrame([{
            "numero": numero,
            "nome": nome,
            "perfil": perfil,
            "servico": servico,
            "distrito": dist,
            "dtadmissao": dtadmissao,
            "dtnascimento": dtnascimento,
            "sexo": sexo,
            "activo": activo,
            "origem": origem,
            "bi_num": bi_num,
            "nif": nif,
            "email": email
        }])
        self.formandos_data = pd.concat(
            [self.formandos_data, novo],
            ignore_index=True,
            sort=False
        )
        self.formandos_data.to_csv(
            CSV_PATH,
            index=False,
            sep=';',
            encoding='utf-16'
        )
        self.filtered_data = self.formandos_data.copy()
        self.current_page   = 0
        self.atualizar()
        janela.destroy()

    def editar_registro(self):
        if self.user_role != 'Gestor':
            messagebox.showwarning("Permissão", "Não tem permissão para editar Formandos.")
            return

        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um Formando para editar.")
            return
        idx = int(sel[0])  # índice no DataFrame

        # Cria janela igual ao novo_registro
        root = self.container.winfo_toplevel()
        janela = tk.Toplevel(root)
        janela.title("Editar Registo de Formando")
        janela.geometry("600x400")

        # Notebook e frames
        notebook = ttk.Notebook(janela)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        frame_pessoais = ttk.Frame(notebook)
        frame_profissionais = ttk.Frame(notebook)
        frame_contactos = ttk.Frame(notebook)
        frame_educacao = ttk.Frame(notebook)
        frame_acesso = ttk.Frame(notebook)
        frame_eventos = ttk.Frame(notebook)
        notebook.add(frame_pessoais, text="Dados Pessoais")
        notebook.add(frame_profissionais, text="Dados Profissionais")
        notebook.add(frame_contactos, text="Contactos")
        notebook.add(frame_educacao, text="Educação")
        notebook.add(frame_acesso, text="Acesso")
        notebook.add(frame_eventos, text="Eventos Extra")

        # --- Campos Dados Pessoais ---
        # Número
        ttk.Label(frame_pessoais, text="Numero:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_numero = ttk.Entry(frame_pessoais)
        entry_numero.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        entry_numero.insert(0, self.formandos_data.at[idx, "numero"])

        # Nome
        ttk.Label(frame_pessoais, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        entry_nome = ttk.Entry(frame_pessoais)
        entry_nome.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        entry_nome.insert(0, self.formandos_data.at[idx, "nome"])

        # Distrito
        ttk.Label(frame_pessoais, text="Distrito:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_dist = ttk.Entry(frame_pessoais)
        entry_dist.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        entry_dist.insert(0, self.formandos_data.at[idx, "distrito"])

        # Activo
        ttk.Label(frame_pessoais, text="Activo:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        var_activo = tk.StringVar()
        combo_activo = ttk.Combobox(frame_pessoais, textvariable=var_activo,
                                    values=["Ativo", "Inactivo"], state="readonly")
        combo_activo.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        var_activo.set(self.formandos_data.at[idx, "activo"])

        # N.º BI
        ttk.Label(frame_pessoais, text="N.º BI:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        entry_bi = ttk.Entry(frame_pessoais)
        entry_bi.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        entry_bi.insert(0, self.formandos_data.at[idx, "bi_num"])

        # N.º Contribuinte
        ttk.Label(frame_pessoais, text="N.º Contribuinte:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        entry_contribuinte = ttk.Entry(frame_pessoais)
        entry_contribuinte.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        entry_contribuinte.insert(0, self.formandos_data.at[idx, "nif"])

        # Data Nascimento
        ttk.Label(frame_pessoais, text="Data Nascimento:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        date_nasc = DateEntry(frame_pessoais, date_pattern='dd-MM-yyyy', showweeknumbers=False)
        date_nasc.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        # popula com data existente (string)
        date_nasc.set_date(self.formandos_data.at[idx, "dtnascimento"])

        # Sexo
        ttk.Label(frame_pessoais, text="Sexo:").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        var_sexo = tk.StringVar()
        combo_sexo = ttk.Combobox(frame_pessoais, textvariable=var_sexo,
                                  values=["F", "M"], state="readonly")
        combo_sexo.grid(row=7, column=1, padx=5, pady=5, sticky="w")
        var_sexo.set(self.formandos_data.at[idx, "sexo"])

        # --- Campos Acesso (exemplo) ---
        # Perfil
        ttk.Label(frame_acesso, text="perfil:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        var_perfil = tk.StringVar(value="Formando")
        combo_perfil = ttk.Combobox(frame_acesso, textvariable=var_perfil, values=["Formando", "Formador", "Gestor"],
                                    state="readonly")
        combo_perfil.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Origem
        ttk.Label(frame_acesso, text="origem:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        var_origem = tk.StringVar(value="Interno")
        combo_origem = ttk.Combobox(frame_acesso, textvariable=var_origem, values=["Interno", "Externo"],
                                    state="readonly")
        combo_origem.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # ——— Preenche o tab "Contactos" como exemplo ———

        # Email
        ttk.Label(frame_contactos, text="Email:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_email = ttk.Entry(frame_contactos)
        entry_email.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # ——— Preenche o tab "Dados Profissionais" como exemplo ———

        # Servico
        ttk.Label(frame_profissionais, text="Serviço:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_servico = ttk.Entry(frame_profissionais)
        entry_servico.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Data de Admissão
        ttk.Label(frame_profissionais, text="Data Admissão:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        dtadmissao = DateEntry(
            frame_profissionais,
            date_pattern='dd-MM-yyyy',
            showweeknumbers=False
        )
        dtadmissao.grid(row=1, column=1, padx=5, pady=5, sticky="w")



        # — Botão Gravar na base —
        btn_frame = ttk.Frame(janela)
        btn_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(btn_frame, text="Gravar",
                   command=lambda: self._gravar_edicao(
                       idx,
                       entry_numero, entry_nome, entry_dist,
                       var_activo, entry_bi, entry_contribuinte,
                       date_nasc, var_sexo,
                       var_perfil, var_origem,
                       janela
                   )
                   ).pack(side="right", padx=10)

    def _gravar_edicao(
            self, idx,
            entry_numero, entry_nome, entry_dist,
            var_activo, entry_bi, entry_contribuinte,
            date_nasc, var_sexo,
            var_perfil, var_origem,
            janela
    ):
        # coleta valores
        numero = entry_numero.get().strip()
        nome = entry_nome.get().strip()
        distrito = entry_dist.get().strip()
        activo = var_activo.get().strip()
        bi_num = entry_bi.get().strip()
        nif = entry_contribuinte.get().strip()
        dtnasc = date_nasc.get_date().strftime("%d-%m-%Y")
        sexo = var_sexo.get().strip()
        perfil = var_perfil.get().strip()
        origem = var_origem.get().strip()

        # valida obrigatórios
        if not (numero and nome and distrito):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        # atualiza linha no DataFrame
        df = self.formandos_data
        df.at[idx, "numero"] = numero
        df.at[idx, "nome"] = nome
        df.at[idx, "distrito"] = distrito
        df.at[idx, "activo"] = activo
        df.at[idx, "bi_num"] = bi_num
        df.at[idx, "nif"] = nif
        df.at[idx, "dtnascimento"] = dtnasc
        df.at[idx, "sexo"] = sexo
        df.at[idx, "perfil"] = perfil
        df.at[idx, "origem"] = origem
        # … e o que mais preencheres …

        # grava e atualiza view
        df.to_csv(CSV_PATH, index=False, sep=';', encoding='utf-16')
        self.filtered_data = df.copy()
        self.current_page = 0
        self.atualizar()
        janela.destroy()

    def remover_registro(self):
        if self.user_role != 'Gestor':
            messagebox.showwarning("Permissão", "Não tem permissão para remover Formandos.")
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um Formando para remover.")
            return
        idx = int(sel[0])
        if not messagebox.askyesno("Confirmar", "Deseja remover o Formando selecionado?"):
            return
        self.formandos_data.drop(index=idx, inplace=True)
        self.formandos_data.reset_index(drop=True, inplace=True)
        self.formandos_data.to_csv(CSV_PATH, index=False, sep=';', encoding='utf-16')
        self.filtered_data = self.formandos_data.copy()
        self.current_page = 0
        self.atualizar()

    def exportar_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        if path:
            self.filtered_data.to_csv(path, sep=';', encoding='utf-16', index=False)
            messagebox.showinfo("Exportar CSV", "Dados exportados com sucesso.")

    def gerar_pdf(self):
        messagebox.showinfo("PDF", "Função de gerar PDF não implementada.")

    def mostrar_grafico(self):
        messagebox.showinfo("Gráfico", "Função de gráfico não implementada.")