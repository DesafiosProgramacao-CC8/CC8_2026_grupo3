class Registro:
    def __init__(self, id, valores):
        self.id = id
        self.valores = {"id": id}

        self.valores.update(valores)

    def obter_valores(self, coluna):
        return self.valores[coluna]