import unicodedata

from .tipo_dado import TipoDado

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
