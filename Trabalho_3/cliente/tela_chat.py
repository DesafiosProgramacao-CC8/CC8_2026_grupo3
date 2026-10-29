#Interface do chat geral e privado, em modo de prévia local.
import tkinter as tk
from protocolo_cliente import criar_mensagem
from componentes import BotaoArredondado, CampoArredondado

CORES = {"fundo": "#F3EFE8", "painel": "#FFFAF4", "verde": "#4D563D",
         "caramelo": "#A67C52", "hover": "#8C6C55", "borda": "#DDD4C8",
         "texto": "#27251F", "secundario": "#666057", "branco": "#FFFFFF",
         "areia": "#F0EBE3", "selecao": "#E8DDCB", "cabecalho": "#E4E3D8"}


class PainelArredondado(tk.Frame):
    #Desenha um painel de cantos arredondados sem bordas pretas.
    def __init__(self, mestre, cor, raio=16, margem=12, **kwargs):
        super().__init__(mestre, bg=CORES["painel"], **kwargs)
        self.cor, self.raio, self.margem = cor, raio, margem
        self.fundo = tk.Canvas(self, bg=CORES["painel"], highlightthickness=0, bd=0)
        self.fundo.pack(fill="both", expand=True)
        self.interior = tk.Frame(self.fundo, bg=cor)
        self.janela = self.fundo.create_window(margem, margem, anchor="nw", window=self.interior)
        self.fundo.bind("<Configure>", self.redesenhar)

    def redesenhar(self, evento):
        largura, altura = evento.width, evento.height
        r = min(self.raio, largura // 2, altura // 2)
        self.fundo.delete("fundo")
        pontos = [r, 0, largura-r, 0, largura, 0, largura, r,
                  largura, altura-r, largura, altura, largura-r, altura,
                  r, altura, 0, altura, 0, altura-r, 0, r, 0, 0]
        self.fundo.create_polygon(pontos, smooth=True, splinesteps=16,
                                  fill=self.cor, outline="", tags="fundo")
        self.fundo.tag_lower("fundo")
        self.fundo.coords(self.janela, self.margem, self.margem)
        self.fundo.itemconfigure(self.janela, width=max(1, largura-2*self.margem),
                                height=max(1, altura-2*self.margem))


class TelaChat(tk.Frame):
    def __init__(self, mestre, voltar):
        super().__init__(mestre, bg=CORES["painel"])
        self.voltar = voltar
        self.tipo = "geral"
        self.remetente = tk.StringVar()
        self.destinatario = tk.StringVar()
        self.busca = tk.StringVar()
        self.aviso = tk.StringVar(value="Prévia local: mensagens não são enviadas ao servidor.")
        self.montar()

    def botao(self, pai, texto, comando, cor=None):
        return BotaoArredondado(pai, texto, comando, cor=cor or CORES["caramelo"],
                                 fundo=CORES["areia"], width=94)

    def montar(self):
        #A navegação superior pertence ao interface.py.
        corpo = tk.Frame(self, bg=CORES["painel"])
        corpo.pack(fill="both", expand=True, padx=14, pady=(8, 10))
        painel_lateral = PainelArredondado(corpo, CORES["areia"], width=240)
        painel_lateral.pack(side="left", fill="y", padx=(0, 12))
        painel_lateral.pack_propagate(False)
        lateral = painel_lateral.interior
        tk.Label(lateral, text="Conversas", bg=CORES["areia"], fg=CORES["verde"],
                 font=("Helvetica Neue", 16, "bold")).pack(anchor="w", padx=14, pady=(16, 12))

        abas = tk.Frame(lateral, bg=CORES["areia"])
        abas.pack(fill="x", padx=10, pady=(0, 10))
        self.aba_geral = self.botao(abas, "Geral", lambda: self.selecionar("geral"))
        self.aba_privada = self.botao(abas, "Privada", lambda: self.selecionar("privada"), CORES["selecao"])
        self.aba_geral.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.aba_privada.pack(side="left", fill="x", expand=True, padx=(4, 0))

        busca_container = tk.Frame(lateral, bg=CORES["areia"])
        busca_container.pack(fill="x", padx=10, pady=(0, 10))
        campo_busca = CampoArredondado(busca_container, variavel=self.busca,
                                       fundo=CORES["areia"], prefixo="🔍")
        campo_busca.pack(fill="x", expand=True)
        self.campo_busca = campo_busca.entrada
        self.busca.trace_add("write", lambda *_: self.atualizar_lista())
        self.item_lista = tk.Label(lateral, text="", bg=CORES["selecao"], fg=CORES["texto"],
                                   font=("Helvetica Neue", 11, "bold"), justify="left",
                                   anchor="w", padx=12, pady=13, cursor="hand2")
        self.item_lista.pack(fill="x", padx=10)
        self.item_lista.bind("<Button-1>", lambda _: self.abrir_item())

        principal = tk.Frame(corpo, bg=CORES["painel"])
        principal.pack(side="left", fill="both", expand=True)
        painel_cabecalho = PainelArredondado(principal, CORES["cabecalho"], margem=14, height=78)
        painel_cabecalho.pack(fill="x", pady=(0, 10))
        painel_cabecalho.pack_propagate(False)
        cabecalho = painel_cabecalho.interior
        self.titulo = tk.Label(cabecalho, text="Conversa geral", bg=CORES["cabecalho"],
                               fg=CORES["verde"], font=("Helvetica Neue", 15, "bold"))
        self.titulo.pack(anchor="w")
        self.subtitulo = tk.Label(cabecalho, text="Todos os usuários", bg=CORES["cabecalho"],
                                  fg=CORES["secundario"], font=("Helvetica Neue", 10))
        self.subtitulo.pack(anchor="w", pady=(3, 0))
        #Área de mensagens com fundo suave e cantos arredondados.
        painel_mensagens = PainelArredondado(principal, CORES["areia"], margem=14)
        painel_mensagens.pack(fill="both", expand=True)
        self.area_mensagens = tk.Text(
            painel_mensagens.interior, bg=CORES["areia"], fg=CORES["texto"],
            relief="flat", bd=0, highlightthickness=0, wrap="word",
            font=("Helvetica Neue", 11), padx=12, pady=12,
            insertbackground=CORES["texto"]
        )
        self.area_mensagens.pack(fill="both", expand=True)
        self.area_mensagens.insert("end", "\nNenhuma mensagem carregada.\nA comunicação será integrada posteriormente.")
        self.area_mensagens.configure(state="disabled")

        rodape = tk.Frame(principal, bg=CORES["painel"], pady=10)
        rodape.pack(fill="x")
        ids = tk.Frame(rodape, bg=CORES["painel"])
        ids.pack(fill="x", pady=(0, 8))
        tk.Label(ids, text="Meu ID:", bg=CORES["painel"], fg=CORES["secundario"]).pack(side="left")
        campo_id = CampoArredondado(ids, variavel=self.remetente, fundo=CORES["painel"])
        campo_id.pack(side="left", padx=(8, 15), ipadx=0)
        campo_id.configure(width=110)
        self.label_destino = tk.Label(ids, text="ID destinatário:", bg=CORES["painel"], fg=CORES["secundario"])
        self.campo_destino = CampoArredondado(ids, variavel=self.destinatario,
                                               fundo=CORES["painel"])
        self.campo_destino.configure(width=110)
        linha = tk.Frame(rodape, bg=CORES["painel"])
        linha.pack(fill="x")
        campo_mensagem = CampoArredondado(linha, fundo=CORES["painel"])
        campo_mensagem.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entrada = campo_mensagem.entrada
        self.botao(linha, "Enviar", self.preparar).pack(side="right", padx=(0, 2))
        tk.Label(self, textvariable=self.aviso, bg=CORES["painel"], fg=CORES["secundario"],
                 font=("Helvetica Neue", 10), wraplength=650).pack(pady=(0, 8))
        self.selecionar("geral")

    def atualizar_lista(self):
        #A busca filtra apenas a categoria selecionada.
        nome = "Conversa geral" if self.tipo == "geral" else "Conversa privada"
        termo = self.busca.get().strip().lower()
        if termo and termo not in nome.lower():
            self.item_lista.configure(text="Nenhuma conversa encontrada.", cursor="arrow")
        else:
            self.item_lista.configure(text=nome, cursor="hand2")

    def abrir_item(self):
        self.selecionar(self.tipo)

    def selecionar(self, tipo):
        #Atualiza as abas sem recriar a janela.
        self.tipo = tipo
        for item, selecionado in ((self.aba_geral, tipo == "geral"), (self.aba_privada, tipo == "privada")):
            item.definir_cor(CORES["caramelo"] if selecionado else CORES["selecao"])
        self.titulo.configure(text="Conversa geral" if tipo == "geral" else "Conversa privada")
        self.subtitulo.configure(text="Todos os usuários" if tipo == "geral" else "Conversa individual")
        if tipo == "privada":
            self.label_destino.pack(side="left")
            self.campo_destino.pack(side="left", padx=8)
        else:
            self.label_destino.pack_forget()
            self.campo_destino.pack_forget()
        self.busca.set("")
        self.atualizar_lista()
        self.aviso.set("Prévia local: mensagens não são enviadas ao servidor.")

    def preparar(self):
        #Prepara o comando sem transmitir mensagens ao servidor.
        origem = self.remetente.get().strip()
        destino = self.destinatario.get().strip() if self.tipo == "privada" else ""
        mensagem = self.entrada.get().strip()
        if not origem.isdigit() or int(origem) <= 0:
            self.aviso.set("Informe um ID de remetente positivo.")
            return
        if self.tipo == "privada" and (not destino.isdigit() or int(destino) <= 0):
            self.aviso.set("Informe um ID de destinatário positivo.")
            return
        if not mensagem:
            self.aviso.set("Digite uma mensagem para preparar o comando.")
            return
        try:
            criar_mensagem(2048, origem, destino, mensagem)
        except (ValueError, TypeError) as erro:
            self.aviso.set(f"Mensagem inválida: {erro}")
            return
        self.aviso.set("Comando ENVIARMENSAGEM (2048) preparado localmente. Nada foi enviado.")
