#Interface do chat geral e privado, em modo de prévia local.
import tkinter as tk
import threading
from conexao import ErroConexao
from protocolo_cliente import criar_mensagem
from componentes import BotaoArredondado, CampoArredondado

CORES = {"fundo": "#F3EFE8", "painel": "#FFFAF4", "verde": "#4D563D",
         "caramelo": "#A67C52", "hover": "#8C6C55", "borda": "#DDD4C8",
         "texto": "#27251F", "secundario": "#666057", "branco": "#FFFFFF",
         "areia": "#F0E8DD", "selecao": "#E8DDCB", "cabecalho": "#E9DCCB"}


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
    def __init__(self, mestre, voltar, aplicacao=None):
        super().__init__(mestre, bg=CORES["painel"])
        self.voltar = voltar
        self.aplicacao = aplicacao
        self.ativo = False
        self.consultando = False
        self.historico_carregado = set()
        self._consulta_agendada = False
        self.tipo = "geral"
        self.remetente = tk.StringVar()
        self.destinatario = tk.StringVar()
        self.busca = tk.StringVar()
        self.aviso = tk.StringVar(value="")
        self.enviando = False
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
                                       fundo=CORES["areia"], prefixo="⌕")
        campo_busca.pack(fill="x", expand=True)
        self.campo_busca = campo_busca.entrada
        self._busca_placeholder = "Buscar conversa..."
        self._busca_placeholder_ativo = False
        self.campo_busca.bind("<FocusIn>", self._limpar_busca_placeholder)
        self.campo_busca.bind("<FocusOut>", self._restaurar_busca_placeholder)
        self._restaurar_busca_placeholder()
        self.busca.trace_add("write", lambda *_: self.atualizar_lista())
        #Mensagem discreta apenas quando a pesquisa não encontra conversas.
        self.aviso_busca = tk.Label(lateral, text="", bg=CORES["areia"],
                                    fg=CORES["secundario"], font=("Helvetica Neue", 10))
        self.aviso_busca.pack(fill="x", padx=10)

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
        painel_mensagens = PainelArredondado(principal, "#F5EFE7", margem=14)
        painel_mensagens.pack(fill="both", expand=True)
        self.area_mensagens = tk.Text(
            painel_mensagens.interior, bg="#F5EFE7", fg=CORES["texto"],
            relief="flat", bd=0, highlightthickness=0, wrap="word",
            font=("Helvetica Neue", 11), padx=12, pady=12,
            insertbackground=CORES["texto"]
        )
        self.area_mensagens.pack(fill="both", expand=True)
        self.area_mensagens.insert("end", "")
        self.area_mensagens.configure(state="disabled")

        rodape = tk.Frame(principal, bg=CORES["painel"], pady=10)
        rodape.pack(fill="x")
        ids = tk.Frame(rodape, bg=CORES["painel"])
        ids.pack(fill="x", pady=(0, 8))
        tk.Label(ids, text="Meu ID:", bg=CORES["painel"], fg=CORES["secundario"]).pack(side="left")
        campo_id = CampoArredondado(ids, variavel=self.remetente, fundo=CORES["painel"])
        campo_id.pack(side="left", padx=(8, 15), ipadx=0)
        campo_id.configure(width=150)
        self._configurar_placeholder(campo_id.entrada, "Digite seu ID...")
        self.label_destino = tk.Label(ids, text="ID destinatário:", bg=CORES["painel"], fg=CORES["secundario"])
        self.campo_destino = CampoArredondado(ids, variavel=self.destinatario,
                                               fundo=CORES["painel"])
        self.campo_destino.configure(width=190)
        self._configurar_placeholder(self.campo_destino.entrada, "Digite o ID do destinatário...")
        linha = tk.Frame(rodape, bg=CORES["painel"])
        linha.pack(fill="x")
        campo_mensagem = CampoArredondado(linha, fundo=CORES["painel"])
        campo_mensagem.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entrada = campo_mensagem.entrada
        #Envia a mensagem com Enter.
        self.entrada.bind("<Return>", lambda evento: (self.preparar(), "break")[1])
        #Placeholder da mensagem sem alterar o conteúdo enviado.
        self._placeholder = "Digite sua mensagem..."
        self._placeholder_ativo = False
        self.entrada.bind("<FocusIn>", self._limpar_placeholder)
        self.entrada.bind("<FocusOut>", self._restaurar_placeholder)
        self._restaurar_placeholder()
        self.botao(linha, "Enviar", self.preparar).pack(side="right", padx=(0, 2))
        tk.Label(self, textvariable=self.aviso, bg=CORES["painel"], fg=CORES["secundario"],
                 font=("Helvetica Neue", 10), wraplength=650).pack(pady=(0, 8))
        self.selecionar("geral")

    def _limpar_busca_placeholder(self, _evento=None):
        #Remove o texto de orientação ao iniciar a busca.
        if self._busca_placeholder_ativo:
            self._busca_placeholder_ativo = False
            self.busca.set("")
            self.campo_busca.configure(fg=CORES["texto"])

    def _restaurar_busca_placeholder(self, _evento=None):
        #Restaura a dica quando o campo estiver vazio.
        if not self.busca.get().strip():
            self._busca_placeholder_ativo = True
            self.busca.set(self._busca_placeholder)
            self.campo_busca.configure(fg="#8B857C")

    def atualizar_lista(self):
        #Não exibe cartão de conversa; informa somente buscas sem correspondência.
        nome = "Conversa geral" if self.tipo == "geral" else "Conversa privada"
        termo = "" if self._busca_placeholder_ativo else self.busca.get().strip().lower()
        self.aviso_busca.configure(text="Nenhuma conversa encontrada." if termo and termo not in nome.lower() else "")

    def selecionar(self, tipo):
        #Atualiza as abas sem recriar a janela.
        self.tipo = tipo
        for item, selecionado in ((self.aba_geral, tipo == "geral"), (self.aba_privada, tipo == "privada")):
            item.definir_cor(CORES["caramelo"] if selecionado else CORES["selecao"])
        self.area_mensagens.configure(state="normal")
        self.area_mensagens.delete("1.0", "end")
        self.area_mensagens.insert("end", "")
        self.area_mensagens.configure(state="disabled")
        self.titulo.configure(text="Conversa geral" if tipo == "geral" else "Conversa privada")
        self.subtitulo.configure(text="Todos os usuários" if tipo == "geral" else "Conversa individual")
        if tipo == "privada":
            self.label_destino.pack(side="left")
            self.campo_destino.pack(side="left", padx=8)
        else:
            self.label_destino.pack_forget()
            self.campo_destino.pack_forget()
        self.busca.set("")
        self._restaurar_busca_placeholder()
        self.atualizar_lista()
        self.aviso.set("")
        if self.ativo:
            self.iniciar_consulta()

    def _configurar_placeholder(self, entrada, texto):
        #Mostra uma dica sem incluir o texto no comando enviado.
        def entrar(_evento=None):
            if entrada.get() == texto:
                entrada.delete(0, "end")
                entrada.configure(fg=CORES["texto"])

        def sair(_evento=None):
            if not entrada.get().strip():
                entrada.delete(0, "end")
                entrada.insert(0, texto)
                entrada.configure(fg="#8B857C")

        entrada.bind("<FocusIn>", entrar, add="+")
        entrada.bind("<FocusOut>", sair, add="+")
        sair()

    def _limpar_placeholder(self, _evento=None):
        if self._placeholder_ativo:
            self.entrada.delete(0, "end")
            self.entrada.configure(fg=CORES["texto"])
            self._placeholder_ativo = False

    def _restaurar_placeholder(self, _evento=None):
        if not self.entrada.get().strip():
            self.entrada.delete(0, "end")
            self.entrada.insert(0, self._placeholder)
            self.entrada.configure(fg="#8B857C")
            self._placeholder_ativo = True

    def preparar(self):
        if self.enviando:
            return
        #Prepara o comando sem transmitir mensagens ao servidor.
        origem = self.remetente.get().strip()
        if origem == "Digite seu ID...":
            origem = ""
        destino = self.destinatario.get().strip() if self.tipo == "privada" else ""
        if destino == "Digite o ID do destinatário...":
            destino = ""
        mensagem = "" if self._placeholder_ativo else self.entrada.get().strip()
        if not self.aplicacao or not self.aplicacao.conexao.id_usuario:
            self.aviso.set("Faça login antes de enviar mensagens.")
            return
        origem = str(self.aplicacao.conexao.id_usuario)
        if self.tipo == "privada" and (not destino.isdigit() or int(destino) <= 0):
            self.aviso.set("Informe um ID de destinatário positivo.")
            return
        if not mensagem:
            self.aviso.set("Digite uma mensagem antes de enviar.")
            return
        try:
            criar_mensagem(2048, origem, destino, mensagem)
        except (ValueError, TypeError) as erro:
            self.aviso.set(f"Mensagem inválida: {erro}")
            return
        self.enviar(destino, mensagem)

    def executar_rede(self, tarefa, concluir):
        #Executa as requisicoes sem bloquear a interface.
        def trabalho():
            try:
                resposta, erro = tarefa(), None
            except (ErroConexao, OSError, ValueError) as falha:
                resposta, erro = None, str(falha)
            try:
                self.after(0, lambda: concluir(resposta, erro))
            except RuntimeError:
                pass
        threading.Thread(target=trabalho, daemon=True).start()

    def enviar(self, destino, mensagem):
        self.enviando = True
        app = self.aplicacao
        usuario = app.conexao.id_usuario
        def tarefa():
            codigo, _ = app.conexao.requisitar(2048, usuario, destino, mensagem)
            if codigo != 2049:
                raise ErroConexao("O servidor não confirmou o envio.")
        def concluir(_, erro):
            self.enviando = False
            if erro:
                self.aviso.set("Falha no envio: " + erro)
                return
            self.entrada.delete(0, "end")
            self._restaurar_placeholder()
            self.aviso.set("Mensagem enviada.")
            self.consultar()
        self.executar_rede(tarefa, concluir)

    def mostrar_mensagens(self, campos, historico=False):
        #Exibe as mensagens na ordem definida pelo protocolo.
        if not campos:
            return
        self.area_mensagens.configure(state="normal")
        if not self.area_mensagens.get("1.0", "end").strip():
            self.area_mensagens.delete("1.0", "end")
        for indice in range(0, len(campos), 5):
            grupo = campos[indice:indice + 5]
            if historico:
                remetente, data, hora, minuto, texto = grupo
            else:
                remetente, texto, data, hora, minuto = grupo
            self.area_mensagens.insert("end", f"[{data} {hora.zfill(2)}:{minuto.zfill(2)}] {remetente}: {texto}\n")
        self.area_mensagens.see("end")
        self.area_mensagens.configure(state="disabled")

    def iniciar_consulta(self):
        if not self.ativo or not self.aplicacao.conexao.id_usuario:
            return
        self.remetente.set(str(self.aplicacao.conexao.id_usuario))
        if not self.consultando and not self._consulta_agendada:
            self.consultar()

    def consultar(self):
        if not self.ativo or self.consultando or not self.aplicacao.conexao.id_usuario:
            return
        destino = self.destinatario.get().strip() if self.tipo == "privada" else ""
        if destino == "Digite o ID do destinatário...":
            destino = ""
        if self.tipo == "privada" and (not destino.isdigit() or int(destino) <= 0):
            self.agendar_consulta()
            return
        self.consultando = True
        app = self.aplicacao
        usuario = app.conexao.id_usuario
        chave = (usuario, destino)
        historico = bool(destino and chave not in self.historico_carregado)
        def tarefa():
            codigo, campos = app.conexao.requisitar(4096 if historico else 1024, usuario, destino)
            if codigo != (4097 if historico else 1025):
                raise ErroConexao("Resposta inesperada ao consultar mensagens.")
            return campos
        def concluir(campos, erro):
            self.consultando = False
            if erro:
                self.aviso.set("Falha na consulta: " + erro)
            elif usuario == app.conexao.id_usuario and self.ativo:
                atual = self.destinatario.get().strip() if self.tipo == "privada" else ""
                if atual == "Digite o ID do destinatário...":
                    atual = ""
                if atual == destino:
                    if historico:
                        self.historico_carregado.add(chave)
                    self.mostrar_mensagens(campos, historico)
            self.agendar_consulta()
        self.executar_rede(tarefa, concluir)

    def agendar_consulta(self):
        if not self.ativo or self._consulta_agendada:
            return
        self._consulta_agendada = True
        def repetir():
            self._consulta_agendada = False
            self.iniciar_consulta()
        self.after(3000, repetir)
