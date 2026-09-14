from .tipo_dado import TipoDado

class Inteiro(TipoDado):
    def validar(self, valor):
       return isinstance(valor, int) and not isinstance(valor, bool)