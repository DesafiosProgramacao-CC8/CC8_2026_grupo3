#Tela de perfil em modo local, sem consulta ou atualização no servidor.
import tkinter as tk
from componentes import BotaoArredondado, CampoArredondado
from telas_acesso import formatar_nascimento

CORES = {"fundo": "#FFFAF4", "verde": "#4D563D", "caramelo": "#A67C52",
         "texto": "#27251F", "secundario": "#666057"}


class TelaPerfil(tk.Frame):
    def __init__(self, mestre):
        super().__init__(mestre, bg=CORES["fundo"])
        self.campos = {}
        self.aviso = tk.StringVar(value="Prévia local: perfil ainda não carregado do servidor.")
        #Centraliza o formulário como no Cadastro, sem cortar o título.
        self.canvas = tk.Canvas(self, bg=CORES["fundo"], highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.area = tk.Frame(self.canvas, bg=CORES["fundo"])
        self.item = self.canvas.create_window(0, 0, window=self.area, anchor="n")
        self.canvas.bind("<Configure>", self.ajustar)
        self.area.bind("<Configure>", self.ajustar)
        quadro = tk.Frame(self.area, bg=CORES["fundo"], padx=22, pady=6)
        quadro.pack(fill="both", expand=True)
        #Linha verde acima do título, no padrão do Cadastro.
        tk.Frame(quadro, bg=CORES["verde"], height=5).pack(fill="x", pady=(0, 12))
        tk.Label(quadro, text="Meu perfil", fg=CORES["verde"], bg=CORES["fundo"],
                 font=("Helvetica Neue", 25, "bold")).pack(pady=(0, 2))
        tk.Label(quadro, text="Visualização e edição dos dados da conta",
                 fg=CORES["secundario"], bg=CORES["fundo"]).pack(pady=(0, 8))
        for titulo, chave in (("Nome completo", "nome"), ("Apelido", "apelido"),
                              ("Data de nascimento", "nascimento"), ("Senha atual", "senha")):
            tk.Label(quadro, text=titulo, fg=CORES["secundario"], bg=CORES["fundo"],
                     anchor="w").pack(fill="x", pady=(4, 2))
            campo = CampoArredondado(quadro, fundo=CORES["fundo"], senha=chave == "senha",
                                     somente_leitura=chave == "apelido")
            campo.pack(fill="x")
            self.campos[chave] = campo.entrada
        tk.Label(quadro, text="O apelido é apenas para consulta e não pode ser alterado.",
                 fg=CORES["secundario"], bg=CORES["fundo"], wraplength=400).pack(pady=(7, 9))
        botao = BotaoArredondado(quadro, "Salvar alterações", self.salvar,
                                fundo=CORES["fundo"], cor=CORES["caramelo"])
        botao.pack(fill="x")
        tk.Label(quadro, textvariable=self.aviso, fg=CORES["secundario"],
                 bg=CORES["fundo"], wraplength=400, justify="center").pack(pady=(8, 0))

    def ajustar(self, _evento=None):
        #Mantém o formulário centralizado e o topo sempre visível.
        largura = max(1, self.canvas.winfo_width())
        altura = self.area.winfo_reqheight()
        self.canvas.itemconfigure(self.item, width=min(480, max(250, largura - 30)))
        self.canvas.coords(self.item, largura / 2, max(12, (self.canvas.winfo_height() - altura) / 2))

    def salvar(self):
        #Não apresenta sucesso falso enquanto não houver autenticação.
        self.aviso.set("A edição do perfil estará disponível após a integração com o servidor.")
