#Formulários de login e cadastro do IFFARCHAT (somente interface, sem envio).

import re
import tkinter as tk
from datetime import date, datetime

CORES = {"fundo": "#F3EFE8", "painel": "#FFFAF4", "verde": "#4D563D",
         "caramelo": "#A67C52", "borda": "#DDD4C8", "texto": "#27251F",
         "secundario": "#666057", "branco": "#FFFFFF"}


def validar_cadastro(nome, apelido, nascimento, senha, confirmacao):
    if not nome.strip() or not apelido.strip():
        return "Informe nome completo e apelido."
    if any(c in nome + apelido for c in "|#\n\r"):
        return "Nome e apelido não podem conter |, # ou quebra de linha."
    try:
        data = datetime.strptime(nascimento, "%d/%m/%Y").date()
        if data.strftime("%d/%m/%Y") != nascimento or data > date.today():
            raise ValueError
    except ValueError:
        return "Informe uma data válida no formato DD/MM/AAAA."
    if not re.fullmatch(r"[A-Za-z0-9]{6}", senha):
        return "A senha deve ter exatamente 6 caracteres alfanuméricos."
    if senha != confirmacao:
        return "As senhas informadas não coincidem."
    return None


def validar_login(apelido, senha):
    if not apelido.strip() or not senha:
        return "Informe apelido e senha."
    if any(c in apelido for c in "|#\n\r"):
        return "O apelido contém caracteres não permitidos."
    if not re.fullmatch(r"[A-Za-z0-9]{6}", senha):
        return "A senha deve ter exatamente 6 caracteres alfanuméricos."
    return None


class TelaAcesso(tk.Frame):
    def __init__(self, mestre, navegar):
        super().__init__(mestre, bg=CORES["painel"])
        self.navegar = navegar
        self.modo = "login"
        self.campos = {}
        self.mensagem = tk.StringVar()
        self.canvas = tk.Canvas(self, bg=CORES["painel"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.area = tk.Frame(self.canvas, bg=CORES["painel"])
        self.item = self.canvas.create_window(0, 0, window=self.area, anchor="n")
        self.canvas.bind("<Configure>", self.ajustar)
        self.area.bind("<Configure>", self.ajustar)

    def ajustar(self, _evento=None):
        largura = max(1, self.canvas.winfo_width())
        altura = self.area.winfo_reqheight()
        self.canvas.itemconfigure(self.item, width=min(480, max(250, largura - 30)))
        self.canvas.coords(self.item, largura / 2, max(12, (self.canvas.winfo_height() - altura) / 2))
        self.canvas.configure(scrollregion=(0, 0, largura, max(altura + 24, self.canvas.winfo_height())))

    def mostrar(self, modo):
        self.modo = modo
        self.renderizar()

    def renderizar(self):
        for filho in self.area.winfo_children():
            filho.destroy()
        self.campos = {}
        corpo = tk.Frame(self.area, bg=CORES["painel"], padx=22, pady=12)
        corpo.pack(fill="both", expand=True)
        tk.Frame(corpo, bg=CORES["verde"], height=5).pack(fill="x", pady=(0, 12))
        tk.Label(corpo, text="IFFARCHAT", fg=CORES["verde"], bg=CORES["painel"],
                 font=("Helvetica Neue", 25, "bold"), cursor="hand2").pack(pady=(0, 2))
        tk.Label(corpo, text="CRIAR UMA CONTA" if self.modo == "cadastro" else "ENTRAR NA CONTA",
                 fg=CORES["secundario"], bg=CORES["painel"],
                 font=("Helvetica Neue", 10, "bold")).pack(pady=(0, 12))
        campos = ([('Nome completo', 'nome', False)] if self.modo == 'cadastro' else [])
        campos += [('Apelido', 'apelido', False)]
        if self.modo == 'cadastro':
            campos.append(('Data de nascimento (DD/MM/AAAA)', 'nascimento', False))
        campos.append(('Senha (6 caracteres alfanuméricos)', 'senha', True))
        if self.modo == 'cadastro':
            campos.append(('Confirmar senha', 'confirmacao', True))
        for titulo, chave, segredo in campos:
            tk.Label(corpo, text=titulo, fg=CORES["secundario"], bg=CORES["painel"],
                     font=("Helvetica Neue", 10)).pack(anchor="w", pady=(0, 3))
            entrada = tk.Entry(corpo, show="•" if segredo else "", font=("Helvetica Neue", 11),
                               bg=CORES["branco"], fg=CORES["texto"], relief="flat",
                               highlightthickness=1, highlightbackground=CORES["borda"])
            entrada.pack(fill="x", ipady=6, pady=(0, 9))
            self.campos[chave] = entrada
        self.botao(corpo, "Criar conta" if self.modo == "cadastro" else "Entrar", self.validar, CORES["caramelo"])
        self.botao(corpo, "Voltar ao login" if self.modo == "cadastro" else "Criar uma conta",
                   lambda: self.mostrar("login" if self.modo == "cadastro" else "cadastro"), CORES["verde"])
        self.mensagem.set("Prévia da interface: envio ao servidor ainda não integrado.")
        tk.Label(corpo, textvariable=self.mensagem, bg=CORES["painel"], fg=CORES["secundario"],
                 wraplength=390, justify="center", font=("Helvetica Neue", 10)).pack(fill="x", pady=(10, 0))
        self.after_idle(self.ajustar)

    def botao(self, pai, texto, comando, cor):
        rotulo = tk.Label(pai, text=texto, fg=CORES["branco"], bg=cor,
                          font=("Helvetica Neue", 11, "bold"), pady=10,
                          cursor="hand2", takefocus=1)
        rotulo.pack(fill="x", pady=(5, 0))
        for evento in ("<Button-1>", "<Return>", "<space>"):
            rotulo.bind(evento, lambda e: comando())

    def validar(self):
        dados = {chave: entrada.get() for chave, entrada in self.campos.items()}
        if self.modo == "login":
            erro = validar_login(dados["apelido"], dados["senha"])
        else:
            erro = validar_cadastro(dados["nome"], dados["apelido"], dados["nascimento"],
                                    dados["senha"], dados["confirmacao"])
        self.mensagem.set(erro or "Dados válidos. Cadastro e login serão integrados posteriormente.")
