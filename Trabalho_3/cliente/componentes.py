#Componentes visuais compartilhados pelas telas do IFFARCHAT.
import tkinter as tk


def retangulo_arredondado(canvas, x1, y1, x2, y2, raio, **opcoes):
    raio = max(0, min(raio, (x2-x1)/2, (y2-y1)/2))
    pontos = [x1+raio,y1, x2-raio,y1, x2,y1, x2,y1+raio,
              x2,y2-raio, x2,y2, x2-raio,y2, x1+raio,y2,
              x1,y2, x1,y2-raio, x1,y1+raio, x1,y1]
    return canvas.create_polygon(pontos, smooth=True, splinesteps=20, **opcoes)


class BotaoArredondado(tk.Canvas):
    #Botão de cor consistente no macOS, inclusive com navegação por teclado.
    def __init__(self, pai, texto, comando, cor="#A67C52", hover="#8C6C55",
                 fundo="#FFFAF4", altura=42, **opcoes):
        super().__init__(pai, height=altura, bg=fundo, bd=0,
                         highlightthickness=0, takefocus=1, cursor="hand2", **opcoes)
        self.texto, self.comando = texto, comando
        self.cor, self.hover, self.fundo = cor, hover, fundo
        self.habilitado = True
        self._sobre = False
        self.bind("<Configure>", lambda _: self.desenhar())
        self.bind("<Button-1>", self.acionar)
        self.bind("<Return>", self.acionar)
        self.bind("<space>", self.acionar)
        self.bind("<Enter>", lambda _: self._hover(True))
        self.bind("<Leave>", lambda _: self._hover(False))

    def _hover(self, sobre):
        self._sobre = sobre
        self.desenhar()

    def acionar(self, _evento=None):
        if self.habilitado:
            self.comando()

    def desenhar(self):
        largura, altura = self.winfo_width(), self.winfo_height()
        if largura < 3 or altura < 3:
            return
        self.delete("all")
        cor = (self.hover if self._sobre else self.cor) if self.habilitado else "#DDD4C8"
        retangulo_arredondado(self, 1, 1, largura-1, altura-1, 12, fill=cor, outline="")
        self.create_text(largura/2, altura/2, text=self.texto,
                         fill=("#4D563D" if self.cor == "#E8DDCB" else "#FFFFFF") if self.habilitado else "#666057",
                         font=("Helvetica Neue", 11, "bold"))
        self.configure(cursor="hand2" if self.habilitado else "arrow")

    def definir_cor(self, cor):
        #Atualiza a cor do botão desenhado no Canvas.
        self.cor = cor
        self.desenhar()


class CampoArredondado(tk.Frame):
    #Campo de texto com margem interna, borda suave e cantos arredondados.
    def __init__(self, pai, variavel=None, largura=None, senha=False,
                 fundo="#FFFAF4", placeholder=None, prefixo=None, **opcoes):
        super().__init__(pai, bg=fundo)
        self.prefixo = prefixo
        self.canvas = tk.Canvas(self, height=42, bg=fundo, bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.entrada = tk.Entry(self.canvas, textvariable=variavel, show="•" if senha else "",
                                bg="#FFFFFF", fg="#27251F", relief="flat", bd=0,
                                insertbackground="#27251F", highlightthickness=0, font=("Helvetica Neue", 11), **opcoes)
        self.item = self.canvas.create_window(42 if prefixo else 14, 9, anchor="nw", window=self.entrada)
        self.canvas.bind("<Configure>", self._redesenhar)
        if largura:
            self.configure(width=largura)
        if placeholder:
            self.entrada.insert(0, placeholder)

    def _redesenhar(self, evento):
        self.canvas.delete("borda")
        retangulo_arredondado(self.canvas, 1, 1, evento.width-1, evento.height-1, 11,
                             fill="#FFFFFF", outline="#DDD4C8", width=1, tags="borda")
        self.canvas.tag_lower("borda")
        self.canvas.delete("icone")
        if self.prefixo:
            self.canvas.create_text(22, evento.height / 2, text=self.prefixo,
                                    font=("Helvetica Neue", 12), tags="icone")
        self.canvas.itemconfigure(self.item, width=max(1, evento.width-(56 if self.prefixo else 28)),
                                  height=max(1, evento.height-18))

    def get(self):
        return self.entrada.get()
