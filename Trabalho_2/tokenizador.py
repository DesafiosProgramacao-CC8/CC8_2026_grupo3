import math
import re

from erros import ErroIFFARQL
from token import Token


ASPAS = {'"': '"', '“': '”'}
CARACTERES_ASPAS = '"“”'


def tokenizar(comando):
    """Separa o comando em trechos, mantendo as aspas nos valores textuais."""
    if not isinstance(comando, str) or not comando.strip():
        raise ErroIFFARQL("Comando vazio ou inválido.")

    partes = []
    separadores = "(),;=+-*/<>"
    posicao = 0

    while posicao < len(comando):
        caractere = comando[posicao]

        if caractere.isspace():
            posicao += 1
            continue

        if caractere in ASPAS:
            fechamento = ASPAS[caractere]
            inicio = posicao
            posicao += 1

            # Dentro das aspas, espaços e operadores fazem parte do texto.
            while posicao < len(comando) and comando[posicao] != fechamento:
                posicao += 1

            if posicao == len(comando):
                raise ErroIFFARQL("Texto com aspas não fechadas.")

            posicao += 1
            partes.append(comando[inicio:posicao])

            if posicao < len(comando):
                proximo = comando[posicao]
                if not proximo.isspace() and proximo not in separadores:
                    raise ErroIFFARQL("Falta um separador após o texto entre aspas.")
            continue

        if caractere in separadores:
            operador = comando[posicao:posicao + 2]
            if operador in ("<=", ">=", "==", "<>"):
                partes.append(operador)
                posicao += 2
            else:
                partes.append(caractere)
                posicao += 1
            continue

        inicio = posicao
        while posicao < len(comando):
            caractere = comando[posicao]
            if caractere.isspace() or caractere in separadores:
                break
            if caractere in CARACTERES_ASPAS:
                raise ErroIFFARQL("Falta um separador antes do texto entre aspas.")
            posicao += 1

        partes.append(comando[inicio:posicao])

    return partes


def converter_valor(texto):
    """Converte um literal IFFARQL, preservando seu tipo e o uso de aspas."""
    if not isinstance(texto, str):
        raise ErroIFFARQL("O valor recebido deve ser um texto do comando.")

    texto = texto.strip()
    if not texto:
        raise ErroIFFARQL("Valor não informado.")

    if any(aspas in texto for aspas in CARACTERES_ASPAS):
        if len(texto) >= 2 and texto[0] in ASPAS and texto[-1] == ASPAS[texto[0]]:
            valor = texto[1:-1]
            if not any(aspas in valor for aspas in CARACTERES_ASPAS):
                return Token(valor, True)
        raise ErroIFFARQL("Aspas inválidas: use um único par de aspas externas.")

    if texto == "True":
        return Token(True, False)
    if texto == "False":
        return Token(False, False)

    # O formato permite um sinal opcional, seguido de dígitos.
    if re.fullmatch(r"[+-]?[0-9]+", texto):
        try:
            return Token(int(texto), False)
        except ValueError:
            raise ErroIFFARQL("Número inteiro fora do limite de conversão.") from None

    # DECIMAL tem dígitos antes e depois do ponto, como 20.0 ou -0.5.
    if re.fullmatch(r"[+-]?[0-9]+\.[0-9]+", texto):
        valor = float(texto)
        if not math.isfinite(valor):
            raise ErroIFFARQL("Número decimal fora do limite suportado.")
        return Token(valor, False)

    raise ErroIFFARQL(
        f"Valor inválido: '{texto}'. Use texto entre aspas, "
        "INTEIRO, DECIMAL, True ou False."
    )
