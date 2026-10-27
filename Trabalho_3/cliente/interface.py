#Interface de conexão TCP do IFFARCHAT, com cores do Iffagle.
import threading
import tkinter as tk
from conexao import ConexaoTCP, ErroConexao

CORES = {
    "fundo": "#F3EFE8", "painel": "#FFFAF4", "verde": "#4D563D",
    "caramelo": "#A67C52", "hover": "#8C6C55", "borda": "#DDD4C8",
    "texto": "#27251F", "secundario": "#666057", "branco": "#FFFFFF",
}


class JanelaIFFARChat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IFFARCHAT | Cliente")
        self.geometry("720x500")
        self.minsize(550, 460)
        self.configure(bg=CORES["fundo"])
        self.conexao = ConexaoTCP()
        self.ocupado = False
        self.host = tk.StringVar(value="127.0.0.1")
        self.porta = tk.StringVar(value="42000")
        self.status = tk.StringVar(value="Desconectado")

        painel = tk.Frame(self, bg=CORES["painel"], highlightbackground=CORES["borda"], highlightthickness=1)
        painel.pack(fill="both", expand=True, padx=32, pady=28)
        tk.Frame(painel, bg=CORES["verde"], height=5).pack(fill="x")
        conteudo = tk.Frame(painel, bg=CORES["painel"], padx=44, pady=25)
        conteudo.pack(fill="both", expand=True)
        tk.Label(conteudo, text="IFFARCHAT", font=("Helvetica Neue", 30, "bold"),
                 fg=CORES["verde"], bg=CORES["painel"]).pack(pady=(0, 5))
        tk.Label(conteudo, text="CONEXÃO COM O SERVIDOR TCP", font=("Helvetica Neue", 10, "bold"),
                 fg=CORES["secundario"], bg=CORES["painel"]).pack(pady=(0, 25))
        self.campo(conteudo, "Endereço do servidor", self.host)
        self.campo(conteudo, "Porta", self.porta)

        barra = tk.Frame(conteudo, bg=CORES["painel"])
        barra.pack(fill="x", pady=(12, 14))
        self.btn_conectar = self.botao(barra, "Conectar", self.conectar)
        self.btn_ping = self.botao(barra, "Testar PING", self.ping)
        self.btn_sair = self.botao(barra, "Desconectar", self.desconectar)
        tk.Frame(conteudo, bg=CORES["borda"], height=1).pack(fill="x", pady=(4, 13))
        tk.Label(conteudo, textvariable=self.status, wraplength=510, justify="left",
                 fg=CORES["verde"], bg=CORES["painel"], font=("Helvetica Neue", 11)).pack(anchor="w")
        self.protocol("WM_DELETE_WINDOW", self.fechar)
        self.atualizar_botoes()

    def campo(self, pai, titulo, variavel):
        tk.Label(pai, text=titulo, fg=CORES["secundario"], bg=CORES["painel"],
                 font=("Helvetica Neue", 11)).pack(anchor="w", pady=(0, 5))
        tk.Entry(pai, textvariable=variavel, bg=CORES["branco"], fg=CORES["texto"],
                 insertbackground=CORES["texto"], relief="flat", highlightthickness=1,
                 highlightbackground=CORES["borda"], highlightcolor=CORES["verde"],
                 font=("Helvetica Neue", 12)).pack(fill="x", ipady=9, pady=(0, 14))

    def botao(self, pai, texto, comando):
        # Canvas evita que o macOS substitua as cores por botões cinza nativos.
        quadro = tk.Frame(pai, bg=CORES["painel"])
        quadro.pack(side="left", fill="x", expand=True, padx=4)
        botao = tk.Canvas(quadro, height=42, bg=CORES["caramelo"], highlightthickness=0,
                          cursor="hand2", takefocus=1)
        botao.pack(fill="x")
        botao.create_text(0, 0, text=texto, fill=CORES["branco"],
                          font=("Helvetica Neue", 11, "bold"), tags="titulo")
        botao.bind("<Configure>", lambda e, b=botao: b.coords("titulo", e.width / 2, e.height / 2))
        botao.bind("<Button-1>", lambda e, b=botao: comando() if b.habilitado else None)
        botao.bind("<Return>", lambda e, b=botao: comando() if b.habilitado else None)
        botao.bind("<space>", lambda e, b=botao: comando() if b.habilitado else None)
        botao.bind("<Enter>", lambda e, b=botao: b.configure(bg=CORES["hover"]) if b.habilitado else None)
        botao.bind("<Leave>", lambda e, b=botao: b.configure(bg=CORES["caramelo"]) if b.habilitado else None)
        botao.habilitado = True
        return botao

    def atualizar_botoes(self):
        conectado = self.conexao.conectado
        estados = ((self.btn_conectar, not conectado and not self.ocupado),
                   (self.btn_ping, conectado and not self.ocupado),
                   (self.btn_sair, conectado and not self.ocupado))
        for botao, ativo in estados:
            botao.habilitado = ativo
            botao.configure(bg=CORES["caramelo"] if ativo else CORES["borda"],
                            cursor="hand2" if ativo else "arrow")
            botao.itemconfigure("titulo", fill=CORES["branco"] if ativo else CORES["secundario"])

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
                pass  # Janela já encerrada.

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
