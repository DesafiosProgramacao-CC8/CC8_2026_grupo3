#Tela inicial do IFFARCHAT com navegação integrada.
import threading
import tkinter as tk
from conexao import ConexaoTCP, ErroConexao
from componentes import BotaoArredondado, CampoArredondado

CORES = {"fundo": "#F3EFE8", "painel": "#FFFAF4", "verde": "#4D563D",
         "caramelo": "#A67C52", "hover": "#8C6C55", "borda": "#DDD4C8",
         "texto": "#27251F", "secundario": "#666057", "branco": "#FFFFFF"}


class JanelaIFFARChat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IFFARCHAT | Cliente")
        self.geometry("780x600")
        self.minsize(650, 540)
        self.configure(bg=CORES["fundo"])
        self.conexao = ConexaoTCP()
        self.ocupado = False
        self.host = tk.StringVar(value="127.0.0.1")
        self.porta = tk.StringVar(value="42000")
        self.status = tk.StringVar(value="Desconectado")

        painel = tk.Frame(self, bg=CORES["painel"], highlightbackground=CORES["borda"], highlightthickness=1)
        painel.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Frame(painel, bg=CORES["verde"], height=5).pack(fill="x")

        topo = tk.Frame(painel, bg=CORES["painel"])
        topo.pack(fill="x", padx=25, pady=(16, 0))
        for texto, acao in (("Sair", self.fechar),
                            ("Login", lambda: self.mostrar("login")),
                            ("Cadastro", lambda: self.mostrar("cadastro")),
                            ("Conexão", lambda: self.mostrar("conexao"))):
            link = tk.Label(topo, text=texto, fg=CORES["verde"], bg=CORES["painel"],
                            font=("Helvetica Neue", 11, "bold"), cursor="hand2", padx=10)
            link.pack(side="right")
            link.bind("<Button-1>", lambda evento, funcao=acao: funcao())
        self.area = tk.Frame(painel, bg=CORES["painel"])
        self.area.pack(fill="both", expand=True)
        # Telas sobrepostas em uma única célula: alternar não recalcula o pack.
        self.area.grid_rowconfigure(0, weight=1)
        self.area.grid_columnconfigure(0, weight=1)
        self.tela_acesso = None
        self.tela_chat = None

        # Centraliza o formulário sem altura fixa, evitando cortar botões.
        self.tela_conexao = tk.Frame(self.area, bg=CORES["painel"])
        self.tela_conexao.grid(row=0, column=0, sticky="nsew")
        centro = tk.Frame(self.tela_conexao, bg=CORES["painel"], width=540, height=390)
        centro.place(relx=0.5, rely=0.53, anchor="center")
        centro.pack_propagate(False)
        tk.Label(centro, text="IFFARCHAT", fg=CORES["verde"], bg=CORES["painel"],
                 font=("Helvetica Neue", 32, "bold")).pack(pady=(8, 4))
        tk.Label(centro, text="CONEXÃO COM O SERVIDOR TCP", fg=CORES["secundario"],
                 bg=CORES["painel"], font=("Helvetica Neue", 10, "bold")).pack(pady=(0, 37))
        self.campo(centro, "Endereço do servidor", self.host)
        self.campo(centro, "Porta", self.porta)
        barra = tk.Frame(centro, bg=CORES["painel"])
        barra.pack(fill="x", pady=(16, 18))
        self.btn_conectar = self.botao(barra, "Conectar", self.conectar)
        self.btn_ping = self.botao(barra, "Testar PING", self.ping)
        self.btn_sair = self.botao(barra, "Desconectar", self.desconectar)
        tk.Frame(centro, bg=CORES["borda"], height=1).pack(fill="x", pady=(2, 15))
        linha_status = tk.Frame(centro, bg=CORES["painel"])
        linha_status.pack(fill="x")
        self.indicador = tk.Canvas(linha_status, width=16, height=16, bg=CORES["painel"], highlightthickness=0)
        self.indicador.pack(side="left", padx=(0, 9))
        self.bolinha = self.indicador.create_oval(2, 2, 14, 14, fill="#C84A48", outline="")
        tk.Label(linha_status, textvariable=self.status, fg=CORES["verde"], bg=CORES["painel"],
                 font=("Helvetica Neue", 11), anchor="w", justify="left", wraplength=470).pack(side="left", fill="x", expand=True)
        # A prévia do chat não altera a conexão TCP nem exige autenticação.
        self.painel = painel
        self.atalho_chat = tk.Label(topo, text="Prévia do chat", fg=CORES["verde"],
                                    bg=CORES["painel"], cursor="hand2",
                                    font=("Helvetica Neue", 11, "bold"), padx=10)
        self.atalho_chat.pack(side="left")
        self.atalho_chat.bind("<Button-1>", lambda _: self.mostrar("chat"))
        self.protocol("WM_DELETE_WINDOW", self.fechar)
        self.atualizar_botoes()

    def mostrar(self, modo):
        """Troca apenas a tela visível, preservando a conexão TCP."""
        if modo == "conexao":
            destino = self.tela_conexao
        elif modo == "chat":
            if self.tela_chat is None:
                from tela_chat import TelaChat
                self.tela_chat = TelaChat(self.area, lambda: self.mostrar("conexao"))
                self.tela_chat.grid(row=0, column=0, sticky="nsew")
            destino = self.tela_chat
        elif modo in ("login", "cadastro"):
            if self.tela_acesso is None:
                from telas_acesso import TelaAcesso
                self.tela_acesso = TelaAcesso(self.area, self.mostrar)
                self.tela_acesso.grid(row=0, column=0, sticky="nsew")
            destino = self.tela_acesso
            destino.mostrar(modo)
        else:
            return
        destino.tkraise()

    def campo(self, pai, titulo, variavel):
        tk.Label(pai, text=titulo, fg=CORES["secundario"], bg=CORES["painel"],
                 font=("Helvetica Neue", 11)).pack(anchor="w", pady=(0, 5))
        CampoArredondado(pai, variavel=variavel, fundo=CORES["painel"]).pack(
            fill="x", pady=(0, 15))

    def botao(self, pai, texto, comando):
        quadro = tk.Frame(pai, bg=CORES["painel"])
        quadro.pack(side="left", fill="x", expand=True, padx=4)
        botao = BotaoArredondado(quadro, texto, comando, fundo=CORES["painel"])
        botao.pack(fill="x")
        return botao

    def atualizar_botoes(self):
        conectado = self.conexao.conectado
        estados = ((self.btn_conectar, not conectado and not self.ocupado),
                   (self.btn_ping, conectado and not self.ocupado),
                   (self.btn_sair, conectado and not self.ocupado))
        for botao, ativo in estados:
            botao.habilitado = ativo
            botao.desenhar()
        self.indicador.itemconfigure(self.bolinha, fill="#458453" if conectado else "#C84A48")

    def executar(self, tarefa, sucesso):
        if self.ocupado:
            return
        self.ocupado = True
        self.status.set("Aguardando resposta do servidor...")
        self.atualizar_botoes()

        def trabalho():
            try:
                tarefa()
                resultado = sucesso
            except (ErroConexao, OSError) as erro:
                resultado = f"Falha: {erro}"
            try:
                self.after(0, lambda: self.finalizar(resultado))
            except RuntimeError:
                pass
        threading.Thread(target=trabalho, daemon=True).start()

    def finalizar(self, resultado):
        self.ocupado = False
        self.status.set(resultado)
        self.atualizar_botoes()

    def conectar(self):
        host = self.host.get().strip()
        try:
            porta = int(self.porta.get())
            if not host or not 1 <= porta <= 65535:
                raise ValueError
        except ValueError:
            self.status.set("Informe endereço e porta válidos (1 a 65535).")
            return
        self.executar(lambda: self.conexao.conectar(host, porta),
                      "Conectado: servidor respondeu CONECTADO (3).")

    def ping(self):
        self.executar(self.conexao.ping, "PONG (5) recebido: servidor disponível.")

    def desconectar(self):
        self.conexao.desconectar()
        self.status.set("Desconectado. Socket encerrado.")
        self.atualizar_botoes()

    def fechar(self):
        if not self.ocupado:
            self.conexao.desconectar()
        self.destroy()
