import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2.extras


class SistemaNotas:
    def __init__(self, root):
        """
        Inicializa a aplicação principal.
        """
        self.root = root
        self.root.title("Sistema de Cadastro e Consulta de Notas")
        self.root.geometry("1200x700")
        self.root.minsize(900, 500)
        self.root.resizable(True, True)

        self.db_params = {
            'dbname': 'sistema_notas',
            'user': 'postgres',
            'password': 'Gus.0902',
            'host': 'localhost',
            'port': '5432'
        }

        self.disciplinas = ["portugues", "matematica", "ciencias", "historia", "geografia", "educacao_fisica", "arte"]
        self.disciplinas_formatadas = {
            "portugues": "Português", "matematica": "Matemática", "ciencias": "Ciências",
            "historia": "História", "geografia": "Geografia", "educacao_fisica": "Ed. Física", "arte": "Arte"
        }

        self.style = ttk.Style()
        self.definir_estilos_ttk()
        self.criar_interface()
        self.carregar_alunos()
        self.executar_consulta()  # Executa a consulta inicial

    def definir_estilos_ttk(self):
        """
        Define os estilos customizados para os widgets ttk da aplicação, com tema escolar.
        """
        self.style.theme_use('clam')

        cor_fundo_principal = "#E0F2F7"
        cor_fundo_secundaria = "white"
        cor_fundo_terciaria = "#F8FCFF"
        cor_texto_primaria = "#2C3E50"
        cor_texto_secundaria = "#4A4A4A"
        cor_borda = "#B0D8E4"
        cor_destaque = "#81C784"
        cor_botao_padrao = "#64B5F6"
        cor_botao_ativo = "#42A5F5"
        cor_aprovado = "#4CAF50"
        cor_reprovado = "#EF5350"

        # --- Estilos Globais ---
        self.style.configure(".", background=cor_fundo_principal, foreground=cor_texto_secundaria,
                             font=('Helvetica', 10))

        # --- Notebook (Abas) ---
        self.style.configure("TNotebook", background=cor_fundo_principal, borderwidth=0)
        self.style.configure("TNotebook.Tab", padding=[15, 7], font=('Helvetica', 10, 'bold'))
        self.style.map("TNotebook.Tab",
                       background=[("selected", cor_fundo_secundaria), ("!selected", cor_fundo_terciaria)],
                       foreground=[("selected", cor_texto_primaria), ("!selected", cor_texto_secundaria)],
                       bordercolor=[("selected", cor_borda), ("!selected", cor_fundo_principal)])

        # --- Frames e LabelFrames ---
        self.style.configure("TFrame", background=cor_fundo_secundaria)
        self.style.configure("TLabelFrame", background=cor_fundo_secundaria, padding=12, borderwidth=1, relief="solid",
                             bordercolor=cor_borda)
        self.style.configure("TLabelFrame.Label", foreground=cor_texto_primaria, background=cor_fundo_secundaria,
                             font=('Helvetica', 11, 'bold'), padding=(0, 0, 0, 8))

        # --- Labels (Rótulos) ---
        self.style.configure("TLabel", background=cor_fundo_secundaria, foreground=cor_texto_secundaria,
                             font=('Helvetica', 10))

        # --- Buttons (Botões) ---
        self.style.configure("TButton", padding=(15, 7), font=('Helvetica', 10, 'bold'), foreground="white",
                             relief="flat",
                             background=cor_botao_padrao, borderwidth=0, bordercolor=cor_borda)
        self.style.map("TButton",
                       background=[('active', cor_botao_ativo), ('!disabled', cor_botao_padrao)],
                       foreground=[('disabled', 'gray')],
                       relief=[('pressed', 'sunken'), ('!pressed', 'flat')])  # Efeito de clique
        # Botões de Ação Específicos
        self.style.configure("Danger.TButton", background=cor_reprovado)
        self.style.map("Danger.TButton", background=[('active', '#C62828'), ('!disabled', cor_reprovado)])
        self.style.configure("Success.TButton", background=cor_aprovado)
        self.style.map("Success.TButton", background=[('active', '#2E7D32'), ('!disabled', cor_aprovado)])

        # --- Entry e Combobox ---
        self.style.configure("TEntry", padding=6, font=('Helvetica', 10), fieldbackground="white",
                             foreground=cor_texto_primaria,
                             borderwidth=1, relief="solid", bordercolor=cor_borda)
        self.style.configure("TCombobox", padding=6, font=('Helvetica', 10), fieldbackground="white",
                             foreground=cor_texto_primaria,
                             borderwidth=1, relief="solid", bordercolor=cor_borda)
        self.style.map("TCombobox", fieldbackground=[('readonly', 'white')],
                       selectbackground=[('readonly', cor_fundo_terciaria)],
                       selectforeground=[('readonly', cor_texto_primaria)])

        # --- Treeview (Tabelas) ---
        self.style.configure("Treeview", background="white", foreground=cor_texto_secundaria, rowheight=30,
                             fieldbackground="white", borderwidth=1, relief="solid", bordercolor=cor_borda)
        self.style.map("Treeview", background=[('selected', cor_destaque)], foreground=[('selected', 'white')])

        # Cabeçalhos da Treeview
        self.style.configure("Treeview.Heading", background=cor_destaque, foreground="white",
                             font=('Helvetica', 10, 'bold'), padding=10, relief='flat', borderwidth=0)
        self.style.map("Treeview.Heading", background=[('active', '#66BB6A')])  # Verde mais escuro ao passar o mouse

        # --- Radiobuttons ---
        self.style.configure("TRadiobutton", background=cor_fundo_secundaria, font=('Helvetica', 10),
                             foreground=cor_texto_secundaria)
        self.style.map("TRadiobutton",
                       background=[('active', cor_fundo_terciaria)])  # Destaca levemente ao passar o mouse

    def criar_interface(self):
        """
        Cria a estrutura principal da interface gráfica com duas abas.
        """
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)  # Mais padding para respiro

        self.tab_cadastro = ttk.Frame(self.notebook, style="TFrame", padding=20)  # Mais padding interno
        self.notebook.add(self.tab_cadastro, text="  Cadastro  ")
        self.tab_cadastro.columnconfigure(0, weight=1)
        self.tab_cadastro.rowconfigure(1, weight=1)

        self.tab_consulta = ttk.Frame(self.notebook, style="TFrame", padding=20)  # Mais padding interno
        self.notebook.add(self.tab_consulta, text="  Consulta  ")
        self.tab_consulta.columnconfigure(0, weight=1)
        self.tab_consulta.rowconfigure(1, weight=1)

        self.configurar_aba_cadastro()
        self.configurar_aba_consulta()

        # Configurar tags de linha alternadas diretamente no Treeview
        self.tree.tag_configure("oddrow", background="white")
        self.tree.tag_configure("evenrow", background="#F0F8F9")
        self.tree_final.tag_configure("oddrow", background="white")
        self.tree_final.tag_configure("evenrow", background="#F0F8F9")


    def configurar_aba_cadastro(self):
        """
        Configura os widgets e o layout da aba de cadastro de alunos e notas.
        """
        frame_aluno = ttk.LabelFrame(self.tab_cadastro, text="Cadastro de Alunos")
        frame_aluno.grid(row=0, column=0, sticky='ew', padx=0, pady=(0, 20))  # Mais pady
        frame_aluno.columnconfigure(1, weight=1)
        ttk.Label(frame_aluno, text="Nome do Aluno:").grid(row=0, column=0, padx=10, pady=10,
                                                           sticky='w')  # Mais padding
        self.entry_nome = ttk.Entry(frame_aluno, width=50)
        self.entry_nome.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        ttk.Button(frame_aluno, text="Cadastrar Aluno", command=self.cadastrar_aluno, style="Success.TButton").grid(
            row=0, column=2, padx=15, pady=10)  # Mais padding

        frame_notas = ttk.LabelFrame(self.tab_cadastro, text="Cadastro de Notas")
        frame_notas.grid(row=1, column=0, sticky='nsew', padx=0, pady=(0, 0))  # Sem pady inferior
        frame_notas.columnconfigure(1, weight=1)
        ttk.Label(frame_notas, text="Selecione o Aluno:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.combo_alunos = ttk.Combobox(frame_notas, width=48, state="readonly")
        self.combo_alunos.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        ttk.Button(frame_notas, text="Excluir Aluno Selecionado", command=self.excluir_aluno_selecionado,
                   style="Danger.TButton").grid(row=0, column=2, padx=15, pady=10, sticky='e')
        ttk.Label(frame_notas, text="Semestre:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.combo_semestre = ttk.Combobox(frame_notas, width=10, values=["1", "2"], state="readonly")
        self.combo_semestre.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        self.combo_semestre.current(0)
        self.entries_notas = {}
        for i, disciplina in enumerate(self.disciplinas):
            ttk.Label(frame_notas, text=f"{self.disciplinas_formatadas[disciplina]}:").grid(row=i + 2, column=0,
                                                                                            padx=10,
                                                                                            pady=8,
                                                                                            sticky='w')  # Mais pady
            entry = ttk.Entry(frame_notas, width=10)
            entry.grid(row=i + 2, column=1, padx=10, pady=8, sticky='w')
            self.entries_notas[disciplina] = entry
        ttk.Button(frame_notas, text="Salvar Notas", command=self.salvar_notas, style="Success.TButton").grid(
            row=len(self.disciplinas) + 2, column=0, columnspan=3, padx=10,
            pady=20)  # Mais pady e columnspan para centralizar

    def configurar_aba_consulta(self):
        """
        Configura a aba de consulta com opções de visualização e tabelas dinâmicas.
        """
        # --- Frame para todos os filtros e opções ---
        frame_filtros_geral = ttk.LabelFrame(self.tab_consulta, text="Opções de Consulta")
        frame_filtros_geral.grid(row=0, column=0, sticky='ew', padx=0, pady=(0, 20))
        frame_filtros_geral.columnconfigure(1, weight=1)

        # --- Sub-frame para tipo de consulta ---
        frame_tipo_consulta = ttk.Frame(frame_filtros_geral)
        frame_tipo_consulta.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='w')
        ttk.Label(frame_tipo_consulta, text="Tipo de Visualização:", font=('Helvetica', 10, 'bold')).pack(side='left', anchor='w', padx=(0,15))  # Mais padding
        self.consulta_tipo_var = tk.StringVar(value="Por Semestre")
        ttk.Radiobutton(frame_tipo_consulta, text="Por Semestre", variable=self.consulta_tipo_var, value="Por Semestre",
                        command=self.alternar_filtros).pack(side='left', anchor='w', padx=10)
        ttk.Radiobutton(frame_tipo_consulta, text="Situação Final", variable=self.consulta_tipo_var,
                        value="Situação Final", command=self.alternar_filtros).pack(side='left', anchor='w', padx=10)

        # --- Sub-frame para filtros específicos (inicialmente visível) ---
        self.frame_filtros_semestral = ttk.Frame(frame_filtros_geral)
        self.frame_filtros_semestral.grid(row=1, column=0, columnspan=3, sticky='ew')
        self.frame_filtros_semestral.columnconfigure(1, weight=1)

        ttk.Label(self.frame_filtros_semestral, text="Nome do Aluno:").grid(row=0, column=0, padx=10, pady=8,
                                                                            sticky='w')
        self.entry_filtro_nome = ttk.Entry(self.frame_filtros_semestral, width=50)
        self.entry_filtro_nome.grid(row=0, column=1, padx=10, pady=8, sticky='ew')

        # Listbox para sugestões do autocompletar
        self.listbox_sugestoes = tk.Listbox(self.frame_filtros_semestral, height=5, relief="solid", borderwidth=1,
                                            font=('Helvetica', 10), background="white", foreground="black",
                                            highlightbackground="lightgrey", highlightcolor="darkgrey",
                                            selectbackground="lightgrey", selectforeground="black") # Corrigido aqui
        self.listbox_sugestoes.grid(row=1, column=1, padx=10, sticky='ew')
        self.listbox_sugestoes.grid_remove()  # Inicia escondido

        # Bind para o autocompletar e seleção
        self.entry_filtro_nome.bind("<KeyRelease>", self.atualizar_sugestoes_alunos)
        self.entry_filtro_nome.bind("<FocusOut>",
                                    lambda e: self.listbox_sugestoes.after(150, self.listbox_sugestoes.grid_remove))
        self.listbox_sugestoes.bind("<<ListboxSelect>>", self.selecionar_sugestao_aluno)

        ttk.Label(self.frame_filtros_semestral, text="Semestre:").grid(row=2, column=0, padx=10, pady=8, sticky='w')
        self.combo_filtro_semestre = ttk.Combobox(self.frame_filtros_semestral, width=15, values=["Todos", "1", "2"],
                                                  state="readonly")
        self.combo_filtro_semestre.grid(row=2, column=1, padx=10, pady=8, sticky='w')
        self.combo_filtro_semestre.current(0)
        ttk.Label(self.frame_filtros_semestral, text="Situação:").grid(row=3, column=0, padx=10, pady=8, sticky='w')
        self.combo_filtro_situacao = ttk.Combobox(self.frame_filtros_semestral, width=15,
                                                  values=["Todos", "Aprovado", "Reprovado"], state="readonly")
        self.combo_filtro_situacao.grid(row=3, column=1, padx=10, pady=8, sticky='w')
        self.combo_filtro_situacao.current(0)

        ttk.Button(frame_filtros_geral, text="Consultar", command=self.executar_consulta).grid(row=4, column=0,columnspan=3, padx=10,pady=15)  # Mais pady

        # --- Frame para os resultados (contém as duas tabelas) ---
        frame_resultados = ttk.Frame(self.tab_consulta, style="TFrame")
        frame_resultados.grid(row=1, column=0, sticky='nsew')
        frame_resultados.columnconfigure(0, weight=1)
        frame_resultados.rowconfigure(0, weight=1)

        # --- Tabela 1: Consulta Semestral ---
        colunas_semestral = ["aluno_id", "nome", "semestre"] + self.disciplinas + ["media", "situacao"]
        self.tree = ttk.Treeview(frame_resultados, columns=colunas_semestral, show='headings')
        self.tree.heading("aluno_id", text="ID");
        self.tree.column("aluno_id", width=40, stretch=tk.NO, anchor='center')
        self.tree.heading("nome", text="Nome do Aluno");
        self.tree.column("nome", width=200, stretch=tk.YES)
        self.tree.heading("semestre", text="Sem.");
        self.tree.column("semestre", width=50, stretch=tk.NO, anchor='center')
        for d in self.disciplinas:
            self.tree.heading(d, text=self.disciplinas_formatadas[d]);
            self.tree.column(d, width=80, stretch=tk.NO, anchor='center')
        self.tree.heading("media", text="Média");
        self.tree.column("media", width=70, stretch=tk.NO, anchor='center')
        self.tree.heading("situacao", text="Situação");
        self.tree.column("situacao", width=100, stretch=tk.NO, anchor='center')
        self.scrollbar = ttk.Scrollbar(frame_resultados, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.scrollbar.grid(row=0, column=1, sticky='ns')

        # --- Tabela 2: Situação Final ---
        colunas_finais = ["nome"] + [f"{d}_final" for d in self.disciplinas] + ["media_final", "situacao_final"]
        self.tree_final = ttk.Treeview(frame_resultados, columns=colunas_finais, show='headings')
        self.tree_final.heading("nome", text="Nome do Aluno");
        self.tree_final.column("nome", width=250, stretch=tk.YES)
        for d in self.disciplinas:
            self.tree_final.heading(f"{d}_final", text=f"M. {self.disciplinas_formatadas[d]}");
            self.tree_final.column(f"{d}_final", width=90, stretch=tk.NO, anchor='center')
        self.tree_final.heading("media_final", text="Média Final");
        self.tree_final.column("media_final", width=90, stretch=tk.NO, anchor='center')
        self.tree_final.heading("situacao_final", text="Situação Final");
        self.tree_final.column("situacao_final", width=120, stretch=tk.NO, anchor='center')
        self.scrollbar_final = ttk.Scrollbar(frame_resultados, orient="vertical", command=self.tree_final.yview)
        self.tree_final.configure(yscrollcommand=self.scrollbar_final.set)
        self.tree_final.grid(row=0, column=0, sticky='nsew')
        self.scrollbar_final.grid(row=0, column=1, sticky='ns')
        self.tree_final.grid_remove();
        self.scrollbar_final.grid_remove()

        # --- Frame para botões de ação (APENAS Excluir) ---
        frame_acoes = ttk.Frame(self.tab_consulta, style="TFrame")
        frame_acoes.grid(row=2, column=0, sticky='ew', padx=0, pady=(20, 0))  # Mais pady
        frame_acoes.columnconfigure(1, weight=1)

        self.btn_excluir = ttk.Button(frame_acoes, text="Excluir Registro de Notas", command=self.excluir_registro, style="Danger.TButton")
        self.btn_excluir.pack(side='right', padx=10, pady=5)  # Mais padding

    def alternar_filtros(self):
        """Mostra ou esconde os filtros semestrais com base na escolha do RadioButton."""
        if self.consulta_tipo_var.get() == "Por Semestre":
            self.frame_filtros_semestral.grid()
            self.listbox_sugestoes.grid_remove()
        else:
            self.frame_filtros_semestral.grid_remove()
            self.listbox_sugestoes.grid_remove()

    def executar_consulta(self):
        """Verifica o tipo de consulta selecionado e chama a função correspondente."""
        tipo = self.consulta_tipo_var.get()
        if tipo == "Por Semestre":
            self.consultar_por_semestre()
            self.btn_excluir.config(state='normal')
        else:
            self.consultar_situacao_final()
            self.btn_excluir.config(state='disabled')

    def conectar_bd(self):
        try:
            return psycopg2.connect(**self.db_params)
        except (Exception, psycopg2.DatabaseError) as error:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados: {error}")
            return None

    def carregar_alunos(self):
        conn = self.conectar_bd()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome FROM alunos ORDER BY nome")
                alunos = cursor.fetchall()
                self.combo_alunos['values'] = [f"{a[0]} - {a[1]}" for a in alunos] if alunos else []
            except (Exception, psycopg2.DatabaseError) as error:
                messagebox.showerror("Erro", f"Erro ao carregar alunos: {error}")
            finally:
                conn.close()

    def cadastrar_aluno(self):
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showwarning("Campo Obrigatório", "Informe o nome do aluno.")
            return
        conn = self.conectar_bd()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO alunos (nome) VALUES (%s) RETURNING id", (nome,))
                aluno_id = cursor.fetchone()[0]
                conn.commit()
                messagebox.showinfo("Sucesso", f"Aluno '{nome}' (ID: {aluno_id}) cadastrado.")
                self.entry_nome.delete(0, tk.END)
                self.carregar_alunos()
            except (Exception, psycopg2.DatabaseError) as error:
                conn.rollback()
                messagebox.showerror("Erro", f"Erro ao cadastrar aluno: {error}")
            finally:
                conn.close()

    def salvar_notas(self):
        aluno_selecionado = self.combo_alunos.get()
        if not aluno_selecionado:
            messagebox.showwarning("Seleção Necessária", "Selecione um aluno.")
            return
        try:
            aluno_id = int(aluno_selecionado.split(" - ")[0])
            semestre = int(self.combo_semestre.get())
            notas = {}
            for d in self.disciplinas:
                nota_str = self.entries_notas[d].get().replace(',', '.').strip()
                if not nota_str:
                    messagebox.showwarning("Campo Obrigatório", f"Informe a nota de {self.disciplinas_formatadas[d]}.")
                    return
                nota = float(nota_str)
                if not (0 <= nota <= 10):
                    messagebox.showwarning("Nota Inválida",
                                           f"A nota de {self.disciplinas_formatadas[d]} deve ser entre 0 e 10.")
                    return
                notas[d] = nota
        except (ValueError, IndexError) as e:
            messagebox.showerror("Erro de Dados", "Verifique os dados informados.")
            return

        media = sum(notas.values()) / len(notas)
        aprovado = media >= 6.0

        conn = self.conectar_bd()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM notas WHERE aluno_id = %s AND semestre = %s", (aluno_id, semestre))
                if cursor.fetchone():
                    set_clause = ", ".join([f"{d} = %s" for d in self.disciplinas])
                    query = f"UPDATE notas SET {set_clause}, media = %s, aprovado = %s WHERE aluno_id = %s AND semestre = %s"
                    cursor.execute(query, list(notas.values()) + [media, aprovado, aluno_id, semestre])
                    msg = "Notas atualizadas com sucesso!"
                else:
                    cols = ", ".join(self.disciplinas)
                    vals = ", ".join(["%s"] * len(self.disciplinas))
                    query = f"INSERT INTO notas (aluno_id, semestre, {cols}, media, aprovado) VALUES (%s, %s, {vals}, %s, %s)"
                    cursor.execute(query, [aluno_id, semestre] + list(notas.values()) + [media, aprovado])
                    msg = "Notas cadastradas com sucesso!"
                conn.commit()
                messagebox.showinfo("Sucesso",
                                    f"{msg}\nMédia: {media:.2f} - Situação: {'Aprovado(a)' if aprovado else 'Reprovado(a)'}")
                self.executar_consulta()  # Atualiza a aba de consulta
            except (Exception, psycopg2.DatabaseError) as error:
                conn.rollback()
                messagebox.showerror("Erro ao Salvar", f"Erro: {error}")
            finally:
                conn.close()

    def consultar_por_semestre(self):
        """Consulta as notas por semestre e exibe na tabela principal."""
        self.tree_final.grid_remove();
        self.scrollbar_final.grid_remove()
        self.tree.grid();
        self.scrollbar.grid()

        for item in self.tree.get_children(): self.tree.delete(item)

        query = "SELECT a.id, a.nome, n.semestre, n.portugues, n.matematica, n.ciencias, n.historia, n.geografia, n.educacao_fisica, n.arte, n.media, n.aprovado FROM alunos a JOIN notas n ON a.id = n.aluno_id WHERE 1=1"
        params = []
        if self.entry_filtro_nome.get().strip():
            query += " AND a.nome ILIKE %s";
            params.append(f"%{self.entry_filtro_nome.get().strip()}%")
        if self.combo_filtro_semestre.get() != "Todos":
            query += " AND n.semestre = %s";
            params.append(int(self.combo_filtro_semestre.get()))
        if self.combo_filtro_situacao.get() != "Todos":
            query += " AND n.aprovado = %s";
            params.append(self.combo_filtro_situacao.get() == "Aprovado")
        query += " ORDER BY a.nome, n.semestre"

        conn = self.conectar_bd()
        if conn:
            try:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cursor.execute(query, params)

                # Popula a Treeview com cores alternadas
                for i, r in enumerate(cursor.fetchall()):
                    vals = [r['id'], r['nome'], r['semestre']] + \
                           [f"{r[d]:.1f}" if r[d] is not None else '-' for d in self.disciplinas] + \
                           [f"{r['media']:.1f}" if r['media'] is not None else '-',
                            "Aprovado" if r['aprovado'] else "Reprovado"]

                    tag = "evenrow" if i % 2 == 0 else "oddrow"
                    self.tree.insert("", "end", values=vals, tags=(tag,))

            except (Exception, psycopg2.DatabaseError) as error:
                messagebox.showerror("Erro de Consulta", f"Erro: {error}")
            finally:
                conn.close()

    def consultar_situacao_final(self):
        """Consulta a situação final e exibe na tabela secundária."""
        self.tree.grid_remove();
        self.scrollbar.grid_remove()
        self.tree_final.grid();
        self.scrollbar_final.grid()
        self.btn_excluir.config(state='disabled')

        for item in self.tree_final.get_children(): self.tree_final.delete(item)

        query = """
            SELECT a.nome, AVG(n.portugues) p, AVG(n.matematica) m, AVG(n.ciencias) c,
                   AVG(n.historia) h, AVG(n.geografia) g, AVG(n.educacao_fisica) ef,
                   AVG(n.arte) ar, AVG(n.media) media_final
            FROM alunos a JOIN notas n ON a.id = n.aluno_id
            GROUP BY a.id, a.nome HAVING COUNT(n.semestre) = 2 ORDER BY a.nome
        """
        conn = self.conectar_bd()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                resultados = cursor.fetchall()
                if not resultados:
                    self.tree_final.insert("", "end", values=["Nenhum aluno com 2 semestres completos."],tags=("oddrow",))
                    return

                # Popula a Treeview com cores alternadas
                for i, r in enumerate(resultados):
                    media_final = r[8] if r[8] is not None else 0.0  # Garante que media_final seja numérico
                    situacao = "Aprovado" if media_final >= 6.0 else "Reprovado"
                    vals = [r[0]] + [f"{nota:.2f}" if nota is not None else '-' for nota in r[1:8]] + \
                           [f"{media_final:.2f}", situacao]

                    tag = "evenrow" if i % 2 == 0 else "oddrow"
                    self.tree_final.insert("", "end", values=vals, tags=(tag,))

            except (Exception, psycopg2.DatabaseError) as error:
                messagebox.showerror("Erro de Consulta", f"Erro: {error}")
            finally:
                conn.close()

    def atualizar_sugestoes_alunos(self, event=None):
        """Atualiza a lista de sugestões de alunos no Listbox."""
        texto_digitado = self.entry_filtro_nome.get().strip()
        self.listbox_sugestoes.delete(0, tk.END)

        if texto_digitado:
            conn = self.conectar_bd()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT nome FROM alunos WHERE nome ILIKE %s ORDER BY nome LIMIT 10",
                                   (f"%{texto_digitado}%",))
                    sugestoes = [row[0] for row in cursor.fetchall()]
                    for sugestao in sugestoes:
                        self.listbox_sugestoes.insert(tk.END, sugestao)

                    info_entry = self.entry_filtro_nome.grid_info()
                    self.listbox_sugestoes.grid(row=info_entry['row'] + 1, column=info_entry['column'],
                                                padx=info_entry['padx'], sticky='ew')
                    self.listbox_sugestoes.lift()
                except (Exception, psycopg2.DatabaseError) as error:
                    print(f"Erro ao buscar sugestões: {error}")
                finally:
                    conn.close()

            if not self.listbox_sugestoes.size():
                self.listbox_sugestoes.grid_remove()
        else:
            self.listbox_sugestoes.grid_remove()

    def selecionar_sugestao_aluno(self, event=None):
        """Preenche o Entry com a sugestão selecionada no Listbox."""
        if self.listbox_sugestoes.curselection():
            selecionado = self.listbox_sugestoes.get(self.listbox_sugestoes.curselection())
            self.entry_filtro_nome.delete(0, tk.END)
            self.entry_filtro_nome.insert(0, selecionado)
            self.listbox_sugestoes.grid_remove()

    def excluir_aluno_selecionado(self):
        aluno_selecionado = self.combo_alunos.get()
        if not aluno_selecionado:
            messagebox.showwarning("Seleção Necessária", "Selecione um aluno para excluir.")
            return
        aluno_id = int(aluno_selecionado.split(" - ")[0])
        nome_aluno = aluno_selecionado.split(" - ")[1]
        if messagebox.askyesno("Confirmar Exclusão", f"Deseja excluir o aluno '{nome_aluno}' e TODAS as suas notas?",
                               icon='warning'):
            conn = self.conectar_bd()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM alunos WHERE id = %s", (aluno_id,))
                    conn.commit()
                    messagebox.showinfo("Sucesso", f"Aluno '{nome_aluno}' excluído.")
                    self.carregar_alunos()
                    self.executar_consulta()
                except (Exception, psycopg2.DatabaseError) as error:
                    conn.rollback()
                    messagebox.showerror("Erro", f"Erro ao excluir aluno: {error}")
                finally:
                    conn.close()

    def excluir_registro(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Seleção Necessária", "Selecione um registro de notas para excluir.")
            return
        item = self.tree.item(selecionado[0])
        # Ajuste para garantir que os valores existam
        if len(item["values"]) < 3:  # Verifica se há pelo menos ID, Nome e Semestre
            messagebox.showerror("Erro", "Registro inválido para exclusão.")
            return

        aluno_id, nome_aluno, semestre = item["values"][0], item["values"][1], item["values"][2]

        # Garante que aluno_id e semestre são inteiros (pode ser string do Treeview)
        try:
            aluno_id = int(aluno_id)
            semestre = int(semestre)
        except ValueError:
            messagebox.showerror("Erro", "ID do aluno ou semestre inválido.")
            return

        if messagebox.askyesno("Confirmar Exclusão",
                               f"Deseja excluir as notas de '{nome_aluno}' do semestre {semestre}?", icon='warning'):
            conn = self.conectar_bd()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM notas WHERE aluno_id = %s AND semestre = %s", (aluno_id, semestre))
                    conn.commit()
                    messagebox.showinfo("Sucesso", "Registro de notas excluído.")
                    self.executar_consulta()
                except (Exception, psycopg2.DatabaseError) as error:
                    conn.rollback()
                    messagebox.showerror("Erro", f"Erro ao excluir registro: {error}")
                finally:
                    conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaNotas(root)
    root.mainloop()