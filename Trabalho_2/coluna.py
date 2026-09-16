class Coluna:
    def __init__(self, nome, tipo, chave_estrangeira=None):
        self.nome = nome
        self.tipo = tipo
        self.chave_estrangeira = chave_estrangeira

    def validar_valor(self, valor):
        return self.tipo.validar(valor)