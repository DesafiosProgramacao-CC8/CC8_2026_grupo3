from tipos.tipo_dado import TipoDado
from erros import ErroIFFARQL

class Decimal(TipoDado):

    def validar(self, valor):
        return isinstance(valor, float)

    # Executa operações matemáticas entre valores do tipo DECIMAL.
    def operar(self, valor_atual, operador, valor_operacao):
        if not self.validar(valor_operacao):
            raise ErroIFFARQL(
                "Não é permitido operar DECIMAL com outro tipo de dado."
            )
        if operador == "+":
            return valor_atual + valor_operacao
        if operador == "-":
            return valor_atual - valor_operacao
        if operador == "*":
            return valor_atual * valor_operacao
        if operador == "/":
            if valor_operacao == 0:
                raise ErroIFFARQL(
                    "Divisão por zero não é permitida."
                )
            return valor_atual / valor_operacao
        raise ErroIFFARQL(
            f"Operador '{operador}' não permitido para DECIMAL."
        )