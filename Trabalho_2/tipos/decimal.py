from .tipo_dado import TipoDado

class Decimal(TipoDado):
    def validar(self, valor):
        return isinstance(valor, float)