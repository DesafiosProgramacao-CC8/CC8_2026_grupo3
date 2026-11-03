#Tela de amizades com menu lateral no padrão do chat.
import tkinter as tk
import threading
from conexao import ErroConexao
from componentes import BotaoArredondado, CampoArredondado
from tela_chat import PainelArredondado

CORES = {"fundo": "#FFFAF4", "verde": "#4D563D", "caramelo": "#A67C52",
         "bege": "#F0E8DD", "selecao": "#EDE2D2", "borda": "#DDD4C8",
         "texto": "#27251F", "muted": "#666057"}


class TelaAmizades(tk.Frame):
    def __init__(self, mestre, aplicacao=None):
        super().__init__(mestre, bg=CORES["fundo"])
        self.aplicacao = aplicacao
        self.ativo = False
        self.consultando = False
        self.usuarios = []
        self.amigos = []
        self.pedidos = {}
        self.respostas = []
        self.aba = "usuarios"
        self.busca = tk.StringVar()
        self.dica_busca = "Buscar usuários..."
        self.montar()

    def montar(self):
        corpo = tk.Frame(self, bg=CORES["fundo"])
        corpo.pack(fill="both", expand=True, padx=18, pady=15)

        #Coluna lateral mais larga, com abas lado a lado.
        painel_lateral = PainelArredondado(corpo, CORES["bege"], width=395)
        lateral = painel_lateral.interior
        painel_lateral.pack(side="left", fill="y", padx=(0, 14))
        painel_lateral.pack_propagate(False)
        tk.Label(lateral, text="Amigos", bg=CORES["bege"], fg=CORES["verde"],
                 font=("Helvetica Neue", 18, "bold")).pack(anchor="w", padx=16, pady=(20, 15))
        abas = tk.Frame(lateral, bg=CORES["bege"])
        abas.pack(fill="x", padx=8, pady=(0, 12))
        for coluna in range(3):
            abas.grid_columnconfigure(coluna, weight=1, uniform="abas")
        self.botoes = {}
        for coluna, (titulo, chave) in enumerate((("Usuários", "usuarios"), ("Meus amigos", "amigos"),
                              ("Solicitações", "solicitacoes"))):
            botao = BotaoArredondado(abas, titulo, lambda aba=chave: self.selecionar(aba),
                                    cor=CORES["selecao"], fundo=CORES["bege"], altura=42, width=90)
            botao.grid(row=0, column=coluna, sticky="ew", padx=3)
            self.botoes[chave] = botao

        #Busca com lupa dentro do próprio campo.
        campo_busca = CampoArredondado(lateral, variavel=self.busca, fundo=CORES["bege"], prefixo="⌕")
        campo_busca.pack(fill="x", padx=14, pady=(0, 14))
        self.campo_busca = campo_busca
        self._placeholder(campo_busca.entrada)
        self.busca.trace_add("write", lambda *_: self.atualizar())
        #Aviso de pesquisa sem correspondência, sem cartão.
        self.aviso_busca = tk.Label(lateral, text="", bg=CORES["bege"],
                                    fg=CORES["muted"], font=("Helvetica Neue", 11))
        self.aviso_busca.pack(fill="x", padx=14)

        #Painel principal de resultados.
        direita = tk.Frame(corpo, bg=CORES["fundo"])
        direita.pack(side="left", fill="both", expand=True)
        painel_cabecalho = PainelArredondado(direita, "#E9DCCB", height=105)
        painel_cabecalho.pack(fill="x", pady=(0, 12))
        painel_cabecalho.pack_propagate(False)
        cabecalho = painel_cabecalho.interior
        self.titulo = tk.Label(cabecalho, bg="#E9DCCB", fg=CORES["verde"],
                               font=("Helvetica Neue", 16, "bold"), anchor="w", padx=18)
        self.titulo.pack(fill="x", pady=(7, 2))
        self.subtitulo = tk.Label(cabecalho, bg="#E9DCCB", fg=CORES["muted"],
                                  font=("Helvetica Neue", 11), anchor="w", padx=18)
        self.subtitulo.pack(fill="x", pady=(0, 4))
        painel_resultados = PainelArredondado(direita, "#F5EFE7")
        painel_resultados.pack(fill="both", expand=True)
        self.resultados = tk.Frame(painel_resultados.interior, bg="#F5EFE7")
        self.resultados.pack(fill="both", expand=True, padx=12, pady=12)
        self.mensagem = tk.Label(direita, text="", bg=CORES["fundo"], fg=CORES["muted"],
                                 font=("Helvetica Neue", 10), wraplength=400)
        self.mensagem.pack(pady=(8, 0))
        self.selecionar("usuarios")

    def _placeholder(self, entrada):
        #Exibe a dica da aba atual sem afetar a pesquisa.
        def foco(_evento=None):
            if entrada.get() == self.dica_busca:
                entrada.delete(0, "end")
                entrada.configure(fg=CORES["texto"])

        def sair(_evento=None):
            if not entrada.get().strip():
                entrada.delete(0, "end")
                entrada.insert(0, self.dica_busca)
                entrada.configure(fg="#8B857C")

        entrada.bind("<FocusIn>", foco, add="+")
        entrada.bind("<FocusOut>", sair, add="+")
        sair()

    def selecionar(self, aba):
        if aba not in self.botoes:
            return
        self.aba = aba
        #Ajusta a dica da busca conforme a aba escolhida.
        self.dica_busca = {"usuarios": "Buscar usuários...", "amigos": "Buscar amigos...",
                           "solicitacoes": "Buscar solicitações..."}[aba]
        for chave, botao in self.botoes.items():
            botao.definir_cor(CORES["caramelo"] if chave == aba else CORES["selecao"])
        titulos = {"usuarios": ("Usuários online", "Encontre usuários conectados"),
                   "amigos": ("Meus amigos", "Seus contatos"),
                   "solicitacoes": ("Solicitações de amizade", "Pedidos recebidos")}
        self.titulo.configure(text=titulos[aba][0])
        self.subtitulo.configure(text=titulos[aba][1])
        self.busca.set("")
        self.campo_busca.entrada.delete(0, "end")
        self.campo_busca.entrada.insert(0, self.dica_busca)
        self.campo_busca.entrada.configure(fg="#8B857C")
        self.atualizar()
        if self.ativo:
            self.consultar()

    def atualizar(self):
        #Filtra somente a lista correspondente à aba selecionada.
        termo = self.busca.get().strip().lower()
        if termo == self.dica_busca.lower():
            termo = ""
        for filho in self.resultados.winfo_children():
            filho.destroy()
        if self.aba == "usuarios":
            lista = [(uid, nome, "Adicionar") for uid, nome in self.usuarios
                     if uid != self._meu_id()]
        elif self.aba == "amigos":
            lista = [(uid, nome, "Conversar") for uid, nome in self.amigos]
        else:
            lista = [(uid, nome, "Responder") for uid, nome in self.pedidos.items()]
        filtrados = [(uid, nome, acao) for uid, nome, acao in lista
                     if not termo or termo in nome.lower() or termo in str(uid)]
        self.aviso_busca.configure(text="Nenhum resultado encontrado." if termo and not filtrados else "")
        for uid, nome, acao in filtrados:
            linha = tk.Frame(self.resultados, bg="#F5EFE7")
            linha.pack(fill="x", pady=5)
            tk.Label(linha, text=f"{nome} (ID {uid})", bg="#F5EFE7", fg=CORES["texto"],
                     font=("Helvetica Neue", 11)).pack(side="left", padx=8)
            if acao == "Responder":
                self._botao(linha, "Aceitar", lambda i=uid: self.responder(i, True))
                self._botao(linha, "Recusar", lambda i=uid: self.responder(i, False))
            else:
                self._botao(linha, acao, lambda i=uid, a=acao: self.acao(i, a))

    def _botao(self, pai, texto, comando):
        botao = BotaoArredondado(pai, texto, comando, cor=CORES["caramelo"],
                                fundo="#F5EFE7", width=92, altura=34)
        botao.pack(side="right", padx=4)

    def _meu_id(self):
        return self.aplicacao.conexao.id_usuario if self.aplicacao else None

    def iniciar_consulta(self):
        if self.ativo:
            self.consultar()
            self.after(3000, self.iniciar_consulta)

    def consultar(self):
        if self.consultando or not self.ativo or not self._meu_id():
            return
        self.consultando = True
        def trabalho():
            try:
                conexao = self.aplicacao.conexao
                uid = self._meu_id()
                codigo, online = conexao.requisitar(64, uid, 0)
                codigo2, amigos = conexao.requisitar(64, uid, 1)
                if codigo != 65 or codigo2 != 65:
                    raise ErroConexao("Resposta inesperada ao listar usuários")
                avisos = conexao.retirar_avisos()
                self.after(0, lambda: self._receber(online, amigos, avisos))
            except (ErroConexao, OSError) as erro:
                self.after(0, lambda msg=str(erro): self._erro(msg))
        threading.Thread(target=trabalho, daemon=True).start()

    def _receber(self, online, amigos, avisos):
        self.consultando = False
        self.usuarios = [(int(online[i]), online[i+1]) for i in range(0, len(online), 2)]
        self.amigos = [(int(amigos[i]), amigos[i+1]) for i in range(0, len(amigos), 2)]
        nomes = dict(self.usuarios + self.amigos)
        for codigo, campos in avisos:
            uid = int(campos[0])
            if codigo == 257:
                self.pedidos[uid] = nomes.get(uid, f"Usuário {uid}")
            elif codigo == 259:
                self.mensagem.configure(text=f"Usuário {uid}: amizade " +
                    ("aceita." if campos[1] == "VERDADEIRO" else "recusada."))
        self.atualizar()

    def _erro(self, mensagem):
        self.consultando = False
        self.mensagem.configure(text=mensagem)

    def acao(self, uid, acao):
        if acao == "Conversar":
            self.aplicacao.mostrar("chat")
            self.aplicacao.tela_chat.conversas[uid] = next(
                (nome for amigo, nome in self.amigos if amigo == uid), f"Usuário {uid}")
            self.aplicacao.tela_chat.abrir_conversa(uid)
            return
        self._enviar(256, uid)

    def responder(self, uid, aceitar):
        self._enviar(258, uid, "VERDADEIRO" if aceitar else "FALSO")

    def _enviar(self, codigo, uid, resposta=None):
        #A solicitação é enviada sem esperar confirmação imediata.
        def trabalho():
            try:
                conexao = self.aplicacao.conexao
                if resposta is None:
                    conexao.enviar_sem_resposta(codigo, self._meu_id(), uid)
                else:
                    conexao.enviar_sem_resposta(codigo, self._meu_id(), uid, resposta)
                self.after(0, lambda: self._enviado(codigo, uid, resposta))
            except (ErroConexao, OSError) as erro:
                self.after(0, lambda msg=str(erro): self._erro(msg))
        threading.Thread(target=trabalho, daemon=True).start()

    def _enviado(self, codigo, uid, resposta):
        if codigo == 258:
            self.pedidos.pop(uid, None)
        self.mensagem.configure(text="Solicitação enviada ao servidor." if codigo == 256
                                 else "Resposta enviada ao servidor.")
        self.atualizar()
        self.consultar()
