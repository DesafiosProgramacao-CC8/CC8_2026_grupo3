class Token:

    def __init__(self, valor, com_aspas=False):
        self.valor = valor
        self.com_aspas = com_aspas

    def obter_valor(self):
        return self.valor

    def possui_aspas(self):
        return self.com_aspas

    def __str__(self):
        return str(self.valor)