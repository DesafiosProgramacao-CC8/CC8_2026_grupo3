# Telas de cadastro e login, sem comunicação com o servidor nesta etapa.
import re
import tkinter as tk
from datetime import date, datetime
from hash_senha import gerar_hash_senha
from protocolo_cliente import criar_mensagem
from componentes import BotaoArredondado, CampoArredondado

CORES = {"fundo": "#F3EFE8", "painel": "#FFFAF4", "verde": "#4D563D",
         "caramelo": "#A67C52", "borda": "#DDD4C8", "texto": "#27251F",
         "secundario": "#666057", "branco": "#FFFFFF"}


def formatar_nascimento(valor):
    """Insere barras em DD/MM/AAAA, aceitando digitação com ou sem barras."""
    numeros = re.sub(r"\D", "", valor)[:8]
    if len(numeros) > 4:
        return f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}"
    if len(numeros) > 2:
        return f"{numeros[:2]}/{numeros[2:]}"
    return numeros


def validar_cadastro(nome, apelido, nascimento, senha, confirmacao):
    if not nome.strip() or not apelido.strip():
        return "Informe nome completo e apelido."
    if any(c in nome + apelido for c in "|#\n\r"):
        return "Nome e apelido não podem conter |, # ou quebra de linha."
    nascimento = formatar_nascimento(nascimento)
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
            campo = CampoArredondado(corpo, senha=segredo, fundo=CORES["painel"])
            campo.pack(fill="x", pady=(0, 9))
            entrada = campo.entrada
            if chave == "nascimento":
                entrada.bind("<KeyPress>", lambda evento: self.tecla_data(evento))
                entrada.bind("<<Paste>>", lambda evento: self.after(10, self.ajustar_data_colada, evento.widget))
            self.campos[chave] = entrada
        self.botao(corpo, "Criar conta" if self.modo == "cadastro" else "Entrar", self.validar, CORES["caramelo"])
        if self.modo == "login":
            self.botao(corpo, "Criar uma conta", lambda: self.mostrar("cadastro"), CORES["verde"])
        self.mensagem.set("Prévia da interface: envio ao servidor ainda não integrado.")
        tk.Label(corpo, textvariable=self.mensagem, bg=CORES["painel"], fg=CORES["secundario"],
                 wraplength=390, justify="center", font=("Helvetica Neue", 10)).pack(fill="x", pady=(10, 0))
        self.after_idle(self.ajustar)

    def tecla_data(self, evento):
        entrada = evento.widget
        tecla = evento.keysym
        if tecla in ("Tab", "ISO_Left_Tab", "Left", "Right", "Home", "End"):
            return None
        if evento.state & 0x4 and tecla.lower() in ("a", "c", "v", "x"):
            return None  # Atalhos do teclado, inclusive colar.
        atual = entrada.get()
        digitos = re.sub(r"\D", "", atual)[:8]
        pos = len(re.sub(r"\D", "", atual[:entrada.index(tk.INSERT)]))
        selecao = entrada.selection_present()
        if selecao:
            inicio = len(re.sub(r"\D", "", atual[:entrada.index(tk.SEL_FIRST)]))
            fim = len(re.sub(r"\D", "", atual[:entrada.index(tk.SEL_LAST)]))
            digitos = digitos[:inicio] + digitos[fim:]
            pos = inicio
        if evento.char.isascii() and evento.char.isdigit():
            if len(digitos) >= 8:
                return "break"
            digitos = digitos[:pos] + evento.char + digitos[pos:]
            pos += 1
        elif tecla == "BackSpace":
            if not selecao and pos > 0:
                digitos = digitos[:pos - 1] + digitos[pos:]
                pos -= 1
        elif tecla == "Delete":
            if not selecao:
                digitos = digitos[:pos] + digitos[pos + 1:]
        else:
            return "break"
        formatado = formatar_nascimento(digitos)
        entrada.delete(0, tk.END)
        entrada.insert(0, formatado)
        indice = 0
        vistos = 0
        while indice < len(formatado) and vistos < pos:
            if formatado[indice].isdigit():
                vistos += 1
            indice += 1
        if indice < len(formatado) and formatado[indice] == "/":
            indice += 1
        entrada.icursor(indice)
        return "break"

    def ajustar_data_colada(self, entrada):
        texto = formatar_nascimento(entrada.get())
        entrada.delete(0, tk.END)
        entrada.insert(0, texto)
        entrada.icursor(tk.END)

    def botao(self, pai, texto, comando, cor):
        botao = BotaoArredondado(pai, texto, comando, cor=cor,
                                 fundo=CORES["painel"])
        botao.pack(fill="x", pady=(5, 0))

    def validar(self):
        dados = {chave: entrada.get() for chave, entrada in self.campos.items()}
        if self.modo == "login":
            erro = validar_login(dados["apelido"], dados["senha"])
        else:
            erro = validar_cadastro(dados["nome"], dados["apelido"], dados["nascimento"],
                                    dados["senha"], dados["confirmacao"])
        if erro:
            self.mensagem.set(erro)
            return

        # A senha é codificada no cliente, antes de qualquer envio à rede.
        # Neste commit apenas preparamos o comando; não o transmitimos.
        try:
            senha_hash = gerar_hash_senha(dados["senha"])
            if self.modo == "login":
                comando = criar_mensagem(16, dados["apelido"], senha_hash)
            else:
                comando = criar_mensagem(8, dados["nome"], dados["apelido"],
                                         formatar_nascimento(dados["nascimento"]), senha_hash)
        except ValueError as erro_hash:
            self.mensagem.set(str(erro_hash))
            return

        # Não exibir nem registrar senha ou hash em logs.
        self.mensagem.set("Dados validados e senha codificada. "
                          "Comando preparado localmente; envio ainda não integrado.")
