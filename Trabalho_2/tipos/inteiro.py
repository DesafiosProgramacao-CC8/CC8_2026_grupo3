from .tipo_dado import TipoDado
from erros import ErroIFFARQL

class Inteiro(TipoDado):
    def validar(self, valor):
       return isinstance(valor, int) and not isinstance(valor, bool)
    
# Executa operações matemáticas entre valores do tipo INTEIRO.

    def operar(self, valor_atual, operador, valor_operacao):
        if not self.validar(valor_operacao):
            raise ErroIFFARQL(
                "Não é permitido operar INTEIRO com outro tipo de dado."
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
            resultado = valor_atual / valor_operacao

            # A operação entre INTEIROS deve continuar resultando em INTEIRO.
            if not resultado.is_integer():
                raise ErroIFFARQL(
                    "A divisão entre INTEIROS deve resultar em um valor INTEIRO."
                )
            return int(resultado)
        raise ErroIFFARQL(
            f"Operador '{operador}' não permitido para INTEIRO."
        )