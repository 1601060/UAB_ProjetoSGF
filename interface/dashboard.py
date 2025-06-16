import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data.acoes import carregar_acoes
from data.inscricoes import carregar_inscricoes

class DashboardView:
    """
    Interface de Dashboard para o perfil Gestor:
    - Frame de Gestão
    - Alertas
    - Gestão de utilizadores
    - Indicadores com gráficos
    """
    def __init__(self, container, callbacks):
        self.container = container
        self.callbacks = callbacks
        self.acoes_data = None

    def build(self):
        # Limpa a área
        for widget in self.container.winfo_children():
            widget.destroy()

        # Configura grid
        self.container.columnconfigure(0, weight=1)
        self.container.columnconfigure(1, weight=1)
        self.container.rowconfigure(0, weight=1)
        self.container.rowconfigure(1, weight=1)

        # Frame de Gestão da formação
        frame_formacao = tk.LabelFrame(self.container, text="Gestão da formação")
        frame_formacao.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ttk.Button(frame_formacao, text="Cursos", command=self.callbacks.get('acao_padrao')).pack(padx=5, pady=5, fill=tk.X)
        ttk.Button(frame_formacao, text="Ações", command=self.callbacks.get('mostrar_ecran_acoes')).pack(padx=5, pady=5, fill=tk.X)
        ttk.Button(frame_formacao, text="Relatórios", command=self.callbacks.get('acao_padrao')).pack(padx=5, pady=5, fill=tk.X)
        ttk.Button(frame_formacao, text="Pedidos", command=self.callbacks.get('acao_padrao')).pack(padx=5, pady=5, fill=tk.X)

        # Frame de Alertas e notificações
        frame_alertas = tk.LabelFrame(self.container, text="Alertas e notificações")
        frame_alertas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        cols = ("Nº de itens", "Descrição")
        tree_alertas = ttk.Treeview(frame_alertas, columns=cols, show='headings')
        for col in cols:
            tree_alertas.heading(col, text=col)
        tree_alertas.insert("", "end", values=("2", "Tem ações que terminam em 2 dias"))
        tree_alertas.insert("", "end", values=("1", "Há ações pendentes para atualizar"))
        tree_alertas.pack(fill=tk.BOTH, expand=True)

        # Frame de Gestão de utilizadores
        frame_utilizadores = tk.LabelFrame(self.container, text="Gestão de utilizadores")
        frame_utilizadores.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        ttk.Button(frame_utilizadores, text="Formandos", command=self.callbacks.get('mostrar_ecran_formandos')).pack(padx=5, pady=5, fill=tk.X)
        ttk.Button(frame_utilizadores, text="Formadores", command=self.callbacks.get('acao_padrao')).pack(padx=5, pady=5, fill=tk.X)
        ttk.Button(frame_utilizadores, text="Utilizadores", command=self.callbacks.get('acao_padrao')).pack(padx=5, pady=5, fill=tk.X)
        ttk.Button(frame_utilizadores, text="Grupos", command=self.callbacks.get('acao_padrao')).pack(padx=5, pady=5, fill=tk.X)

        # Frame de Indicadores
        frame_indicadores = tk.Frame(self.container)
        frame_indicadores.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        frame_indicadores.columnconfigure(0, weight=1)
        frame_indicadores.columnconfigure(1, weight=1)

        # Indicador: Horas de Formação
        frame_horas = tk.LabelFrame(frame_indicadores, text="Nº de horas de formação")
        frame_horas.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ttk.Button(frame_horas, text="Mostrar Gráfico de Horas", command=self.show_hours_chart).pack(padx=5, pady=5, fill=tk.X)

        # Indicador: Progresso nas Ações
        frame_progresso = tk.LabelFrame(frame_indicadores, text="Progresso nas ações")
        frame_progresso.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ttk.Button(frame_progresso, text="Mostrar Gráfico de Progresso", command=self.show_progress_chart).pack(padx=5, pady=5, fill=tk.X)

    def show_hours_chart(self):
        df = self._load_acoes()
        if df is None:
            return
        df = df[~df["estado"].isin(["Anulada", "Suspensa", "Cancelada"])]
        df["data_fim"] = pd.to_datetime(df["data_fim"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["data_fim"])
        df["ano"] = df["data_fim"].dt.year.astype(int)

        anos = sorted(df["ano"].unique())
        sel_win = self._create_selection_window("Seleção de Anos", anos, self._generate_hours_chart, df)

    def show_progress_chart(self):
        df_acoes = self._load_acoes()
        if df_acoes is None:
            return
        df_acoes["data_fim"] = pd.to_datetime(df_acoes["data_fim"], dayfirst=True, errors="coerce")
        df_acoes = df_acoes.dropna(subset=["data_fim"])
        df_acoes["ano"] = df_acoes["data_fim"].dt.year.astype(int)

        anos = sorted(df_acoes["ano"].unique())
        sel_win = self._create_selection_window("Seleção de Anos para Progresso", anos, self._generate_progress_chart, df_acoes)

    def _create_selection_window(self, title, items, callback, df):
        win = tk.Toplevel(self.container)
        win.title(title)
        win.geometry("300x300")
        tk.Label(win, text="Selecione um ou mais anos:").pack(padx=10, pady=5)
        lb = tk.Listbox(win, selectmode=tk.MULTIPLE, height=6)
        for it in items:
            lb.insert(tk.END, str(it))
        lb.pack(padx=10, pady=5, fill=tk.X)
        ttk.Button(win, text="Gerar Gráfico", command=lambda: callback(lb, df, win)).pack(pady=5)
        return win

    def _generate_hours_chart(self, listbox, df, parent_win):
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("Seleção", "Selecione pelo menos um ano.")
            return
        anos = [int(listbox.get(i)) for i in sel]
        df_f = df[df["ano"].isin(anos)]
        if df_f.empty:
            messagebox.showinfo("Informação", "Sem dados para os anos selecionados.")
            return

        # --- CONVERSÃO para numérico e remoção de possíveis NaNs
        df_f["duracao"] = pd.to_numeric(df_f["duracao"], errors="coerce")
        df_f = df_f.dropna(subset=["duracao"])

        # --- agrega e ORDENA
        df_agg = (
            df_f
            .groupby("ano")["duracao"]
            .sum()
            .reset_index()
            .sort_values("ano")  # ordena cronologicamente
            # .sort_values("duracao", ascending=False)  # ou, se quiser ordenar por total de horas
        )

        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        ax.bar(df_agg["ano"].astype(str), df_agg["duracao"])
        ax.set_xlabel("Ano")
        ax.set_ylabel("Total de Horas de Formação")
        ax.set_title("Horas de Formação por Ano")
        fig.tight_layout()

        self._show_chart_window(fig, "Gráfico de Horas de Formação")
        parent_win.destroy()

    def _generate_progress_chart(self, listbox, df_acoes, parent_win):
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("Seleção", "Selecione pelo menos um ano.")
            return
        anos = [int(listbox.get(i)) for i in sel]
        df_f = df_acoes[df_acoes["ano"].isin(anos)]
        if df_f.empty:
            messagebox.showinfo("Informação", "Sem dados para os anos selecionados.")
            return
        df_insc = carregar_inscricoes()
        if df_insc is None or df_insc.empty:
            messagebox.showerror("Erro", "Não foi possível carregar Inscrições.")
            return
        cods = df_f["codigo"].astype(str).unique()
        df_insc_f = df_insc[df_insc["codigo_accao"].astype(str).isin(cods)]
        if df_insc_f.empty:
            messagebox.showinfo("Informação", "Sem inscrições para os anos selecionados.")
            return
        df_agg = df_insc_f.groupby("estado_inscricao")["codigo_accao"].count().reset_index()
        labels = df_agg["estado_inscricao"].tolist()
        sizes = df_agg["codigo_accao"].tolist()

        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        wedges, texts, autotexts = ax.pie(sizes, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        ax.set_title("Progresso nas Ações por Estado de Inscrição")
        fig.tight_layout()
        legend = ax.legend(wedges, labels, title="Estado de Inscrição", loc="upper right", bbox_to_anchor=(1, 1))
        self._show_chart_window(fig, "Gráfico de Progresso")
        parent_win.destroy()

    def _show_chart_window(self, fig, title):
        win = tk.Toplevel(self.container)
        win.title(title)
        # Ajustar tamanho da janela ao gráfico
        win.geometry(f"{fig.get_size_inches()[0]*100:.0f}x{fig.get_size_inches()[1]*100:.0f}")
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _load_acoes(self):
        if self.acoes_data is None:
            df = carregar_acoes()
            if df is None or df.empty:
                messagebox.showerror("Erro", "Não foi possível carregar Ações.")
                return None
            self.acoes_data = df.copy()
        return self.acoes_data.copy()
