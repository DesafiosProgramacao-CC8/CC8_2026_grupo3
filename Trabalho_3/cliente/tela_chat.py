#Prévia da tela principal do IFFARCHAT

import tkinter as tk

CORES = {"fundo": "#F3EFE8", "painel": "#FFFAF4", "verde": "#4D563D",
         "caramelo": "#A67C52", "borda": "#DDD4C8", "texto": "#27251F",
         "secundario": "#666057", "branco": "#FFFFFF"}

class TelaChat(tk.Frame):
    def __init__(self, mestre, voltar):
        super().__init__(mestre, bg=CORES["painel"])
        self.voltar = voltar
        self.cabecalho = tk.Frame(self, bg=CORES["painel"], padx=24, pady=15)
        self.cabecalho.pack(fill="x")
        tk.Label(self.cabecalho, text="IFFARCHAT", bg=CORES["painel"],
                 fg=CORES["verde"], font=("Helvetica Neue", 22, "bold")).pack(side="left")
        voltar_btn = tk.Label(self.cabecalho, text="Voltar à conexão",
                              bg=CORES["caramelo"], fg=CORES["branco"],
                              font=("Helvetica Neue", 11, "bold"),
                              padx=14, pady=10, cursor="hand2", takefocus=1)
        voltar_btn.pack(side="right")
        voltar_btn.bind("<Button-1>", lambda _e: self.voltar())
        voltar_btn.bind("<Return>", lambda _e: self.voltar())
        voltar_btn.bind("<space>", lambda _e: self.voltar())
        voltar_btn.bind("<Enter>", lambda _e: voltar_btn.configure(bg="#8C6C55"))
        voltar_btn.bind("<Leave>", lambda _e: voltar_btn.configure(bg=CORES["caramelo"]))
        tk.Frame(self, bg=CORES["borda"], height=1).pack(fill="x")
        corpo = tk.Frame(self, bg=CORES["painel"])
        corpo.pack(fill="both", expand=True, padx=18, pady=18)
        lateral = tk.Frame(corpo, bg=CORES["fundo"], width=205,
                           highlightbackground=CORES["borda"], highlightthickness=1)
        lateral.pack(side="left", fill="y", padx=(0, 12))
        lateral.pack_propagate(False)
        tk.Label(lateral, text="Conversas", bg=CORES["fundo"], fg=CORES["verde"],
                 font=("Helvetica Neue", 15, "bold")).pack(anchor="w", padx=16, pady=(18, 12))
        tk.Label(lateral, text="Nenhuma conversa disponível.", bg=CORES["fundo"],
                 fg=CORES["secundario"], wraplength=170, justify="left").pack(anchor="w", padx=16)
        principal = tk.Frame(corpo, bg=CORES["branco"],
                             highlightbackground=CORES["borda"], highlightthickness=1)
        principal.pack(side="left", fill="both", expand=True)
        tk.Label(principal, text="Conversa geral", bg=CORES["branco"], fg=CORES["verde"],
                 font=("Helvetica Neue", 15, "bold")).pack(anchor="w", padx=20, pady=18)
        tk.Frame(principal, bg=CORES["borda"], height=1).pack(fill="x")
        tk.Label(principal, text="As mensagens aparecerão aqui após a integração.",
                 bg=CORES["branco"], fg=CORES["secundario"], wraplength=340,
                 justify="center").pack(fill="both", expand=True, padx=20)
        rodape = tk.Frame(principal, bg=CORES["branco"], padx=16, pady=14)
        rodape.pack(fill="x")
        self.entrada = tk.Entry(rodape, state="disabled", disabledbackground=CORES["fundo"],
                                relief="flat", font=("Helvetica Neue", 11))
        self.entrada.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        # Prévia: o envio ainda não está integrado, portanto não há ação de clique.
        tk.Label(rodape, text="Enviar", bg=CORES["caramelo"],
                 fg=CORES["branco"], font=("Helvetica Neue", 11, "bold"),
                 padx=18, pady=10).pack(side="right")
        tk.Label(self, text="Prévia da interface: envio e recebimento serão integrados posteriormente.",
                 bg=CORES["painel"], fg=CORES["secundario"],
                 font=("Helvetica Neue", 10)).pack(pady=(0, 10))