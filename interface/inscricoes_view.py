import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from data.formando import carregar_formandos
from data.inscricoes import carregar_inscricoes

# Diretório base e caminho do CSV de Inscrições
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'Inscricoes.csv')

class InscricoesView:
    """
    Exibe e gere o ecrã de Inscrições para uma ação selecionada:
    - Lista de inscrições existentes
    - Pesquisa e agendamento de novos formandos
    - Remoção única ou múltipla de inscrições
    """
    def __init__(self, parent, container, record, user_role):
        self.parent = parent
        self.container = container
        self.record = record
        self.user_role = user_role
        self.df_inscricoes = pd.DataFrame()
        self.tree_insc = None
        self.tree_disp = None
        # Filtros
        self.filtro_distrito = tk.StringVar()
        self.filtro_numero = tk.StringVar()
        self.filtro_nome = tk.StringVar()

    def show(self):
        # Cria janela Toplevel
        win = tk.Toplevel(self.parent)
        win.title("Vagas e Inscrições")
        win.geometry("800x600")

        # Inscrições existentes
        frame_exist = ttk.LabelFrame(win, text="Inscrições Existentes")
        frame_exist.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        vsb = ttk.Scrollbar(frame_exist, orient='vertical')
        hsb = ttk.Scrollbar(frame_exist, orient='horizontal')
        self.tree_insc = ttk.Treeview(frame_exist, show='headings', yscrollcommand=vsb.set, xscrollcommand=hsb.set, selectmode='extended')
        vsb.config(command=self.tree_insc.yview)
        hsb.config(command=self.tree_insc.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_insc.pack(fill=tk.BOTH, expand=True)

        btns = ttk.Frame(win)
        btns.pack(pady=5)
        ttk.Button(btns, text="Remover Selecionada", command=self.remover_selecionada).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Remover Múltiplas", command=self.remover_multiplas).pack(side=tk.LEFT, padx=5)

        # Formandos disponíveis
        frame_disp = ttk.LabelFrame(win, text="Formandos Disponíveis")
        frame_disp.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        filtro_frame = ttk.Frame(frame_disp)
        filtro_frame.pack(fill=tk.X)
        ttk.Label(filtro_frame, text="Distrito:").grid(row=0, column=0, padx=5)
        ttk.Entry(filtro_frame, textvariable=self.filtro_distrito).grid(row=0, column=1)
        ttk.Label(filtro_frame, text="Nº:").grid(row=0, column=2, padx=5)
        ttk.Entry(filtro_frame, textvariable=self.filtro_numero).grid(row=0, column=3)
        ttk.Label(filtro_frame, text="Nome:").grid(row=0, column=4, padx=5)
        ttk.Entry(filtro_frame, textvariable=self.filtro_nome).grid(row=0, column=5)
        ttk.Button(filtro_frame, text="Pesquisar", command=self.pesquisar_disp).grid(row=0, column=6, padx=5)

        vsb2 = ttk.Scrollbar(frame_disp, orient='vertical')
        hsb2 = ttk.Scrollbar(frame_disp, orient='horizontal')
        cols_f = ['numero', 'nome', 'distrito', 'servico', 'activo']
        self.tree_disp = ttk.Treeview(frame_disp, columns=cols_f, show='headings', yscrollcommand=vsb2.set, xscrollcommand=hsb2.set, selectmode='extended')
        # Definir colunas e headings
        for col in cols_f:
            self.tree_disp.heading(col, text=col)
            self.tree_disp.column(col, width=100)
        vsb2.config(command=self.tree_disp.yview)
        hsb2.config(command=self.tree_disp.xview)
        vsb2.pack(side=tk.RIGHT, fill=tk.Y)
        hsb2.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_disp.pack(fill=tk.BOTH, expand=True)

        btn_agenda = ttk.Frame(win)
        btn_agenda.pack(pady=5)
        ttk.Button(btn_agenda, text="Agendar Inscrição(s)", command=self.agendar_multiplas).pack()

        # Inicializa
        self._refresh_insc_tree()
        self.pesquisar_disp()

    def _get_codigo(self):
        return self.record.get('codigo_accao', self.record.get('codigo'))

    def _refresh_insc_tree(self):
        df_ins = carregar_inscricoes()
        cod = self._get_codigo()
        df_sel = df_ins[df_ins['codigo_accao'] == cod]
        self.df_inscricoes = df_sel.copy()
        cols = list(df_ins.columns)
        self.tree_insc['columns'] = cols
        for col in cols:
            self.tree_insc.heading(col, text=col)
            self.tree_insc.column(col, width=100)
        for item in self.tree_insc.get_children():
            self.tree_insc.delete(item)
        for idx, row in self.df_inscricoes.iterrows():
            self.tree_insc.insert('', tk.END, iid=idx, values=list(row))

    def remover_selecionada(self):
        if self.user_role != 'Gestor':
            messagebox.showwarning("Permissão", "Não tem permissão para remover inscrições.")
            return
        sel = self.tree_insc.selection()
        if not sel: return
        df = carregar_inscricoes()
        for s in sel:
            df = df.drop(index=int(s))
        df.to_csv(CSV_PATH, sep=';', encoding='utf-16', index=False)
        messagebox.showinfo("Remover", "Inscrições removidas com sucesso.")
        self._refresh_insc_tree()
        self.pesquisar_disp()

    def remover_multiplas(self):
        self.remover_selecionada()

    def pesquisar_disp(self):
        df_f = carregar_formandos()
        df_ins = carregar_inscricoes()
        cod = self._get_codigo()
        inscritos = set(df_ins[df_ins['codigo_accao'] == cod]['num_func'])
        df_disp = df_f[~df_f['numero'].isin(inscritos)]
        if self.filtro_distrito.get():
            df_disp = df_disp[df_disp['distrito'].str.contains(self.filtro_distrito.get(), na=False, case=False)]
        if self.filtro_numero.get():
            df_disp = df_disp[df_disp['numero'].astype(str).str.contains(self.filtro_numero.get(), na=False, case=False)]
        if self.filtro_nome.get():
            df_disp = df_disp[df_disp['nome'].str.contains(self.filtro_nome.get(), na=False, case=False)]
        for item in self.tree_disp.get_children():
            self.tree_disp.delete(item)
        for idx, row in df_disp.iterrows():
            vals = [row['numero'], row['nome'], row['distrito'], row['servico'], row['activo']]
            self.tree_disp.insert('', tk.END, iid=idx, values=vals)

    def agendar_multiplas(self):
        if self.user_role != 'Gestor':
            messagebox.showwarning("Permissão", "Não tem permissão para agendar inscrições.")
            return
        sels = self.tree_disp.selection()
        if not sels:
            messagebox.showinfo("Inscrições", "Selecione ao menos um formando.")
            return
        df_ins = carregar_inscricoes()
        novos = []
        cod = self._get_codigo()
        for s in sels:
            row = self.tree_disp.item(s, 'values')
            novos.append({
                'num_func': row[0],
                'nome': row[1],
                'servico': row[3],
                'codigo_accao': cod,
                'estado_inscricao': 'Inscrito'
            })
        df_new = pd.DataFrame(novos)
        df_up = pd.concat([df_ins, df_new], ignore_index=True)
        df_up.to_csv(CSV_PATH, sep=';', encoding='utf-16', index=False)
        messagebox.showinfo("Agendar", "Inscrições agendadas com sucesso.")
        self._refresh_insc_tree()
        self.pesquisar_disp()
