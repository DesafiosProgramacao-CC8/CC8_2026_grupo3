import unicodedata

from .tipo_dado import TipoDado
from erros import ErroIFFARQL

class Texto(TipoDado):
    def validar(self, valor):
        return isinstance(valor, str) 

    def remover_acentos(self, texto):
        texto_normalizado = unicodedata.normalize("NFD", texto)
        texto_sem_acentos = ""

        for caractere in texto_normalizado:
            if unicodedata.category(caractere) != "Mn":
                texto_sem_acentos += caractere
        return texto_sem_acentos

# Concatena dois valores TEXTO utilizando o operador de soma.
    def operar(self, valor_atual, operador, valor_operacao):
        if not self.validar(valor_operacao):
            raise ErroIFFARQL(
                "Não é permitido operar TEXTO com outro tipo de dado."
            )
        if operador == "+":
            return valor_atual + valor_operacao
        raise ErroIFFARQL(
            f"Operador '{operador}' não permitido para TEXTO."
        )