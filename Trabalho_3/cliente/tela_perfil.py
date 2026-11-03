#Tela de perfil do IFFARCHAT.
import tkinter as tk
import threading
from datetime import datetime, date
from conexao import ErroConexao
from hash_senha import gerar_hash_senha
from componentes import BotaoArredondado, CampoArredondado
from telas_acesso import formatar_nascimento

CORES = {"fundo": "#FFFAF4", "verde": "#4D563D", "caramelo": "#A67C52",
         "texto": "#27251F", "secundario": "#666057"}


class TelaPerfil(tk.Frame):
    def __init__(self, mestre, aplicacao=None):
        super().__init__(mestre, bg=CORES["fundo"])
        self.aplicacao = aplicacao
        self.ocupado = False
        self.campos = {}
        self.aviso = tk.StringVar(value="")
        #Centraliza o formulário como no Cadastro, sem cortar o título.
        self.canvas = tk.Canvas(self, bg=CORES["fundo"], highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.area = tk.Frame(self.canvas, bg=CORES["fundo"])
        self.item = self.canvas.create_window(0, 0, window=self.area, anchor="n")
        self.canvas.bind("<Configure>", self.ajustar)
        self.area.bind("<Configure>", self.ajustar)
        quadro = tk.Frame(self.area, bg=CORES["fundo"], padx=22, pady=6)
        quadro.pack(fill="both", expand=True)
        #Linha verde acima do título, no padrão do Cadastro.
        tk.Frame(quadro, bg=CORES["verde"], height=5).pack(fill="x", pady=(0, 12))
        tk.Label(quadro, text="Meu perfil", fg=CORES["verde"], bg=CORES["fundo"],
                 font=("Helvetica Neue", 25, "bold")).pack(pady=(0, 2))
        tk.Label(quadro, text="Visualização e edição dos dados da conta",
                 fg=CORES["secundario"], bg=CORES["fundo"]).pack(pady=(0, 8))
        for titulo, chave in (("Nome completo", "nome"), ("Apelido", "apelido"),
                              ("Data de nascimento", "nascimento"), ("Senha atual", "senha")):
            tk.Label(quadro, text=titulo, fg=CORES["secundario"], bg=CORES["fundo"],
                     anchor="w").pack(fill="x", pady=(4, 2))
            campo = CampoArredondado(quadro, fundo=CORES["fundo"], senha=chave == "senha",
                                     somente_leitura=chave == "apelido")
            campo.pack(fill="x")
            self.campos[chave] = campo.entrada
        tk.Label(quadro, text="Informe a data de nascimento para salvar. O servidor informa apenas a idade.",
                 fg=CORES["secundario"], bg=CORES["fundo"], wraplength=400).pack(pady=(7, 9))
        botao = BotaoArredondado(quadro, "Salvar alterações", self.salvar,
                                fundo=CORES["fundo"], cor=CORES["caramelo"])
        botao.pack(fill="x")
        tk.Label(quadro, textvariable=self.aviso, fg=CORES["secundario"],
                 bg=CORES["fundo"], wraplength=400, justify="center").pack(pady=(8, 0))

    def ajustar(self, _evento=None):
        #Mantém o formulário centralizado e o topo sempre visível.
        largura = max(1, self.canvas.winfo_width())
        altura = self.area.winfo_reqheight()
        self.canvas.itemconfigure(self.item, width=min(480, max(250, largura - 30)))
        self.canvas.coords(self.item, largura / 2, max(12, (self.canvas.winfo_height() - altura) / 2))

    def _executar(self, tarefa, concluir):
        if self.ocupado:
            return
        self.ocupado = True
        def trabalho():
            try:
                resultado = tarefa()
                self.after(0, lambda: concluir(resultado, None))
            except (ErroConexao, OSError, ValueError) as erro:
                self.after(0, lambda msg=str(erro): concluir(None, msg))
        threading.Thread(target=trabalho, daemon=True).start()

    def carregar(self):
        if not self.aplicacao or not self.aplicacao.conexao.id_usuario:
            return
        self.aviso.set("Consultando perfil...")
        uid = self.aplicacao.conexao.id_usuario
        def tarefa():
            codigo, campos = self.aplicacao.conexao.requisitar(8192, uid)
            if codigo != 8193 or len(campos) != 4:
                raise ErroConexao("Resposta de perfil inválida")
            return campos
        def concluir(campos, erro):
            self.ocupado = False
            if erro:
                self.aviso.set(erro)
                return
            self.campos["nome"].delete(0, "end")
            self.campos["nome"].insert(0, campos[1])
            self.campos["apelido"].delete(0, "end")
            self.campos["apelido"].insert(0, campos[2])
            self.aviso.set(f"Idade: {campos[3]} anos. Para alterar os dados, informe a data de nascimento e a senha atual.")
        self._executar(tarefa, concluir)

    def salvar(self):
        if not self.aplicacao or not self.aplicacao.conexao.id_usuario:
            self.aviso.set("Faça login para atualizar o perfil.")
            return
        nome = self.campos["nome"].get().strip()
        nascimento = formatar_nascimento(self.campos["nascimento"].get())
        senha = self.campos["senha"].get()
        try:
            data = datetime.strptime(nascimento, "%d/%m/%Y").date()
            if data.strftime("%d/%m/%Y") != nascimento or data > date.today():
                raise ValueError
        except ValueError:
            self.aviso.set("Informe uma data válida no formato DD/MM/AAAA.")
            return
        if not nome or any(c in nome for c in "|#\n\r"):
            self.aviso.set("Informe um nome válido.")
            return
        if len(senha) != 6 or not senha.isascii() or not senha.isalnum():
            self.aviso.set("A senha atual deve ter 6 caracteres alfanuméricos.")
            return
        uid = self.aplicacao.conexao.id_usuario
        self.aviso.set("Salvando alterações...")
        def tarefa():
            codigo, _ = self.aplicacao.conexao.requisitar(
                16384, uid, nome, nascimento, gerar_hash_senha(senha))
            if codigo != 16385:
                raise ErroConexao("Resposta inesperada ao atualizar perfil")
            return True
        def concluir(_resultado, erro):
            self.ocupado = False
            self.campos["senha"].delete(0, "end")
            self.aviso.set(erro if erro else "Perfil atualizado com sucesso.")
        self._executar(tarefa, concluir)
