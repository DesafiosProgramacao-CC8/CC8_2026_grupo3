#Tela de notificações preparada para integração com o servidor.
import tkinter as tk
from componentes import BotaoArredondado
from tela_chat import PainelArredondado

CORES = {"fundo": "#FFFAF4", "verde": "#4D563D", "caramelo": "#A67C52",
         "areia": "#F0E8DD", "claro": "#EDE2D2", "texto": "#666057"}


class TelaNotificacoes(tk.Frame):
    def __init__(self, mestre):
        super().__init__(mestre, bg=CORES["fundo"])
        self.filtro = "todas"
        corpo = tk.Frame(self, bg=CORES["fundo"])
        corpo.pack(fill="both", expand=True, padx=18, pady=15)
        lateral = PainelArredondado(corpo, CORES["areia"], width=255)
        lateral.pack(side="left", fill="y", padx=(0, 14))
        lateral.pack_propagate(False)
        tk.Label(lateral.interior, text="Notificações", bg=CORES["areia"],
                 fg=CORES["verde"], font=("Helvetica Neue", 18, "bold")).pack(
                     anchor="w", padx=12, pady=(18, 16))
        linha = tk.Frame(lateral.interior, bg=CORES["areia"])
        linha.pack(fill="x", padx=8)
        self.botoes = {}
        for titulo, chave in (("Todas", "todas"), ("Não lidas", "nao_lidas")):
            botao = BotaoArredondado(linha, titulo, lambda c=chave: self.selecionar(c),
                                    fundo=CORES["areia"], cor=CORES["claro"])
            botao.pack(side="left", fill="x", expand=True, padx=3)
            self.botoes[chave] = botao
        direita = tk.Frame(corpo, bg=CORES["fundo"])
        direita.pack(side="left", fill="both", expand=True)
        cabecalho = PainelArredondado(direita, "#E9DCCB", height=92)
        cabecalho.pack(fill="x", pady=(0, 12))
        cabecalho.pack_propagate(False)
        self.titulo = tk.Label(cabecalho.interior, fg=CORES["verde"], bg="#E9DCCB",
                               font=("Helvetica Neue", 16, "bold"))
        self.titulo.pack(anchor="w", padx=12, pady=(12, 3))
        tk.Label(cabecalho.interior, text="Avisos de mensagens e solicitações",
                 fg=CORES["texto"], bg="#E9DCCB").pack(anchor="w", padx=12)
        painel = PainelArredondado(direita, "#F5EFE7")
        painel.pack(fill="both", expand=True)
        tk.Label(painel.interior, text="Nenhuma notificação carregada.\nAguardando integração com o servidor.",
                 bg="#F5EFE7", fg=CORES["texto"], justify="center",
                 font=("Helvetica Neue", 12)).place(relx=0.5, rely=0.5, anchor="center")
        self.selecionar("todas")

    def selecionar(self, filtro):
        self.filtro = filtro
        for chave, botao in self.botoes.items():
            botao.definir_cor(CORES["caramelo"] if chave == filtro else CORES["claro"])
        self.titulo.configure(text="Todas as notificações" if filtro == "todas" else "Notificações não lidas")
