"""Primeira janela gráfica do IFFARCHAT (commit 01)."""
import tkinter as tk

CORES = {'bg': '#F5F1EB', 'card': '#FFFAF5', 'side': '#4D563D', 'border': '#DDD4C8', 'accent': '#4D563D', 'button': '#A67C52', 'hover': '#8C6C55', 'sage': '#929681', 'olive': '#4D563D', 'text': '#26241E', 'muted': '#77736D', 'dim': '#A9A59B'}

class JanelaIFFARChat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IFFARCHAT | Cliente")
        self.geometry("720x460")
        self.minsize(520, 360)
        self.configure(bg=CORES["bg"])

        painel = tk.Frame(self, bg=CORES["card"], highlightbackground=CORES["border"], highlightthickness=1)
        painel.pack(fill="both", expand=True, padx=34, pady=34)
        tk.Frame(painel, bg=CORES["sage"], height=5).pack(fill="x")
        centro = tk.Frame(painel, bg=CORES["card"])
        centro.pack(expand=True)
        tk.Label(centro, text="IFFARCHAT", bg=CORES["card"], fg=CORES["text"],
                 font=("Helvetica Neue", 32, "bold")).pack(pady=(0, 10))
        tk.Label(centro, text="APLICAÇÃO CLIENTE  •  TRABALHO INTEGRADOR III",
                 bg=CORES["card"], fg=CORES["accent"], font=("Helvetica Neue", 10, "bold")).pack()
        tk.Frame(centro, bg=CORES["border"], height=1, width=330).pack(pady=28)
        tk.Label(centro, text="Interface inicial pronta", bg=CORES["card"], fg=CORES["text"],
                 font=("Helvetica Neue", 15, "bold")).pack(pady=(0, 8))
        tk.Label(centro, text="A conexão TCP será adicionada no próximo commit.",
                 bg=CORES["card"], fg=CORES["muted"], font=("Helvetica Neue", 11)).pack()
