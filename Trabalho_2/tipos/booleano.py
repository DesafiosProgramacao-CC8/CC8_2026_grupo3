from .tipo_dado import TipoDado

class Booleano(TipoDado):
    def validar(self, valor):
        return isinstance(valor, bool)