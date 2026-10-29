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
                 fundo="#FFFAF4", altura=42, cor_texto=None, **opcoes):
        #Evita a largura padrão do Canvas, que escondia botões vizinhos.
        opcoes.setdefault("width", 80)
        super().__init__(pai, height=altura, bg=fundo, bd=0,
                         highlightthickness=0, takefocus=1, cursor="hand2", **opcoes)
        self.texto, self.comando = texto, comando
        self.cor_texto = cor_texto
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
        self.create_text(largura/2, altura/2, text=self.texto, anchor="center",
                         fill=self._cor_do_texto(), font=("Helvetica Neue", 11, "bold"),
                         tags="texto")
        self.tag_raise("texto")
        self.configure(cursor="hand2" if self.habilitado else "arrow")

    def _cor_do_texto(self):
        #Escolhe o texto pelo brilho do fundo do botão.
        if not self.habilitado:
            return "#666057"
        if self.cor_texto:
            return self.cor_texto
        try:
            r, g, b = (valor / 257 for valor in self.winfo_rgb(self.cor))
        except tk.TclError:
            return "#FFFFFF"
        return "#4D563D" if (0.299*r + 0.587*g + 0.114*b) > 170 else "#FFFFFF"

    def definir_cor(self, cor):
        #Atualiza a cor do botão desenhado no Canvas.
        self.cor = cor
        self.desenhar()


class CampoArredondado(tk.Frame):
    #Campo de texto com margem interna, borda suave e cantos arredondados.
    def __init__(self, pai, variavel=None, largura=None, senha=False,
                 fundo="#FFFAF4", placeholder=None, prefixo=None,
                 somente_leitura=False, **opcoes):
        super().__init__(pai, bg=fundo)
        self.prefixo = prefixo
        self.somente_leitura = somente_leitura
        self.cor_campo = "#F5EFE7" if somente_leitura else "#FFFFFF"
        self.canvas = tk.Canvas(self, height=42, bg=fundo, bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.entrada = tk.Entry(self.canvas, textvariable=variavel, show="•" if senha else "",
                                bg=self.cor_campo, fg="#27251F", relief="flat", bd=0,
                                insertbackground="#27251F", highlightthickness=0, font=("Helvetica Neue", 11), **opcoes)
        self.item = self.canvas.create_window(42 if prefixo else 14, 9, anchor="nw", window=self.entrada)
        self.canvas.bind("<Configure>", self._redesenhar)
        if largura:
            self.configure(width=largura)
        if placeholder:
            self.entrada.insert(0, placeholder)
        if somente_leitura:
            self._bloquear_edicao()

    def _bloquear_edicao(self):
        #Bloqueia a digitação sem usar state, que gera tarja escura no macOS.
        self.entrada.configure(insertwidth=0, takefocus=0, cursor="arrow")
        permitidas = ("Tab", "ISO_Left_Tab", "Left", "Right", "Home", "End")
        self.entrada.bind("<Key>", lambda evento: None if evento.keysym in permitidas else "break")
        for evento in ("<<Paste>>", "<<Cut>>", "<<Clear>>", "<<PasteSelection>>"):
            self.entrada.bind(evento, lambda _evento: "break")

    def definir_texto(self, texto):
        #Preenche o campo, inclusive quando for somente leitura.
        self.entrada.delete(0, "end")
        self.entrada.insert(0, texto)

    def _redesenhar(self, evento):
        self.canvas.delete("borda")
        retangulo_arredondado(self.canvas, 1, 1, evento.width-1, evento.height-1, 11,
                             fill=self.cor_campo, outline="#DDD4C8", width=1, tags="borda")
        self.canvas.tag_lower("borda")
        self.canvas.delete("icone")
        if self.prefixo == "⌕":
            self._desenhar_lupa(22, evento.height / 2)
        elif self.prefixo:
            self.canvas.create_text(22, evento.height / 2, text=self.prefixo, fill="#666057",
                                    font=("Helvetica Neue", 12), tags="icone")
        self.canvas.itemconfigure(self.item, width=max(1, evento.width-(56 if self.prefixo else 28)),
                                  height=max(1, evento.height-18))

    def _desenhar_lupa(self, x, y):
        #Desenha a lupa com formas, sem depender da fonte do sistema.
        self.canvas.create_oval(x-6, y-6, x+3, y+3, outline="#666057", width=2, tags="icone")
        self.canvas.create_line(x+2, y+2, x+7, y+7, fill="#666057", width=2,
                                capstyle="round", tags="icone")

    def get(self):
        return self.entrada.get()
