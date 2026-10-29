#Tela de amizades com menu lateral no padrão do chat.
import tkinter as tk
from componentes import BotaoArredondado, CampoArredondado
from tela_chat import PainelArredondado

CORES = {"fundo": "#FFFAF4", "verde": "#4D563D", "caramelo": "#A67C52",
         "bege": "#F0E8DD", "selecao": "#EDE2D2", "borda": "#DDD4C8",
         "texto": "#27251F", "muted": "#666057"}


class TelaAmizades(tk.Frame):
    def __init__(self, mestre):
        super().__init__(mestre, bg=CORES["fundo"])
        self.aba = "usuarios"
        self.busca = tk.StringVar()
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
        self._placeholder(campo_busca.entrada, "Buscar amigos...")
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
        resultados = painel_resultados.interior
        self.conteudo = tk.Label(resultados, bg="#F5EFE7", fg=CORES["muted"],
                                 font=("Helvetica Neue", 12), justify="center")
        self.conteudo.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(direita, text="Prévia local: dados de amizades ainda não integrados.",
                 bg=CORES["fundo"], fg=CORES["muted"],
                 font=("Helvetica Neue", 10)).pack(pady=(12, 0))
        self.selecionar("usuarios")

    def _placeholder(self, entrada, texto):
        #Exibe a dica no campo sem afetar a pesquisa.
        def foco(_evento=None):
            if entrada.get() == texto:
                entrada.delete(0, "end")
                entrada.configure(fg=CORES["texto"])

        def sair(_evento=None):
            if not entrada.get().strip():
                entrada.delete(0, "end")
                entrada.insert(0, texto)
                entrada.configure(fg="#8B857C")

        entrada.bind("<FocusIn>", foco, add="+")
        entrada.bind("<FocusOut>", sair, add="+")
        sair()

    def selecionar(self, aba):
        if aba not in self.botoes:
            return
        self.aba = aba
        for chave, botao in self.botoes.items():
            botao.definir_cor(CORES["caramelo"] if chave == aba else CORES["selecao"])
        titulos = {"usuarios": ("Usuários online", "Encontre usuários conectados"),
                   "amigos": ("Meus amigos", "Seus contatos"),
                   "solicitacoes": ("Solicitações de amizade", "Pedidos recebidos")}
        self.titulo.configure(text=titulos[aba][0])
        self.subtitulo.configure(text=titulos[aba][1])
        self.busca.set("")
        self.campo_busca.entrada.delete(0, "end")
        self.campo_busca.entrada.insert(0, "Buscar amigos...")
        self.campo_busca.entrada.configure(fg="#8B857C")
        self.atualizar()

    def atualizar(self):
        #As listas reais serão carregadas após a integração.
        mensagens = {"usuarios": "Nenhum usuário carregado.",
                     "amigos": "Nenhum amigo carregado.",
                     "solicitacoes": "Nenhuma solicitação carregada."}
        #Exibe o aviso somente se houver pesquisa real sem resultados.
        termo = self.busca.get().strip()
        if termo == "Buscar amigos...":
            termo = ""
        self.aviso_busca.configure(text="Nenhum resultado encontrado." if termo else "")
        self.conteudo.configure(text=mensagens[self.aba] + "\nAguardando integração com o servidor.")
