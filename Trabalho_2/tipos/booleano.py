from tipos.tipo_dado import TipoDado
from erros import ErroIFFARQL

class Booleano(TipoDado):
    def validar(self, valor):
        return isinstance(valor, bool)

    # Impede operações matemáticas com valores BOOLEANO.
    def operar(self, valor_atual, operador, valor_operacao):
        raise ErroIFFARQL(
            "Operações matemáticas não são permitidas para BOOLEANO."
        )