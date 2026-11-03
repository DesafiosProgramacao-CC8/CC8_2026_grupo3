#Tela de notificações do IFFARCHAT.
import tkinter as tk
import threading
from conexao import ErroConexao
from componentes import BotaoArredondado
from tela_chat import PainelArredondado

CORES = {"fundo": "#FFFAF4", "verde": "#4D563D", "caramelo": "#A67C52",
         "areia": "#F0E8DD", "claro": "#EDE2D2", "texto": "#666057"}


class TelaNotificacoes(tk.Frame):
    def __init__(self, mestre, aplicacao=None, abrir_solicitacoes=None):
        super().__init__(mestre, bg=CORES["fundo"])
        self.aplicacao = aplicacao
        self.abrir_solicitacoes = abrir_solicitacoes
        self.ativo = False
        self.consultando = False
        self.agendado = False
        self.avisos = {}
        self.lidas = set()
        self.filtro = "todas"

        corpo = tk.Frame(self, bg=CORES["fundo"])
        corpo.pack(fill="both", expand=True, padx=18, pady=15)

        lateral = PainelArredondado(corpo, CORES["areia"], width=255)
        lateral.pack(side="left", fill="y", padx=(0, 14))
        lateral.pack_propagate(False)

        tk.Label(
            lateral.interior,
            text="Notificações",
            bg=CORES["areia"],
            fg=CORES["verde"],
            font=("Helvetica Neue", 18, "bold")
        ).pack(anchor="w", padx=12, pady=(18, 16))

        linha = tk.Frame(lateral.interior, bg=CORES["areia"])
        linha.pack(fill="x", padx=8)

        self.botoes = {}

        for titulo, chave in (("Todas", "todas"), ("Não lidas", "nao_lidas")):
            botao = BotaoArredondado(
                linha,
                titulo,
                lambda c=chave: self.selecionar(c),
                fundo=CORES["areia"],
                cor=CORES["claro"]
            )
            botao.pack(side="left", fill="x", expand=True, padx=3)
            self.botoes[chave] = botao

        direita = tk.Frame(corpo, bg=CORES["fundo"])
        direita.pack(side="left", fill="both", expand=True)

        cabecalho = PainelArredondado(direita, "#E9DCCB", height=92)
        cabecalho.pack(fill="x", pady=(0, 12))
        cabecalho.pack_propagate(False)

        self.titulo = tk.Label(
            cabecalho.interior,
            fg=CORES["verde"],
            bg="#E9DCCB",
            font=("Helvetica Neue", 16, "bold")
        )
        self.titulo.pack(anchor="w", padx=12, pady=(12, 3))

        tk.Label(
            cabecalho.interior,
            text="Avisos de mensagens e solicitações",
            fg=CORES["texto"],
            bg="#E9DCCB"
        ).pack(anchor="w", padx=12)

        painel = PainelArredondado(direita, "#F5EFE7")
        painel.pack(fill="both", expand=True)

        self.lista = tk.Frame(painel.interior, bg="#F5EFE7")
        self.lista.pack(fill="both", expand=True, padx=12, pady=12)

        self.selecionar("todas")

    def selecionar(self, filtro):
        self.filtro = filtro

        if filtro == "todas":
            self.lidas.update(self.avisos)

        for chave, botao in self.botoes.items():
            botao.definir_cor(
                CORES["caramelo"] if chave == filtro else CORES["claro"]
            )

        self.titulo.configure(
            text="Todas as notificações"
            if filtro == "todas"
            else "Notificações não lidas"
        )

        self.atualizar()

    def iniciar_consulta(self):
        if not self.ativo or self.agendado:
            return

        self.agendado = True
        self.consultar()
        self.after(3000, self._repetir)

    def _repetir(self):
        self.agendado = False

        if self.ativo:
            self.iniciar_consulta()

    def consultar(self):
        if (
            self.consultando
            or not self.aplicacao
            or not self.aplicacao.conexao.id_usuario
        ):
            return

        self.consultando = True
        uid = self.aplicacao.conexao.id_usuario

        def trabalho():
            try:
                codigo, campos = self.aplicacao.conexao.requisitar(128, uid)

                if codigo != 129:
                    raise ErroConexao(
                        f"Resposta inesperada de notificações: {codigo}"
                    )

                avisos = self.aplicacao.conexao.retirar_avisos()

                self.after(
                    0,
                    lambda: self.receber(campos, avisos)
                )

            except (ErroConexao, OSError) as erro:
                self.after(
                    0,
                    lambda msg=str(erro): self.erro(msg)
                )

        threading.Thread(target=trabalho, daemon=True).start()

    def receber(self, ids, avisos):
        self.consultando = False

        #Registra os remetentes de mensagens privadas não lidas.
        atuais = {
            f"msg:{uid}": f"Mensagem privada de usuário {uid}"
            for uid in ids
        }

        self.avisos.update(atuais)

        #Registra os avisos recebidos do servidor.
        for codigo, campos in avisos:
            if codigo == 257 and campos:
                self.avisos[f"amizade:{campos[0]}"] = (
                    f"Solicitação de amizade de usuário {campos[0]}"
                )

            elif codigo == 259 and len(campos) >= 2:
                estado = (
                    "aceita"
                    if campos[1] == "VERDADEIRO"
                    else "recusada"
                )

                self.avisos[f"resposta:{campos[0]}"] = (
                    f"Amizade com usuário {campos[0]} {estado}"
                )

        #Mantem os avisos de amizade durante a sessao.
        amigos = getattr(self.aplicacao, "tela_amizades", None)

        if amigos is not None:
            for usuario, nome in amigos.pedidos.items():
                self.avisos[f"amizade:{usuario}"] = (
                    f"Solicitação de amizade de {nome}"
                )

        if self.filtro == "todas":
            self.lidas.update(self.avisos)

        self.aviso_erro = None
        self.atualizar()

    def erro(self, mensagem):
        self.consultando = False
        self.aviso_erro = mensagem
        self.atualizar()

    def atualizar(self):
        #Limpa os elementos visuais antes de atualizar a lista.
        for filho in self.lista.winfo_children():
            filho.destroy()

        itens = [
            (chave, texto)
            for chave, texto in self.avisos.items()
            if self.filtro == "todas" or chave not in self.lidas
        ]

        if not itens:
            texto = (
                getattr(self, "aviso_erro", None)
                or "Nenhuma notificação disponível."
            )

            tk.Label(
                self.lista,
                text=texto,
                bg="#F5EFE7",
                fg=CORES["texto"]
            ).pack(pady=20)

            return

        #Exibe cada notificacao com a acao alinhada a direita.
        for chave, aviso in itens:
            linha = tk.Frame(self.lista, bg="#F5EFE7")
            linha.pack(fill="x", pady=7)

            if chave.startswith("amizade:") and self.abrir_solicitacoes:
                botao = BotaoArredondado(
                    linha,
                    "Ver solicitação",
                    self.abrir_solicitacoes,
                    cor=CORES["caramelo"],
                    fundo="#F5EFE7",
                    width=140
                )

                botao.pack(side="right", padx=(12, 4))

            tk.Label(
                linha,
                text=aviso,
                anchor="w",
                bg="#F5EFE7",
                fg=CORES["verde"],
                wraplength=380
            ).pack(side="left", fill="x", expand=True, padx=(0, 14))